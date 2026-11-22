import asyncio
import re
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any, Tuple
import httpx
import feedparser
from ..config import RSS_FEEDS

# Verified publisher country mappings (Rule: never assume from article topic)
VERIFIED_PUBLISHER_COUNTRIES = {
    "BBC World": "United Kingdom",
    "The Guardian World": "United Kingdom",
    "UN News": "Switzerland", # UN HQ / Geneva
    "WHO News": "Switzerland"  # WHO HQ / Geneva
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 (Academic Cascade Intelligence)"
}

def strip_html(html_str: str) -> str:
    if not html_str:
        return ""
    clean = re.sub(r"<[^>]+>", " ", html_str)
    return " ".join(clean.split())

def parse_rss_date(date_str: str) -> str:
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()

async def fetch_rss_feed(feed_name: str, feed_url: str) -> List[Dict[str, Any]]:
    items = []
    now = datetime.now(timezone.utc).isoformat()
    source_type = "official_body" if ("UN" in feed_name or "WHO" in feed_name) else "news"
    
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers=HEADERS) as client:
            resp = await client.get(feed_url)
            resp.raise_for_status()
            content = resp.text
            
        parsed = feedparser.parse(content)
        for entry in parsed.entries[:35]:
            title = entry.get("title")
            link = entry.get("link")
            if not title or not link:
                continue
                
            raw_summary = entry.get("summary") or entry.get("description") or ""
            clean_desc = strip_html(raw_summary)[:1200]
            pub_date = parse_rss_date(entry.get("published") or entry.get("updated"))
            
            source_country = VERIFIED_PUBLISHER_COUNTRIES.get(feed_name, "Unknown")
            items.append({
                "title": title.strip(),
                "url": link.strip(),
                "source": feed_name,
                "source_type": source_type,
                "published_at": pub_date,
                "collected_at": now,
                "description": clean_desc,
                "origin": "RSS",
                "author": entry.get("author"),
                "location": "Global",
                "source_country": source_country,
                "metadata": {
                    "sourcecountry": source_country,
                    "tags": [t.get("term") for t in entry.get("tags", []) if t.get("term")]
                }
            })
        logger.info("Feed %s parsed %d items successfully", feed_name, len(items))
        return items
    except Exception as exc:
        logger.warning("Feed %s failed: %s", feed_name, exc)
        return []

async def fetch_all_rss_feeds() -> Tuple[List[Dict[str, Any]], List[str]]:
    tasks = [fetch_rss_feed(name, url) for name, url in RSS_FEEDS]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_items = []
    errors = []
    for (name, _), res in zip(RSS_FEEDS, results):
        if isinstance(res, Exception):
            errors.append(f"{name}: {str(res)}")
        elif isinstance(res, list):
            all_items.extend(res)
    logger.info("RSS collector fetched %d total articles across all feeds", len(all_items))
    return all_items, errors
