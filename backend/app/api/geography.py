from fastapi import APIRouter, HTTPException
from ..database.repository import get_sqlite_connection
import json

router = APIRouter(prefix="/api/geography", tags=["Geography Analysis"])

@router.get("/source-countries")
def get_source_country_stats():
    """Analysis of publishing activity by source country using source_country column."""
    with get_sqlite_connection() as con:
        rows = con.execute("""
            SELECT
                source_country as country,
                COUNT(*) as article_count
            FROM articles
            WHERE source_country IS NOT NULL
            GROUP BY country
            ORDER BY article_count DESC
            LIMIT 20
        """).fetchall()
    return [{"country": r[0] if r[0] else "Unknown", "count": r[1]} for r in rows]

@router.get("/event-countries")
def get_event_country_stats():
    """Analysis of events by country using event_country column."""
    with get_sqlite_connection() as con:
        rows = con.execute("""
            SELECT
                event_country as country,
                COUNT(*) as article_count
            FROM articles
            WHERE event_country IS NOT NULL AND event_country != 'Unknown'
            GROUP BY country
            ORDER BY article_count DESC
            LIMIT 20
        """).fetchall()
    return [{"country": r[0], "count": r[1]} for r in rows]

@router.get("/topics/{country}")
def get_topics_for_country(country: str, type: str = "source"):
    """
    Get emerging topics for a specific country.
    type='source' checks source_country column.
    type='event' checks event_country column.
    """
    query = ""
    country = country.strip()
    if not country:
        raise HTTPException(status_code=400, detail="Country is required.")
    if type not in ("source", "event"):
        raise HTTPException(status_code=400, detail="type must be 'source' or 'event'.")
    if type == "source":
        query = """
            SELECT t.*
            FROM topics t
            JOIN topic_articles ta ON t.id = ta.topic_id
            JOIN articles a ON ta.article_id = a.id
            WHERE a.source_country = ?
            GROUP BY t.id
            ORDER BY t.cascade_score DESC
            LIMIT 20
        """
    else:
        query = """
            SELECT t.*
            FROM topics t
            JOIN topic_articles ta ON t.id = ta.topic_id
            JOIN articles a ON ta.article_id = a.id
            WHERE a.event_country = ?
            GROUP BY t.id
            ORDER BY t.cascade_score DESC
            LIMIT 20
        """

    with get_sqlite_connection() as con:
        rows = con.execute(query, (country,)).fetchall()

    return [dict(r) for r in rows]
