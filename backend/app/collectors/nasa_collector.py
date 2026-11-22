import httpx
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from ..config import NASA_EONET_ENABLED

logger = logging.getLogger(__name__)

async def fetch_nasa_events() -> List[Dict[str, Any]]:
    """
    Collects natural hazard and environmental events from NASA EONET (Earth Observatory Natural Event Tracker).
    Provides scientific ground truth and environmental context for climate/disaster cascade discovery.
    """
    if not NASA_EONET_ENABLED:
        return []
        
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    params = {
        "status": "open",
        "limit": "10"
    }
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            
        events = []
        now = datetime.now(timezone.utc).isoformat()
        for ev in data.get("events", []):
            title = ev.get("title", "Natural Event")
            categories = [c.get("title") for c in ev.get("categories", [])]
            cat_str = ", ".join(categories) if categories else "Environmental"
            
            # Find coordinates or geometry date
            geometries = ev.get("geometry", [])
            latest_geo = geometries[-1] if geometries else {}
            event_date = latest_geo.get("date") or now
            
            sources = ev.get("sources", [])
            primary_url = sources[0].get("url") if sources else f"https://eonet.gsfc.nasa.gov/event/{ev.get('id')}"
            
            description = (
                f"NASA Earth Observatory tracked event: '{title}'. "
                f"Category: {cat_str}. Status: {ev.get('status', 'Open')}. "
                f"Coordinates: {latest_geo.get('coordinates')}."
            )
            
            events.append({
                "title": f"NASA EONET: {title} ({cat_str})",
                "url": primary_url,
                "source": "NASA Earth Observatory (EONET)",
                "source_type": "scientific_api",
                "published_at": event_date,
                "collected_at": now,
                "description": description,
                "origin": "NASA",
                "author": "NASA Earth Science Division",
                "location": cat_str,
                "metadata": {
                    "event_id": ev.get("id"),
                    "categories": categories,
                    "magnitude": latest_geo.get("magnitudeValue")
                }
            })
        logger.info("NASA EONET collector fetched %d environmental events", len(events))
        return events
    except Exception as exc:
        logger.warning("NASA EONET collector error: %s", exc)
        return []

