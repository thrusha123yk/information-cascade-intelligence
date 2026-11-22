from .gemini_service import generate_response
from ..database.repository import get_topics, get_overview_metrics, get_topic_by_id

async def get_agent_response(user_prompt: str, topic_id: str = None) -> str:
    if not user_prompt or not user_prompt.strip():
        return "Please enter a research question."

    # Context data: Gather minimal context from real DB
    topics = get_topics(limit=5)
    overview = get_overview_metrics()

    context_str = f"Platform Overview: {overview['total_articles']} total articles collected.\n"
    if topic_id:
        selected_topic = get_topic_by_id(topic_id)
        if selected_topic:
            context_str += (
                f"Selected Topic: {selected_topic['label']}. "
                f"Description: {selected_topic.get('description', 'No description')}. "
                f"Articles: {selected_topic.get('article_count', 0)}. "
                f"Cascade Score: {selected_topic.get('cascade_score', 0)}.\n"
            )
    context_str += "Top Emerging Topics (Database Facts):\n"
    for t in topics:
        context_str += f"- Topic: {t['label']} (Articles: {t['article_count']}, Cascade Score: {t['cascade_score']})\n"

    system_prompt = (
        "You are an AI Research Analyst for the Information Cascade Intelligence platform. "
        "Your responses must strictly follow these rules:\n"
        "1. Separate 'Facts' (data retrieved from the provided platform context) from 'Analysis' (your AI interpretation).\n"
        "2. If you do not have sufficient information in the provided context, state clearly: 'I do not have enough data to confirm that fact' instead of inventing information.\n"
        "3. Do not invent statistics, evidence, or events.\n\n"
    )

    full_prompt = f"{system_prompt}\nPlatform Context Data:\n{context_str}\nUser Question: {user_prompt}"

    return await generate_response(full_prompt)
