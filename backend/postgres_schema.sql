
-- Information Cascade Intelligence
-- PostgreSQL schema matching the existing SQLite database.
-- Safe to run more than once.

CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT,
    published_at TEXT,
    collected_at TEXT NOT NULL,
    description TEXT,
    origin TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'news',
    author TEXT,
    location TEXT,
    content_hash TEXT,
    metadata TEXT DEFAULT '{}',
    source_country TEXT DEFAULT 'Unknown',
    event_country TEXT DEFAULT 'Unknown'
);

CREATE TABLE IF NOT EXISTS cascade_metrics (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    cascade_score DOUBLE PRECISION NOT NULL,
    velocity_score DOUBLE PRECISION DEFAULT 0.0,
    acceleration_rate DOUBLE PRECISION DEFAULT 0.0,
    source_diversity_score DOUBLE PRECISION DEFAULT 0.0,
    recency_score DOUBLE PRECISION DEFAULT 0.0,
    measured_volume INTEGER DEFAULT 0,
    computed_at TEXT
);

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

CREATE TABLE IF NOT EXISTS extracted_entities (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL,
    entity_text TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    salience DOUBLE PRECISION DEFAULT 0.5,
    context TEXT,
    created_at TEXT
);

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

CREATE TABLE IF NOT EXISTS narrative_relationships (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    source_article_id TEXT NOT NULL,
    target_article_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    label TEXT NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 0.75,
    textual_evidence TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS predictions (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    horizon_hours INTEGER NOT NULL,
    expected_volume INTEGER NOT NULL,
    lower_bound INTEGER NOT NULL,
    upper_bound INTEGER NOT NULL,
    trajectory TEXT NOT NULL,
    confidence_score DOUBLE PRECISION DEFAULT 0.70,
    model_name TEXT DEFAULT 'Baseline Exponential-Decay Trend',
    limitations_note TEXT DEFAULT 'Historical public news observation coverage only; not social media reach.',
    predicted_at TEXT
);

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

CREATE TABLE IF NOT EXISTS topic_articles (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    article_id TEXT NOT NULL,
    similarity_score DOUBLE PRECISION DEFAULT 1.0,
    added_at TEXT,
    UNIQUE (topic_id, article_id)
);

CREATE TABLE IF NOT EXISTS topic_history (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL,
    cascade_score DOUBLE PRECISION NOT NULL,
    snapshot_date TEXT NOT NULL,
    UNIQUE (topic_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT DEFAULT '',
    keywords TEXT DEFAULT '[]',
    first_observed_at TEXT,
    latest_observed_at TEXT,
    article_count INTEGER DEFAULT 1,
    source_count INTEGER DEFAULT 1,
    cascade_score DOUBLE PRECISION DEFAULT 0.0,
    corroboration_score DOUBLE PRECISION DEFAULT 0.0,
    status TEXT DEFAULT 'emerging',
    metadata TEXT DEFAULT '{}'
);

-- Indexes matching the existing SQLite database.

CREATE INDEX IF NOT EXISTS idx_art_collected
    ON articles (collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_art_source
    ON articles (source);

CREATE INDEX IF NOT EXISTS idx_logs_completed
    ON collection_logs (completed_at DESC);

CREATE INDEX IF NOT EXISTS idx_ent_article
    ON extracted_entities (article_id);

CREATE INDEX IF NOT EXISTS idx_narr_topic
    ON narrative_relationships (topic_id);

CREATE INDEX IF NOT EXISTS idx_top_articles_topic
    ON topic_articles (topic_id);

CREATE INDEX IF NOT EXISTS idx_hist_topic
    ON topic_history (topic_id);

CREATE INDEX IF NOT EXISTS idx_top_cascade
    ON topics (cascade_score DESC);
