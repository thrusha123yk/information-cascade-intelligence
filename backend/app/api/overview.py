from fastapi import APIRouter
from ..database.repository import get_overview_metrics, get_topics

router = APIRouter(prefix="/api/overview", tags=["Overview Dashboard"])

@router.get("")
def get_dashboard_overview():
    metrics = get_overview_metrics()
    topics = get_topics(limit=8)
    
    # Topic growth comparison chart
    growth_comparison = [
        {
            "id": t["id"],
            "label": t["label"][:26] + "..." if len(t["label"]) > 26 else t["label"],
            "cascade_score": float(t.get("cascade_score", 0)),
            "corroboration_score": float(t.get("corroboration_score", 0)),
            "article_count": t.get("article_count", 0),
            "source_count": t.get("source_count", 0)
        }
        for t in topics[:6]
    ]

    return {
        **metrics,
        "topics_ranking": growth_comparison
    }

