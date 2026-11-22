import logging
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any
from ..database.repository import (
    get_articles, save_topics_and_relations, save_entities,
    save_narrative_relationships, save_evidence_record,
    save_cascade_metric, save_impact_assessment, save_predictions,
    get_entities_for_article
)
from .nlp_service import (
    build_tfidf_similarity, extract_keywords, extract_entities_from_text
)
from .cascade_service import compute_cascade_activity
from .evidence_service import evaluate_evidence_and_corroboration
from .impact_service import assess_social_impact
from .prediction_service import forecast_cascade_growth
from .narrative_service import build_react_flow_narrative_graph

logger = logging.getLogger(__name__)

def cluster_articles_into_topics(articles: List[Dict[str, Any]], similarity_threshold: float = 0.22) -> List[Dict[str, Any]]:
    if not articles:
        return []

    texts = [
        (a.get("title", "") + " " + (a.get("description") or ""))
        for a in articles
    ]
    _, sim_matrix = build_tfidf_similarity(texts)
    
    n = len(articles)
    visited = set()
    clusters = []

    # Connected components via similarity threshold
    for i in range(n):
        if i in visited:
            continue
        group_indices = [i]
        visited.add(i)
        if sim_matrix is not None:
            for j in range(i + 1, n):
                if j not in visited and sim_matrix[i, j] >= similarity_threshold:
                    group_indices.append(j)
                    visited.add(j)
        clusters.append(group_indices)

    topics = []
    for k, idx_list in enumerate(clusters):
        cluster_articles = [articles[i] for i in idx_list]
        cluster_texts = [
            (a.get("title", "") + " " + (a.get("description") or ""))
            for a in cluster_articles
        ]
        
        # Keywords
        kws = extract_keywords(cluster_texts, top_n=6)
        
        # Sources
        sources = list(set(a.get("source") for a in cluster_articles if a.get("source")))
        
        # Timestamps
        pub_dates = [
            a.get("published_at") or a.get("collected_at")
            for a in cluster_articles if (a.get("published_at") or a.get("collected_at"))
        ]
        pub_dates.sort()
        first_seen = pub_dates[0] if pub_dates else datetime.now(timezone.utc).isoformat()
        latest_seen = pub_dates[-1] if pub_dates else datetime.now(timezone.utc).isoformat()
        
        # Cascade metrics
        cascade_data = compute_cascade_activity(cluster_articles, sources)
        
        # Evidence analysis
        evidence_data = evaluate_evidence_and_corroboration(cluster_articles, sources)
        
        # Label formulation: Use primary article title or top keywords
        primary_title = cluster_articles[0].get("title", "Emerging Cascade Topic")
        topic_label = primary_title
        if len(kws) >= 2 and len(primary_title) > 90:
            topic_label = " ".join([w.capitalize() for w in kws[:3]]) + f" Cascade ({len(cluster_articles)} reports)"

        # Unique topic ID
        topic_hash = hashlib.sha256(f"{first_seen}|{primary_title}".encode()).hexdigest()[:16]
        topic_id = f"topic-{topic_hash}"

        topics.append({
            "id": topic_id,
            "label": topic_label,
            "description": (cluster_articles[0].get("description") or f"Discovered topic cluster encompassing {len(cluster_articles)} public reports.")[:400],
            "keywords": kws,
            "first_observed_at": first_seen,
            "latest_observed_at": latest_seen,
            "article_count": len(cluster_articles),
            "source_count": len(sources),
            "cascade_score": cascade_data["cascade_score"],
            "corroboration_score": evidence_data["corroboration_score"],
            "status": "active" if cascade_data["cascade_score"] >= 40 else "emerging",
            "articles": cluster_articles,
            "sources": sources,
            "cascade_data": cascade_data,
            "evidence_data": evidence_data
        })

    # Sort topics by cascade score and article count
    topics.sort(key=lambda t: (t["cascade_score"], t["article_count"]), reverse=True)
    return topics

def run_topic_clustering_pipeline() -> Dict[str, Any]:
    """
    Full automated pipeline that:
      1. Reads all collected articles
      2. Performs NER on articles
      3. Discovers topic clusters using TF-IDF & Cosine Similarity
      4. Builds narrative relationships for React Flow
      5. Generates cascade metrics, evidence evaluations, impact assessments, and predictions
      6. Persists all structured data to the database
    """
    logger.info("Executing comprehensive topic clustering & AI cascade pipeline...")
    articles = get_articles(limit=1000)
    if not articles:
        return {"topics_discovered": 0, "entities_extracted": 0, "narrative_edges": 0}

    # 1. Extract entities for all articles
    total_entities = 0
    all_extracted_entities = []
    for art in articles:
        combined_text = (art.get("title", "") + " " + (art.get("description") or ""))
        ents = extract_entities_from_text(combined_text, art["id"])
        if ents:
            total_entities += len(ents)
            all_extracted_entities.extend(ents)
            save_entities(ents)

    # 2. Cluster into topics
    topics = cluster_articles_into_topics(articles)
    save_topics_and_relations(topics)

    total_edges = 0
    # 3. For each topic, run deep module analyses and store
    for top in topics:
        top_id = top["id"]
        cluster_arts = top["articles"]
        
        # Get entities for this topic's articles
        topic_entities = []
        for a in cluster_arts:
            topic_entities.extend(get_entities_for_article(a["id"]))

        # A. Narrative Graph
        graph = build_react_flow_narrative_graph(top_id, cluster_arts, topic_entities)
        narrative_edges_to_save = []
        for e in graph["edges"]:
            narrative_edges_to_save.append({
                "topic_id": top_id,
                "source_article_id": e["source"],
                "target_article_id": e["target"],
                "relationship_type": e.get("data", {}).get("relationship_type", "corroborates"),
                "label": e.get("label", "Related"),
                "confidence": 0.85,
                "textual_evidence": f"Shared entities: {e.get('data', {}).get('shared_entities_count', 0)}"
            })
        save_narrative_relationships(narrative_edges_to_save)
        total_edges += len(narrative_edges_to_save)

        # B. Cascade Metric
        c_data = top["cascade_data"]
        save_cascade_metric({
            "topic_id": top_id,
            "cascade_score": c_data["cascade_score"],
            "velocity_score": c_data["velocity_score"],
            "acceleration_rate": c_data["acceleration_rate"],
            "source_diversity_score": c_data["source_diversity_score"],
            "recency_score": c_data["recency_score"],
            "measured_volume": c_data["measured_volume"]
        })

        # C. Evidence Record
        ev_data = top["evidence_data"]
        save_evidence_record({
            "topic_id": top_id,
            "corroboration_level": ev_data["corroboration_level"],
            "independent_sources_count": ev_data["independent_sources_count"],
            "consensus_claim": ev_data["consensus_claim"],
            "conflicting_points": ev_data["conflicting_points"],
            "evidence_gaps": ev_data["evidence_gaps"],
            "unresolved_questions": ev_data["unresolved_questions"]
        })

        # D. Social Impact Assessment
        impact = assess_social_impact(cluster_arts, top["label"])
        save_impact_assessment({
            "topic_id": top_id,
            "primary_category": impact["primary_category"],
            "potential_severity": impact["potential_severity"],
            "urgency_level": impact["urgency_level"],
            "affected_population": impact["affected_population"],
            "affected_area": impact["affected_area"],
            "rationale": impact["rationale"],
            "supporting_sources": impact["supporting_sources"]
        })

        # E. Growth Prediction
        preds = forecast_cascade_growth(cluster_arts, top["cascade_score"])
        for p in preds:
            p["topic_id"] = top_id
        save_predictions(preds)

    logger.info("Pipeline complete: %d topics, %d entities, %d narrative edges", len(topics), total_entities, total_edges)
    return {
        "topics_discovered": len(topics),
        "entities_extracted": total_entities,
        "narrative_edges": total_edges
    }

