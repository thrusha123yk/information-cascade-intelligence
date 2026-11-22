from fastapi import APIRouter, HTTPException
from typing import Optional
from ..database.repository import get_topics, get_topic_by_id

router = APIRouter(prefix="/api/topics", tags=["Emerging Topic Discovery"])

@router.get("")
def list_topics(limit: int = 50, sort_by: str = "cascade"):
    topics = get_topics(limit=limit)
    if sort_by == "articles":
        topics.sort(key=lambda x: x.get("article_count", 0), reverse=True)
    elif sort_by == "corroboration":
        topics.sort(key=lambda x: float(x.get("corroboration_score", 0)), reverse=True)
    else:
        topics.sort(key=lambda x: float(x.get("cascade_score", 0)), reverse=True)
    return topics

@router.get("/{topic_id}")
def get_single_topic(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
    return top

