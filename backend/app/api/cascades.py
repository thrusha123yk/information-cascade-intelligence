from fastapi import APIRouter, HTTPException
from ..database.repository import get_topics, get_topic_by_id, get_cascade_metric_for_topic
from ..services.cascade_service import compute_cascade_activity

router = APIRouter(prefix="/api/cascades", tags=["Cascade Analysis"])

@router.get("")
def get_all_cascade_metrics():
    topics = get_topics(limit=50)
    summaries = []
    for t in topics:
        metric = get_cascade_metric_for_topic(t["id"])
        summaries.append({
            "topic_id": t["id"],
            "label": t["label"],
            "cascade_score": float(t.get("cascade_score", 0)),
            "article_count": t.get("article_count", 0),
            "source_count": t.get("source_count", 0),
            "velocity_score": metric.get("velocity_score", 0) if metric else 0,
            "acceleration_rate": metric.get("acceleration_rate", 0) if metric else 0,
            "status": t.get("status", "emerging")
        })
    return summaries

@router.get("/{topic_id}")
def get_cascade_for_topic(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
        
    metric = get_cascade_metric_for_topic(topic_id)
    if not metric:
        metric = compute_cascade_activity(top.get("articles", []), top.get("sources", []))
        
    return {
        "topic": {
            "id": top["id"],
            "label": top["label"],
            "sources": top.get("sources", []),
            "article_count": top.get("article_count", 0)
        },
        "cascade_metrics": metric,
        "articles": [
            {
                "id": a["id"],
                "title": a["title"],
                "source": a.get("source"),
                "published_at": a.get("published_at"),
                "url": a.get("url")
            }
            for a in top.get("articles", [])
        ]
    }

