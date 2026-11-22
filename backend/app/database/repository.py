import sqlite3
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .connection import get_sqlite_connection, supabase_client

logger = logging.getLogger(__name__)

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

def canonical_article_id(url: str, title: str) -> str:
    return hashlib.sha256(f"{url.strip().lower()}|{title.strip().lower()}".encode("utf-8")).hexdigest()[:24]

# --- ARTICLES ---

def save_articles(items: List[Dict[str, Any]]) -> int:
    if not items:
        return 0
    now = datetime.now(timezone.utc).isoformat()
    saved = 0
    with get_sqlite_connection() as con:
        for it in items:
            art_id = it.get("id") or canonical_article_id(it["url"], it["title"])
            content_hash = it.get("content_hash") or generate_hash(it["url"])
            metadata_str = json.dumps(it.get("metadata", {}))
            
            source_c = it.get("source_country", "Unknown")
            event_c = it.get("event_country")
            if not event_c or event_c == "Unknown":
                from ..services.geo_service import extract_event_country
                combined_text = f"{it['title']}. {it.get('description', '')}"
                geo_res = extract_event_country(combined_text)
                event_c = geo_res["country"]

            cur = con.execute(
                """
                INSERT INTO articles (id, title, description, url, source, source_type, published_at, collected_at, author, location, content_hash, origin, metadata, source_country, event_country)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    description=excluded.description,
                    published_at=COALESCE(excluded.published_at, articles.published_at),
                    metadata=excluded.metadata,
                    source_country=excluded.source_country,
                    event_country=excluded.event_country
                """,
                (
                    art_id,
                    it["title"].strip(),
                    it.get("description", "") or "",
                    it["url"].strip(),
                    it.get("source", "Unknown"),
                    it.get("source_type", "news"),
                    it.get("published_at"),
                    it.get("collected_at", now),
                    it.get("author"),
                    it.get("location"),
                    content_hash,
                    it.get("origin", "RSS"),
                    metadata_str,
                    source_c,
                    event_c
                )
            )
            if cur.rowcount > 0:
                saved += 1
        con.commit()

    # Also update sources table counts
    update_sources_summary()
    return saved

def get_articles(limit: int = 500, offset: int = 0, source: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        if source:
            query += " AND source = ?"
            params.append(source)
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            term = f"%{search}%"
            params.extend([term, term])
        query += " ORDER BY published_at DESC, collected_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = con.execute(query, params).fetchall()
        
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["metadata"] = json.loads(d.get("metadata") or "{}")
            except Exception:
                d["metadata"] = {}
            result.append(d)
        return result

def get_article_by_id(article_id: str) -> Optional[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        r = con.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
        if not r:
            return None
        d = dict(r)
        try:
            d["metadata"] = json.loads(d.get("metadata") or "{}")
        except Exception:
            d["metadata"] = {}
        return d

# --- SOURCES ---

def update_sources_summary():
    with get_sqlite_connection() as con:
        rows = con.execute(
            """
            SELECT source, source_type, origin, COUNT(*) as count, MAX(collected_at) as last_seen
            FROM articles
            GROUP BY source, source_type, origin
            """
        ).fetchall()
        now = datetime.now(timezone.utc).isoformat()
        for r in rows:
            src_id = generate_hash(r["source"])[:16]
            con.execute(
                """
                INSERT INTO sources (id, name, domain, source_type, reliability_tier, country, total_articles, last_collected_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    total_articles=excluded.total_articles,
                    last_collected_at=excluded.last_collected_at
                """,
                (
                    src_id,
                    r["source"],
                    r["source"].lower().replace(" ", "") + ".org",
                    r["source_type"] or "news",
                    "Tier-1 Public" if "UN" in r["source"] or "WHO" in r["source"] or "BBC" in r["source"] else "Independent Public",
                    "Global",
                    r["count"],
                    r["last_seen"] or now,
                    now
                )
            )
        con.commit()

def get_sources() -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT * FROM sources ORDER BY total_articles DESC").fetchall()
        return [dict(r) for r in rows]

# --- TOPICS & TOPIC ARTICLES ---

def save_topics_and_relations(topics: List[Dict[str, Any]]):
    now = datetime.now(timezone.utc).isoformat()
    today_date = now.split("T")[0]
    with get_sqlite_connection() as con:
        for t in topics:
            top_id = t["id"]
            cascade_score = float(t.get("cascade_score", 0))
            con.execute(
                """
                INSERT INTO topics (id, label, description, keywords, first_observed_at, latest_observed_at, article_count, source_count, cascade_score, corroboration_score, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    label=excluded.label,
                    description=excluded.description,
                    keywords=excluded.keywords,
                    latest_observed_at=excluded.latest_observed_at,
                    article_count=excluded.article_count,
                    source_count=excluded.source_count,
                    cascade_score=excluded.cascade_score,
                    corroboration_score=excluded.corroboration_score,
                    status=excluded.status,
                    metadata=excluded.metadata
                """,
                (
                    top_id,
                    t["label"],
                    t.get("description", ""),
                    json.dumps(t.get("keywords", [])),
                    t.get("first_observed_at", now),
                    t.get("latest_observed_at", now),
                    t.get("article_count", len(t.get("articles", []))),
                    t.get("source_count", len(t.get("sources", []))),
                    cascade_score,
                    float(t.get("corroboration_score", 0)),
                    t.get("status", "emerging"),
                    json.dumps(t.get("metadata", {}))
                )
            )
            # Safely log daily historical snapshot without duplication
            hist_id = generate_hash(f"{top_id}|{today_date}")[:20]
            con.execute(
                """
                INSERT INTO topic_history (id, topic_id, cascade_score, snapshot_date)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(topic_id, snapshot_date) DO UPDATE SET
                    cascade_score=excluded.cascade_score
                """,
                (hist_id, top_id, cascade_score, today_date)
            )

            # Link topic articles
            for art in t.get("articles", []):
                rel_id = generate_hash(f"{top_id}|{art['id']}")[:20]
                con.execute(
                    """
                    INSERT INTO topic_articles (id, topic_id, article_id, similarity_score, added_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(topic_id, article_id) DO UPDATE SET
                        similarity_score=excluded.similarity_score
                    """,
                    (rel_id, top_id, art["id"], float(art.get("similarity", 1.0)), now)
                )
        con.commit()

def get_topics(limit: int = 50) -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT * FROM topics ORDER BY cascade_score DESC, article_count DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try: d["keywords"] = json.loads(d.get("keywords") or "[]")
            except Exception: d["keywords"] = []
            try: d["metadata"] = json.loads(d.get("metadata") or "{}")
            except Exception: d["metadata"] = {}
            
            # Fetch related articles
            art_rows = con.execute(
                """
                SELECT a.*, ta.similarity_score
                FROM articles a
                JOIN topic_articles ta ON a.id = ta.article_id
                WHERE ta.topic_id = ?
                ORDER BY a.published_at ASC, a.collected_at ASC
                """,
                (d["id"],)
            ).fetchall()
            
            articles = []
            sources = set()
            for ar in art_rows:
                ad = dict(ar)
                try: ad["metadata"] = json.loads(ad.get("metadata") or "{}")
                except Exception: ad["metadata"] = {}
                articles.append(ad)
                if ad.get("source"):
                    sources.add(ad["source"])
            d["articles"] = articles
            d["sources"] = list(sources)
            result.append(d)
        return result

def get_topic_by_id(topic_id: str) -> Optional[Dict[str, Any]]:
    topics = get_topics(limit=500)
    for t in topics:
        if t["id"] == topic_id:
            return t
    return None

# --- EXTRACTED ENTITIES ---

def save_entities(entities: List[Dict[str, Any]]):
    now = datetime.now(timezone.utc).isoformat()
    with get_sqlite_connection() as con:
        for ent in entities:
            eid = ent.get("id") or generate_hash(f"{ent['article_id']}|{ent['entity_text']}|{ent['entity_type']}")[:20]
            con.execute(
                """
                INSERT OR REPLACE INTO extracted_entities (id, article_id, entity_text, entity_type, salience, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    eid,
                    ent["article_id"],
                    ent["entity_text"],
                    ent["entity_type"],
                    float(ent.get("salience", 0.5)),
                    ent.get("context", ""),
                    now
                )
            )
        con.commit()

def get_entities_for_article(article_id: str) -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT * FROM extracted_entities WHERE article_id = ? ORDER BY salience DESC", (article_id,)).fetchall()
        return [dict(r) for r in rows]

# --- NARRATIVE RELATIONSHIPS ---

def save_narrative_relationships(rels: List[Dict[str, Any]]):
    now = datetime.now(timezone.utc).isoformat()
    with get_sqlite_connection() as con:
        for r in rels:
            rid = r.get("id") or generate_hash(f"{r['topic_id']}|{r['source_article_id']}|{r['target_article_id']}|{r['relationship_type']}")[:20]
            con.execute(
                """
                INSERT OR REPLACE INTO narrative_relationships (id, topic_id, source_article_id, target_article_id, relationship_type, label, confidence, textual_evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rid,
                    r["topic_id"],
                    r["source_article_id"],
                    r["target_article_id"],
                    r["relationship_type"],
                    r["label"],
                    float(r.get("confidence", 0.75)),
                    r.get("textual_evidence", ""),
                    now
                )
            )
        con.commit()

def get_narrative_relationships_for_topic(topic_id: str) -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT * FROM narrative_relationships WHERE topic_id = ?", (topic_id,)).fetchall()
        return [dict(r) for r in rows]

# --- EVIDENCE RECORDS ---

def save_evidence_record(record: Dict[str, Any]):
    now = datetime.now(timezone.utc).isoformat()
    rid = record.get("id") or generate_hash(f"evidence|{record['topic_id']}")[:20]
    with get_sqlite_connection() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO evidence_records (id, topic_id, corroboration_level, independent_sources_count, consensus_claim, conflicting_points, evidence_gaps, unresolved_questions, evaluated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rid,
                record["topic_id"],
                record["corroboration_level"],
                int(record.get("independent_sources_count", 1)),
                record.get("consensus_claim", ""),
                json.dumps(record.get("conflicting_points", [])),
                json.dumps(record.get("evidence_gaps", [])),
                json.dumps(record.get("unresolved_questions", [])),
                now
            )
        )
        con.commit()

def get_evidence_record_for_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        row = con.execute("SELECT * FROM evidence_records WHERE topic_id = ? ORDER BY evaluated_at DESC LIMIT 1", (topic_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        for field in ["conflicting_points", "evidence_gaps", "unresolved_questions"]:
            try: d[field] = json.loads(d.get(field) or "[]")
            except Exception: d[field] = []
        return d

# --- CASCADE METRICS ---

def save_cascade_metric(metric: Dict[str, Any]):
    now = datetime.now(timezone.utc).isoformat()
    mid = metric.get("id") or generate_hash(f"cascade|{metric['topic_id']}|{now}")[:20]
    with get_sqlite_connection() as con:
        con.execute(
            """
            INSERT INTO cascade_metrics (id, topic_id, cascade_score, velocity_score, acceleration_rate, source_diversity_score, recency_score, measured_volume, computed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mid,
                metric["topic_id"],
                float(metric["cascade_score"]),
                float(metric.get("velocity_score", 0)),
                float(metric.get("acceleration_rate", 0)),
                float(metric.get("source_diversity_score", 0)),
                float(metric.get("recency_score", 0)),
                int(metric.get("measured_volume", 0)),
                now
            )
        )
        con.commit()

def get_cascade_metric_for_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        row = con.execute("SELECT * FROM cascade_metrics WHERE topic_id = ? ORDER BY computed_at DESC LIMIT 1", (topic_id,)).fetchone()
        return dict(row) if row else None

# --- IMPACT ASSESSMENTS ---

def save_impact_assessment(assessment: Dict[str, Any]):
    now = datetime.now(timezone.utc).isoformat()
    iid = assessment.get("id") or generate_hash(f"impact|{assessment['topic_id']}")[:20]
    with get_sqlite_connection() as con:
        con.execute(
            """
            INSERT OR REPLACE INTO impact_assessments (id, topic_id, primary_category, potential_severity, urgency_level, affected_population, affected_area, rationale, supporting_sources, assessed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                iid,
                assessment["topic_id"],
                assessment["primary_category"],
                assessment["potential_severity"],
                assessment["urgency_level"],
                assessment.get("affected_population"),
                assessment.get("affected_area"),
                assessment["rationale"],
                json.dumps(assessment.get("supporting_sources", [])),
                now
            )
        )
        con.commit()

def get_impact_assessment_for_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        row = con.execute("SELECT * FROM impact_assessments WHERE topic_id = ? ORDER BY assessed_at DESC LIMIT 1", (topic_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        try: d["supporting_sources"] = json.loads(d.get("supporting_sources") or "[]")
        except Exception: d["supporting_sources"] = []
        return d

# --- PREDICTIONS ---

def save_predictions(preds: List[Dict[str, Any]]):
    now = datetime.now(timezone.utc).isoformat()
    with get_sqlite_connection() as con:
        for p in preds:
            pid = p.get("id") or generate_hash(f"pred|{p['topic_id']}|{p['horizon_hours']}|{now}")[:20]
            con.execute(
                """
                INSERT OR REPLACE INTO predictions (id, topic_id, horizon_hours, expected_volume, lower_bound, upper_bound, trajectory, confidence_score, model_name, limitations_note, predicted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pid,
                    p["topic_id"],
                    int(p["horizon_hours"]),
                    int(p["expected_volume"]),
                    int(p["lower_bound"]),
                    int(p["upper_bound"]),
                    p["trajectory"],
                    float(p.get("confidence_score", 0.70)),
                    p.get("model_name", "Baseline Exponential-Decay Trend"),
                    p.get("limitations_note", "Historical news observation coverage only; not social media reach."),
                    now
                )
            )
        con.commit()

def get_predictions_for_topic(topic_id: str) -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT * FROM predictions WHERE topic_id = ? ORDER BY horizon_hours ASC", (topic_id,)).fetchall()
        return [dict(r) for r in rows]

# --- COLLECTION LOGS ---

def log_collection(source_name: str, source_type: str, items_collected: int, items_saved: int, error_message: Optional[str], started_at: str, completed_at: str, status: str):
    lid = generate_hash(f"{source_name}|{started_at}")[:20]
    with get_sqlite_connection() as con:
        con.execute(
            """
            INSERT INTO collection_logs (id, source_name, source_type, items_collected, items_saved, error_message, status, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (lid, source_name, source_type, items_collected, items_saved, error_message, status, started_at, completed_at)
        )
        con.commit()

def get_collection_logs(limit: int = 50) -> List[Dict[str, Any]]:
    with get_sqlite_connection() as con:
        rows = con.execute("SELECT * FROM collection_logs ORDER BY completed_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]

def get_overview_metrics() -> Dict[str, Any]:
    with get_sqlite_connection() as con:
        total_articles = con.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        distinct_publishers = con.execute("SELECT COUNT(DISTINCT source) FROM articles").fetchone()[0]
        emerging_topics = con.execute("SELECT COUNT(*) FROM topics WHERE cascade_score > 30").fetchone()[0]
        total_topics = con.execute("SELECT COUNT(*) FROM topics").fetchone()[0]
        increasing_coverage_topics = con.execute("SELECT COUNT(*) FROM topics WHERE cascade_score >= 50").fetchone()[0]
        
        last_log = con.execute("SELECT completed_at, status FROM collection_logs ORDER BY completed_at DESC LIMIT 1").fetchone()
        last_collection_time = last_log[0] if last_log else None
        
        recent_articles = [dict(r) for r in con.execute("SELECT id, title, source, url, published_at, collected_at FROM articles ORDER BY collected_at DESC, published_at DESC LIMIT 6").fetchall()]
        
        # Sources breakdown
        sources_breakdown = [dict(r) for r in con.execute("SELECT source, COUNT(*) as count FROM articles GROUP BY source ORDER BY count DESC LIMIT 8").fetchall()]
        
        # Activity timeline (by day or hour)
        timeline_rows = con.execute(
            """
            SELECT SUBSTR(collected_at, 1, 13) || ':00' as time_bucket, COUNT(*) as count
            FROM articles
            WHERE collected_at IS NOT NULL
            GROUP BY time_bucket
            ORDER BY time_bucket DESC
            LIMIT 12
            """
        ).fetchall()
        timeline = [{"time": r["time_bucket"], "count": r["count"]} for r in reversed(timeline_rows)]
        
        return {
            "total_articles": total_articles,
            "total_topics": total_topics,
            "emerging_topics": emerging_topics,
            "increasing_coverage_topics": increasing_coverage_topics,
            "distinct_publishers": distinct_publishers,
            "last_collection_time": last_collection_time,
            "recent_articles": recent_articles,
            "sources_breakdown": sources_breakdown,
            "timeline": timeline
        }

