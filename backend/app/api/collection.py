import logging
from fastapi import APIRouter
from ..collectors.orchestrator import run_data_collection_pipeline
from ..database.repository import get_collection_logs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Data Collection"])

@router.post("/collect")
async def trigger_collection():
    try:
        result = await run_data_collection_pipeline()
        return result
    except Exception as exc:
        logger.error("Data collection endpoint error: %s", exc, exc_info=True)
        return {
            "status": "error",
            "collected_raw": 0,
            "unique_records": 0,
            "saved_records": 0,
            "topics_discovered": 0,
            "entities_extracted": 0,
            "narrative_edges_formed": 0,
            "errors": [str(exc)]
        }

@router.get("/collection-status")
def get_collection_status():
    logs = get_collection_logs(limit=25)
    return {
        "status": "ready",
        "recent_logs": logs
    }
