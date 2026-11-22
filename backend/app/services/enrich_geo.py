import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import sqlite3
from app.services.geo_service import extract_event_country
from app.database.connection import get_sqlite_connection

def enrich_existing_articles_with_geo():
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT id, title, description, source_country FROM articles").fetchall()
        print(f"Loaded {len(rows)} articles for geo enrichment.")

        updated_count = 0
        for r in rows:
            art_id, title, desc, current_sc = r
            new_sc = current_sc if current_sc and current_sc != "Unknown" else "Unknown"

            combined_text = f"{title}. {desc}"
            geo_res = extract_event_country(combined_text)
            event_c = geo_res["country"]

            con.execute(
                "UPDATE articles SET source_country = ?, event_country = ? WHERE id = ?",
                (new_sc, event_c, art_id)
            )
            updated_count += 1
        con.commit()
    print(f"Successfully enriched {updated_count} articles with geographical data.")

if __name__ == "__main__":
    enrich_existing_articles_with_geo()
