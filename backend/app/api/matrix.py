from fastapi import APIRouter
from ..database.repository import get_topics
from ..services.matrix_service import build_matrix_overview

router = APIRouter(prefix="/api/matrix", tags=["Information Classification Matrix"])

@router.get("")
def get_classification_matrix():
    topics = get_topics(limit=100)
    return build_matrix_overview(topics)

