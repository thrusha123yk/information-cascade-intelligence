-- ==============================================================================
-- INFORMATION CASCADE INTELLIGENCE - DATABASE SCHEMA (PostgreSQL / Supabase)
-- Academic Research Database Definition for Information Cascade Intelligence
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 1. SOURCES
CREATE TABLE IF NOT EXISTS public.sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    domain TEXT,
    source_type TEXT NOT NULL DEFAULT 'news', -- news, official_body, weather_api, scientific_api
    reliability_tier TEXT DEFAULT 'tier-1-public',
    country TEXT DEFAULT 'Global',
    feed_url TEXT,
    total_articles INTEGER DEFAULT 0,
    last_collected_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. ARTICLES
CREATE TABLE IF NOT EXISTS public.articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'news',
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    author TEXT,
    location TEXT,
    content_hash TEXT UNIQUE NOT NULL,
    origin TEXT NOT NULL DEFAULT 'RSS', -- GDELT, RSS, Open-Meteo, NASA
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_articles_collected ON public.articles(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_published ON public.articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source ON public.articles(source);

-- 3. TOPICS
CREATE TABLE IF NOT EXISTS public.topics (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT DEFAULT '',
    keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    first_observed_at TIMESTAMPTZ DEFAULT NOW(),
    latest_observed_at TIMESTAMPTZ DEFAULT NOW(),
    article_count INTEGER DEFAULT 1,
    source_count INTEGER DEFAULT 1,
    cascade_score NUMERIC(5,2) DEFAULT 0,
    corroboration_score NUMERIC(5,2) DEFAULT 0,
    status TEXT DEFAULT 'emerging', -- emerging, active, maturing, plateaued
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_topics_cascade ON public.topics(cascade_score DESC);
CREATE INDEX IF NOT EXISTS idx_topics_latest ON public.topics(latest_observed_at DESC);

-- 4. TOPIC_ARTICLES (M2M)
CREATE TABLE IF NOT EXISTS public.topic_articles (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    article_id TEXT NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    similarity_score NUMERIC(5,4) DEFAULT 1.0,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unq_topic_article UNIQUE(topic_id, article_id)
);

CREATE INDEX IF NOT EXISTS idx_topic_articles_topic ON public.topic_articles(topic_id);

-- 5. EXTRACTED_ENTITIES
CREATE TABLE IF NOT EXISTS public.extracted_entities (
    id TEXT PRIMARY KEY,
    article_id TEXT NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    entity_text TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- PERSON, ORG, GPE, DATE, EVENT, QUANTITY
    salience NUMERIC(4,3) DEFAULT 0.5,
    context TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entities_article ON public.extracted_entities(article_id);
CREATE INDEX IF NOT EXISTS idx_entities_text ON public.extracted_entities(entity_text);

-- 6. NARRATIVE_RELATIONSHIPS (Graph Edges for Narrative Tree)
CREATE TABLE IF NOT EXISTS public.narrative_relationships (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    source_article_id TEXT NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    target_article_id TEXT NOT NULL REFERENCES public.articles(id) ON DELETE CASCADE,
    relationship_type TEXT NOT NULL, -- initial_report, corroborates, adds_details, reports_update, divergent_claim
    label TEXT NOT NULL,
    confidence NUMERIC(4,3) DEFAULT 0.75,
    textual_evidence TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_narratives_topic ON public.narrative_relationships(topic_id);

-- 7. EVIDENCE_RECORDS
CREATE TABLE IF NOT EXISTS public.evidence_records (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    corroboration_level TEXT NOT NULL, -- high, moderate, low, insufficient
    independent_sources_count INTEGER DEFAULT 1,
    consensus_claim TEXT,
    conflicting_points JSONB DEFAULT '[]'::jsonb,
    evidence_gaps JSONB DEFAULT '[]'::jsonb,
    unresolved_questions JSONB DEFAULT '[]'::jsonb,
    evaluated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_topic ON public.evidence_records(topic_id);

-- 8. CASCADE_METRICS
CREATE TABLE IF NOT EXISTS public.cascade_metrics (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    cascade_score NUMERIC(5,2) NOT NULL,
    velocity_score NUMERIC(5,2) DEFAULT 0,
    acceleration_rate NUMERIC(5,2) DEFAULT 0,
    source_diversity_score NUMERIC(5,2) DEFAULT 0,
    recency_score NUMERIC(5,2) DEFAULT 0,
    measured_volume INTEGER DEFAULT 0,
    computed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cascade_metrics_topic ON public.cascade_metrics(topic_id);

-- 9. IMPACT_ASSESSMENTS
CREATE TABLE IF NOT EXISTS public.impact_assessments (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    primary_category TEXT NOT NULL, -- Public Health, Environment, Public Safety, Economy, Government & Public Policy, Technology & Society
    potential_severity TEXT NOT NULL, -- Low, Moderate, High, Severe
    urgency_level TEXT NOT NULL, -- Immediate, Developing, Monitored, Low
    affected_population TEXT,
    affected_area TEXT,
    rationale TEXT NOT NULL,
    supporting_sources JSONB DEFAULT '[]'::jsonb,
    assessed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_impact_topic ON public.impact_assessments(topic_id);

-- 10. PREDICTIONS
CREATE TABLE IF NOT EXISTS public.predictions (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    horizon_hours INTEGER NOT NULL, -- 24, 48, 72
    expected_volume INTEGER NOT NULL,
    lower_bound INTEGER NOT NULL,
    upper_bound INTEGER NOT NULL,
    trajectory TEXT NOT NULL, -- accelerating, steady, decaying
    confidence_score NUMERIC(4,3) DEFAULT 0.70,
    model_name TEXT DEFAULT 'Baseline Exponential-Decay Trend',
    limitations_note TEXT DEFAULT 'Historical public news observation coverage only; not social media reach.',
    predicted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predictions_topic ON public.predictions(topic_id);

-- 11. COLLECTION_LOGS
CREATE TABLE IF NOT EXISTS public.collection_logs (
    id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    items_collected INTEGER DEFAULT 0,
    items_saved INTEGER DEFAULT 0,
    error_message TEXT,
    status TEXT NOT NULL, -- success, partial, failure
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_completed ON public.collection_logs(completed_at DESC);
