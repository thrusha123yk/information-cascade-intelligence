import sqlite3
import shutil
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("migration")

def migrate_database(db_path: str):
    db_file = Path(db_path)
    if not db_file.exists():
        logger.error(f"Database file not found at {db_path}")
        return

    # Backup
    backup_path = db_file.with_name(db_file.stem + "_backup" + db_file.suffix)
    shutil.copy2(db_file, backup_path)
    logger.info(f"Backup created at {backup_path}")

    with sqlite3.connect(db_path) as con:
        # Check existing columns
        cols = [r[1] for r in con.execute("PRAGMA table_info(articles)").fetchall()]

        if "source_country" not in cols:
            con.execute("ALTER TABLE articles ADD COLUMN source_country TEXT DEFAULT 'Unknown'")
            logger.info("Added source_country column.")
        if "event_country" not in cols:
            con.execute("ALTER TABLE articles ADD COLUMN event_country TEXT DEFAULT 'Unknown'")
            logger.info("Added event_country column.")

        # Create topic_history table with UNIQUE constraint
        con.execute("""
            CREATE TABLE IF NOT EXISTS topic_history (
                id TEXT PRIMARY KEY,
                topic_id TEXT NOT NULL,
                cascade_score REAL NOT NULL,
                snapshot_date TEXT NOT NULL,
                UNIQUE(topic_id, snapshot_date)
            )
        """)
        con.execute("CREATE INDEX IF NOT EXISTS idx_hist_topic ON topic_history(topic_id);")
        con.commit()

    logger.info(f"Migration completed successfully on {db_path}")

if __name__ == "__main__":
    target_db = sys.argv[1] if len(sys.argv) > 1 else "backend/cascade_intelligence.db"
    migrate_database(target_db)
