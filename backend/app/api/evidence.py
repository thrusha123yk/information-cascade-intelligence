from fastapi import APIRouter, HTTPException
from ..database.repository import get_topic_by_id, get_evidence_record_for_topic
from ..services.evidence_service import evaluate_evidence_and_corroboration

router = APIRouter(prefix="/api/evidence", tags=["Credibility & Evidence Analysis"])

@router.get("/{topic_id}")
def get_topic_evidence(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
        
    record = get_evidence_record_for_topic(topic_id)
    if not record:
        record = evaluate_evidence_and_corroboration(top.get("articles", []), top.get("sources", []))
    else:
        record["corroboration_score"] = float(top.get("corroboration_score", 0))
        record["status_label"] = (
            "Multi-Source Corroborated" if record.get("corroboration_level") == "high" else (
                "Partially Corroborated" if record.get("corroboration_level") == "moderate" else (
                    "Single-Publisher Clustered" if record.get("corroboration_level") == "low" else "Insufficient Evidence"
                )
            )
        )
        
    return {
        "topic": {
            "id": top["id"],
            "label": top["label"],
            "sources": top.get("sources", []),
            "corroboration_score": top.get("corroboration_score", 0)
        },
        "evidence_record": record,
        "articles": [
            {
                "id": a["id"],
                "title": a["title"],
                "source": a.get("source"),
                "source_type": a.get("source_type"),
                "url": a.get("url"),
                "published_at": a.get("published_at")
            }
            for a in top.get("articles", [])
        ]
    }
