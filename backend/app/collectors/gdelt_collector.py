import httpx
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any
from ..config import GDELT_TIMESPAN, MAX_GDELT_RECORDS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (Academic Cascade Intelligence)"
}

def parse_gdelt_date(date_str: str) -> str:
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        clean = date_str.replace("Z", "")
        if "T" in clean:
            dt = datetime.strptime(clean, "%Y%m%dT%H%M%S")
        else:
            dt = datetime.strptime(clean, "%Y%m%d%H%M%S")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()

async def fetch_gdelt_articles() -> List[Dict[str, Any]]:
    """
    Collects real-time international news coverage from GDELT DOC 2.0 API.
    Handles rate-limits gracefully (e.g., 429) so collection never blocks other feeds.
    """
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": "climate OR health OR government OR technology OR economy OR crisis",
        "mode": "ArtList",
        "format": "json",
        "sort": "DateDesc",
        "maxrecords": str(min(MAX_GDELT_RECORDS, 40)),
        "timespan": GDELT_TIMESPAN
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=HEADERS) as client:
            response = await client.get(url, params=params)
            if response.status_code == 429:
                logger.warning("GDELT API rate limit active (429). Continuing with RSS, NASA & Weather.")
                return []
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.warning("GDELT collection skipped gracefully: %s", exc)
        return []
            
    articles = []
    now = datetime.now(timezone.utc).isoformat()
    for item in data.get("articles", []):
        raw_url = item.get("url")
        raw_title = item.get("title")
        if not raw_url or not raw_title:
            continue
        domain = item.get("domain") or "GDELT International Press"
        source_country = item.get("sourcecountry") or "Unknown"
        articles.append({
            "title": raw_title.strip(),
            "url": raw_url.strip(),
            "source": domain.capitalize() if "." not in domain else domain,
            "source_type": "global_news",
            "published_at": parse_gdelt_date(item.get("seendate")),
            "collected_at": now,
            "description": f"GDELT indexed report from {domain}. Language: {item.get('language', 'eng')}",
            "origin": "GDELT",
            "author": None,
            "location": item.get("sourcecountry") or "International",
            "source_country": source_country,
            "metadata": {
                "sourcecountry": source_country,
                "language": item.get("language"),
                "socialimage": item.get("socialimage")
            }
        })
    logger.info("GDELT collector fetched %d articles", len(articles))
    return articles
