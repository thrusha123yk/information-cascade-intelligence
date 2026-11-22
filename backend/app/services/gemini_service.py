import asyncio
import logging
from google import genai
from google.genai import types
import httpx
from ..config import GOOGLE_API_KEY, GEMINI_MODEL_ID

logger = logging.getLogger(__name__)

async def generate_response(prompt: str) -> str:
    if not GOOGLE_API_KEY:
        return "AI Research Analyst is unavailable because GOOGLE_API_KEY is not configured on the backend."

    try:
        client = genai.Client(
            api_key=GOOGLE_API_KEY,
            http_options=types.HttpOptions(
                timeout=25000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        response = await asyncio.to_thread(
            client.interactions.create,
            model=GEMINI_MODEL_ID,
            input=prompt,
            generation_config={
                "max_output_tokens": 200,
                "thinking_level": "minimal",
            },
            store=False,
            timeout=25,
            automatic_continuation=False,
        )
        return (response.output_text or "").strip() or "The AI service returned an empty response."
    except genai.errors.APIError as e:
        logger.error("Gemini API Error (%s %s): %s", e.code, e.status, e.message)
        if e.code == 504 or e.status == "DEADLINE_EXCEEDED":
            return "Gemini timed out while preparing a response. Please try again in a moment."
        return f"Sorry, the AI service could not complete the request: {str(e)}"
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        if isinstance(e, httpx.TimeoutException):
            return "The AI service took too long to respond. Please try again."
        return f"Sorry, the AI service could not complete the request: {str(e)}"
