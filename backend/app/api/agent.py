from fastapi import APIRouter, Body
from ..services.agent_service import get_agent_response

agent_router = APIRouter(prefix="/api/agent", tags=["agent"])

@agent_router.post("/chat")
async def chat_with_agent(data: dict = Body(...)):
    prompt = data.get("prompt", "")
    topic_id = data.get("topic_id")
    response = await get_agent_response(prompt, topic_id)
    return {"response": response}
