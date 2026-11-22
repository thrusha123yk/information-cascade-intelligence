import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from .gdelt_collector import fetch_gdelt_articles
from .rss_collector import fetch_all_rss_feeds
from .weather_collector import fetch_weather_context
from .nasa_collector import fetch_nasa_events
from ..database.repository import save_articles, log_collection
from ..services.topic_service import run_topic_clustering_pipeline

logger = logging.getLogger(__name__)

async def run_data_collection_pipeline() -> Dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()
    logger.info("Executing public data collection pipeline...")
    
    # Run all 4 public connectors concurrently
    tasks = [
        fetch_gdelt_articles(),
        fetch_all_rss_feeds(),
        fetch_weather_context(),
        fetch_nasa_events()
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    gdelt_res, rss_res, weather_res, nasa_res = results
    
    all_items: List[Dict[str, Any]] = []
    errors: List[str] = []
    
    # Process GDELT
    if isinstance(gdelt_res, list) and gdelt_res:
        all_items.extend(gdelt_res)
        log_collection("GDELT DOC API", "global_news", len(gdelt_res), len(gdelt_res), None, started_at, datetime.now(timezone.utc).isoformat(), "success")
    elif isinstance(gdelt_res, Exception):
        errors.append(f"GDELT: {str(gdelt_res)}")
        
    # Process RSS
    if isinstance(rss_res, tuple):
        rss_items, rss_errors = rss_res
        all_items.extend(rss_items)
        errors.extend(rss_errors)
        log_collection("Public RSS Feeds", "news", len(rss_items), len(rss_items), None, started_at, datetime.now(timezone.utc).isoformat(), "success")
    elif isinstance(rss_res, Exception):
        errors.append(f"RSS: {str(rss_res)}")
        
    # Process Weather
    if isinstance(weather_res, list) and weather_res:
        all_items.extend(weather_res)
        log_collection("Open-Meteo", "weather_api", len(weather_res), len(weather_res), None, started_at, datetime.now(timezone.utc).isoformat(), "success")
        
    # Process NASA
    if isinstance(nasa_res, list) and nasa_res:
        all_items.extend(nasa_res)
        log_collection("NASA EONET", "scientific_api", len(nasa_res), len(nasa_res), None, started_at, datetime.now(timezone.utc).isoformat(), "success")
        
    # Deduplicate strictly by canonical URL
    deduped = {}
    for it in all_items:
        u = it.get("url", "").strip()
        if u and u not in deduped:
            deduped[u] = it
    unique_items = list(deduped.values())
    
    saved_count = 0
    if unique_items:
        try:
            saved_count = save_articles(unique_items)
        except Exception as exc:
            logger.error("Database save failed: %s", exc)
            errors.append(f"Storage: {str(exc)}")
    
    # Execute NLP & clustering pipeline on updated dataset
    analysis_stats = {}
    try:
        analysis_stats = run_topic_clustering_pipeline()
    except Exception as exc:
        logger.error("Analysis pipeline error: %s", exc, exc_info=True)
        errors.append(f"Clustering: {str(exc)}")
        
    completed_at = datetime.now(timezone.utc).isoformat()
    return {
        "status": "success" if unique_items else ("partial" if errors else "completed_empty"),
        "collected_raw": len(all_items),
        "unique_records": len(unique_items),
        "saved_records": saved_count,
        "topics_discovered": analysis_stats.get("topics_discovered", 0),
        "entities_extracted": analysis_stats.get("entities_extracted", 0),
        "narrative_edges_formed": analysis_stats.get("narrative_edges", 0),
        "errors": errors,
        "started_at": started_at,
        "completed_at": completed_at
    }
