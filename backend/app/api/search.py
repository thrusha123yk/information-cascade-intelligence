from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.search_service import search_information_ecosystem, compare_two_topics

router = APIRouter(prefix="/api/search", tags=["Search and Exploration"])

@router.get("")
def search(
    q: Optional[str] = None,
    source: Optional[str] = None,
    min_score: Optional[float] = None
):
    # Guard if invoked as raw python function with Query objects
    q_str = str(q) if q is not None and not hasattr(q, "default") else None
    src_str = str(source) if source is not None and not hasattr(source, "default") else None
    score_val = float(min_score) if min_score is not None and not hasattr(min_score, "default") else None
    return search_information_ecosystem(query=q_str, source=src_str, min_cascade_score=score_val)

@router.get("/compare")
def compare_topics(
    topic_a: str = Query(..., description="First topic ID"),
    topic_b: str = Query(..., description="Second topic ID")
):
    comp = compare_two_topics(topic_a, topic_b)
    if not comp:
        raise HTTPException(status_code=404, detail="One or both topics could not be found for comparison.")
    return comp
