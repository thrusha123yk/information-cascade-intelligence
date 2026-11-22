import sqlite3
from pathlib import Path

SQLITE_TABLES = [
    # 1. sources
    """
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        domain TEXT,
        source_type TEXT NOT NULL DEFAULT 'news',
        reliability_tier TEXT DEFAULT 'tier-1-public',
        country TEXT DEFAULT 'Global',
        feed_url TEXT,
        total_articles INTEGER DEFAULT 0,
        last_collected_at TEXT,
        created_at TEXT
    );
    """,
    # 2. articles
    """
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        url TEXT UNIQUE NOT NULL,
        source TEXT NOT NULL,
        source_type TEXT NOT NULL DEFAULT 'news',
        published_at TEXT,
        collected_at TEXT NOT NULL,
        author TEXT,
        location TEXT,
        content_hash TEXT UNIQUE NOT NULL,
        origin TEXT NOT NULL DEFAULT 'RSS',
        metadata TEXT DEFAULT '{}'
    );
    """,
    # 3. topics
    """
    CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        label TEXT NOT NULL,
        description TEXT DEFAULT '',
        keywords TEXT DEFAULT '[]',
        first_observed_at TEXT,
        latest_observed_at TEXT,
        article_count INTEGER DEFAULT 1,
        source_count INTEGER DEFAULT 1,
        cascade_score REAL DEFAULT 0.0,
        corroboration_score REAL DEFAULT 0.0,
        status TEXT DEFAULT 'emerging',
        metadata TEXT DEFAULT '{}'
    );
    """,
    # 4. topic_articles
    """
    CREATE TABLE IF NOT EXISTS topic_articles (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        article_id TEXT NOT NULL,
        similarity_score REAL DEFAULT 1.0,
        added_at TEXT,
        UNIQUE(topic_id, article_id)
    );
    """,
    # 5. extracted_entities
    """
    CREATE TABLE IF NOT EXISTS extracted_entities (
        id TEXT PRIMARY KEY,
        article_id TEXT NOT NULL,
        entity_text TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        salience REAL DEFAULT 0.5,
        context TEXT,
        created_at TEXT
    );
    """,
    # 6. narrative_relationships
    """
    CREATE TABLE IF NOT EXISTS narrative_relationships (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        source_article_id TEXT NOT NULL,
        target_article_id TEXT NOT NULL,
        relationship_type TEXT NOT NULL,
        label TEXT NOT NULL,
        confidence REAL DEFAULT 0.75,
        textual_evidence TEXT,
        created_at TEXT
    );
    """,
    # 7. evidence_records
    """
    CREATE TABLE IF NOT EXISTS evidence_records (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        corroboration_level TEXT NOT NULL,
        independent_sources_count INTEGER DEFAULT 1,
        consensus_claim TEXT,
        conflicting_points TEXT DEFAULT '[]',
        evidence_gaps TEXT DEFAULT '[]',
        unresolved_questions TEXT DEFAULT '[]',
        evaluated_at TEXT
    );
    """,
    # 8. cascade_metrics
    """
    CREATE TABLE IF NOT EXISTS cascade_metrics (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        cascade_score REAL NOT NULL,
        velocity_score REAL DEFAULT 0.0,
        acceleration_rate REAL DEFAULT 0.0,
        source_diversity_score REAL DEFAULT 0.0,
        recency_score REAL DEFAULT 0.0,
        measured_volume INTEGER DEFAULT 0,
        computed_at TEXT
    );
    """,
    # 9. impact_assessments
    """
    CREATE TABLE IF NOT EXISTS impact_assessments (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        primary_category TEXT NOT NULL,
        potential_severity TEXT NOT NULL,
        urgency_level TEXT NOT NULL,
        affected_population TEXT,
        affected_area TEXT,
        rationale TEXT NOT NULL,
        supporting_sources TEXT DEFAULT '[]',
        assessed_at TEXT
    );
    """,
    # 10. predictions
    """
    CREATE TABLE IF NOT EXISTS predictions (
        id TEXT PRIMARY KEY,
        topic_id TEXT NOT NULL,
        horizon_hours INTEGER NOT NULL,
        expected_volume INTEGER NOT NULL,
        lower_bound INTEGER NOT NULL,
        upper_bound INTEGER NOT NULL,
        trajectory TEXT NOT NULL,
        confidence_score REAL DEFAULT 0.70,
        model_name TEXT DEFAULT 'Baseline Exponential-Decay Trend',
        limitations_note TEXT DEFAULT 'Historical public news observation coverage only; not social media reach.',
        predicted_at TEXT
    );
    """,
    # 11. collection_logs
    """
    CREATE TABLE IF NOT EXISTS collection_logs (
        id TEXT PRIMARY KEY,
        source_name TEXT NOT NULL,
        source_type TEXT NOT NULL,
        items_collected INTEGER DEFAULT 0,
        items_saved INTEGER DEFAULT 0,
        error_message TEXT,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT NOT NULL
    );
    """
]

def init_sqlite_db(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as con:
        con.execute("PRAGMA journal_mode=WAL;")
        for stmt in SQLITE_TABLES:
            con.execute(stmt)

        # Existing databases can predate geographical metadata. Add the columns
        # here so startup always preserves compatibility with new collectors.
        article_columns = {
            row[1] for row in con.execute("PRAGMA table_info(articles)").fetchall()
        }
        if "source_country" not in article_columns:
            con.execute(
                "ALTER TABLE articles ADD COLUMN source_country TEXT DEFAULT 'Unknown'"
            )
        if "event_country" not in article_columns:
            con.execute(
                "ALTER TABLE articles ADD COLUMN event_country TEXT DEFAULT 'Unknown'"
            )
        # Create useful indexes
        con.execute("CREATE INDEX IF NOT EXISTS idx_art_collected ON articles(collected_at DESC);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_art_url ON articles(url);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_art_source ON articles(source);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_top_cascade ON topics(cascade_score DESC);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_top_articles_topic ON topic_articles(topic_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_ent_article ON extracted_entities(article_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_narr_topic ON narrative_relationships(topic_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_logs_completed ON collection_logs(completed_at DESC);")
        con.commit()

