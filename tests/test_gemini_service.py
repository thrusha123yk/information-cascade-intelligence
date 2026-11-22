import asyncio
from types import SimpleNamespace

from backend.app.services import gemini_service


def test_generate_response_uses_bounded_fast_interaction(monkeypatch):
    captured = {}

    class FakeInteractions:
        def create(self, **kwargs):
            captured["request"] = kwargs
            return SimpleNamespace(output_text="Concise answer")

    class FakeClient:
        def __init__(self, *, api_key, http_options):
            captured["api_key"] = api_key
            captured["http_options"] = http_options
            self.interactions = FakeInteractions()

    monkeypatch.setattr(gemini_service, "GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service.genai, "Client", FakeClient)

    result = asyncio.run(gemini_service.generate_response("What is the weather?"))

    assert result == "Concise answer"
    assert captured["http_options"].timeout == 25000
    assert captured["http_options"].retry_options.attempts == 1
    assert captured["request"]["model"] == gemini_service.GEMINI_MODEL_ID
    assert captured["request"]["input"] == "What is the weather?"
    assert captured["request"]["generation_config"] == {
        "max_output_tokens": 200,
        "thinking_level": "minimal",
    }
    assert captured["request"]["store"] is False
    assert captured["request"]["timeout"] == 25
    assert captured["request"]["automatic_continuation"] is False


def test_generate_response_explains_gemini_deadline_error(monkeypatch):
    class FakeInteractions:
        def create(self, **kwargs):
            raise gemini_service.genai.errors.ServerError(
                504,
                {"error": {"code": 504, "status": "DEADLINE_EXCEEDED"}},
            )

    class FakeClient:
        def __init__(self, **kwargs):
            self.interactions = FakeInteractions()

    monkeypatch.setattr(gemini_service, "GOOGLE_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service.genai, "Client", FakeClient)

    result = asyncio.run(gemini_service.generate_response("India viral news"))

    assert "Gemini timed out" in result
