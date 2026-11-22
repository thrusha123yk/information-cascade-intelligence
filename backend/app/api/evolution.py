from fastapi import APIRouter, HTTPException
from ..database.repository import get_topic_by_id, get_entities_for_article
from ..services.evolution_service import analyze_information_evolution

router = APIRouter(prefix="/api/evolution", tags=["Information Evolution Analysis"])

@router.get("/{topic_id}")
def get_topic_evolution(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
        
    articles = top.get("articles", [])
    entities = []
    for a in articles:
        entities.extend(get_entities_for_article(a["id"]))
        
    evolution = analyze_information_evolution(articles, entities)
    return {
        "topic": {
            "id": top["id"],
            "label": top["label"],
            "first_observed_at": top.get("first_observed_at"),
            "latest_observed_at": top.get("latest_observed_at"),
            "source_count": top.get("source_count", 0),
            "article_count": top.get("article_count", 0)
        },
        **evolution
    }

