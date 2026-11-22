from .connection import init_database, get_sqlite_connection, supabase_client
from .repository import (
    save_articles, get_articles, get_article_by_id,
    save_topics_and_relations, get_topics, get_topic_by_id,
    save_entities, get_entities_for_article,
    save_narrative_relationships, get_narrative_relationships_for_topic,
    save_evidence_record, get_evidence_record_for_topic,
    save_cascade_metric, get_cascade_metric_for_topic,
    save_impact_assessment, get_impact_assessment_for_topic,
    save_predictions, get_predictions_for_topic,
    log_collection, get_collection_logs, get_sources, get_overview_metrics
)

__all__ = [
    "init_database", "get_sqlite_connection", "supabase_client",
    "save_articles", "get_articles", "get_article_by_id",
    "save_topics_and_relations", "get_topics", "get_topic_by_id",
    "save_entities", "get_entities_for_article",
    "save_narrative_relationships", "get_narrative_relationships_for_topic",
    "save_evidence_record", "get_evidence_record_for_topic",
    "save_cascade_metric", "get_cascade_metric_for_topic",
    "save_impact_assessment", "get_impact_assessment_for_topic",
    "save_predictions", "get_predictions_for_topic",
    "log_collection", "get_collection_logs", "get_sources", "get_overview_metrics"
]

