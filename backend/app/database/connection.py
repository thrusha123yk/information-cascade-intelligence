import sqlite3
import logging
from pathlib import Path
from ..config import SUPABASE_URL, SUPABASE_KEY, DATABASE_URL
from .schema import init_sqlite_db

logger = logging.getLogger(__name__)

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase PostgreSQL at %s", SUPABASE_URL)
    except Exception as exc:
        logger.warning("Supabase initialization failed (%s); using local SQLite", exc)
        supabase_client = None

def get_db_path() -> str:
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "", 1)
    return str(Path(__file__).resolve().parents[2] / "cascade_intelligence.db")

def get_sqlite_connection() -> sqlite3.Connection:
    path = get_db_path()
    init_sqlite_db(path)
    con = sqlite3.connect(path, timeout=15)
    con.row_factory = sqlite3.Row
    return con

def init_database():
    path = get_db_path()
    init_sqlite_db(path)
    backfill_country_metadata(path)
    logger.info("Initialized database tables at %s", path)


def backfill_country_metadata(path: str):
    """Best-effort metadata repair for databases collected before geo fields existed."""
    with sqlite3.connect(path, timeout=15) as con:
        con.execute(
            """
            UPDATE articles
            SET source_country = CASE
                WHEN source IN ('BBC World', 'BBC') THEN 'United Kingdom'
                WHEN source IN ('The Guardian World', 'The Guardian') THEN 'United Kingdom'
                WHEN source IN ('UN News', 'WHO News') THEN 'Switzerland'
                ELSE COALESCE(source_country, 'Unknown')
            END
            WHERE source_country IS NULL OR source_country = '' OR source_country = 'Unknown'
            """
        )
        try:
            rows = con.execute(
                """
                SELECT id, title, description
                FROM articles
                WHERE event_country IS NULL OR event_country = '' OR event_country = 'Unknown'
                """
            ).fetchall()
            if rows:
                from ..services.geo_service import extract_event_country
                for row in rows:
                    result = extract_event_country(
                        f"{row[1]}. {row[2] or ''}"
                    )
                    if result["country"] != "Unknown":
                        con.execute(
                            "UPDATE articles SET event_country = ? WHERE id = ?",
                            (result["country"], row[0]),
                        )
        except Exception as exc:
            logger.warning("Event-country backfill skipped: %s", exc)
        con.execute(
            """
            UPDATE articles SET event_country = CASE event_country
                WHEN 'USA' THEN 'United States'
                WHEN 'UK' THEN 'United Kingdom'
                WHEN 'Gaza' THEN 'Palestine'
                WHEN 'Russian' THEN 'Russia'
                ELSE event_country
            END
            """
        )
        con.commit()
