from fastapi import APIRouter, HTTPException
from ..database.repository import get_topic_by_id, get_impact_assessment_for_topic
from ..services.impact_service import assess_social_impact

router = APIRouter(prefix="/api/impact", tags=["Social Impact Analysis"])

@router.get("/{topic_id}")
def get_topic_social_impact(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
        
    assessment = get_impact_assessment_for_topic(topic_id)
    if not assessment:
        assessment = assess_social_impact(top.get("articles", []), top["label"])
        
    return {
        "topic": {
            "id": top["id"],
            "label": top["label"],
            "sources": top.get("sources", []),
            "article_count": top.get("article_count", 0)
        },
        "impact_assessment": assessment
    }

