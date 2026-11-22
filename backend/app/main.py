import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import CORS_ORIGINS
from .database.connection import init_database
from .database.repository import get_overview_metrics, get_articles, get_topics
from .api import (
    overview_router, topics_router, narratives_router,
    evolution_router, cascades_router, evidence_router,
    impact_router, predictions_router, matrix_router,
    search_router, collection_router, articles_router,
    agent_router, geography_router
)

from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("InformationCascadeIntelligence")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    logger.info("Information Cascade Intelligence backend started successfully.")
    yield

app = FastAPI(
    title="Information Cascade Intelligence API",
    description="Academic Research AI Platform for Emerging Information Cascades, Narrative Trees & Social Impact",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Information Cascade Intelligence Research Platform",
        "version": "2.0.0"
    }

# Mount modular routers for all 10 dashboard modules
app.include_router(overview_router)
app.include_router(topics_router)
app.include_router(narratives_router)
app.include_router(evolution_router)
app.include_router(cascades_router)
app.include_router(evidence_router)
app.include_router(impact_router)
app.include_router(predictions_router)
app.include_router(matrix_router)
app.include_router(search_router)
app.include_router(collection_router)
app.include_router(articles_router)
app.include_router(agent_router)
app.include_router(geography_router)

# Backward-compatibility alias routes
@app.get("/api/analytics/overview")
def legacy_analytics_overview():
    metrics = get_overview_metrics()
    topics = get_topics(limit=10)
    return {
        "overview": {
            "total_items": metrics.get("total_articles", 0),
            "sources": metrics.get("distinct_publishers", 0),
            "social_items": 0,
            "weather_items": sum(1 for a in metrics.get("recent_articles", []) if "Open-Meteo" in a.get("source", "")),
        },
        "topics": topics,
        "timeline": [{"hour": t["time"], "count": t["count"]} for t in metrics.get("timeline", [])]
    }

@app.get("/api/items")
def legacy_items(limit: int = 100):
    arts = get_articles(limit=limit)
    return {"count": len(arts), "items": arts}
