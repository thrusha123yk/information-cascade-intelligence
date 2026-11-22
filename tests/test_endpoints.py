import pytest
from backend.app.api.overview import get_dashboard_overview
from backend.app.api.topics import list_topics, get_single_topic
from backend.app.api.narratives import get_available_narrative_topics, get_narrative_graph_for_topic
from backend.app.api.evolution import get_topic_evolution
from backend.app.api.cascades import get_all_cascade_metrics, get_cascade_for_topic
from backend.app.api.evidence import get_topic_evidence
from backend.app.api.impact import get_topic_social_impact
from backend.app.api.predictions import get_topic_predictions
from backend.app.api.matrix import get_classification_matrix
from backend.app.api.search import search, compare_topics
from backend.app.api.articles import list_articles, list_sources
from backend.app.api.collection import get_collection_status
from backend.app.api.geography import (
    get_source_country_stats,
    get_event_country_stats,
    get_topics_for_country,
)
from backend.app.database.repository import get_topics

def test_overview_endpoint():
    data = get_dashboard_overview()
    assert "total_articles" in data
    assert "distinct_publishers" in data
    assert "topics_ranking" in data
    assert isinstance(data["topics_ranking"], list)

def test_topics_endpoints():
    topics = list_topics(limit=10)
    assert isinstance(topics, list)
    assert len(topics) > 0
    
    first_id = topics[0]["id"]
    single = get_single_topic(first_id)
    assert single["id"] == first_id
    assert "articles" in single
    assert "keywords" in single

def test_narratives_endpoints():
    topics = get_topics(limit=1)
    assert len(topics) > 0
    top_id = topics[0]["id"]
    
    avail = get_available_narrative_topics()
    assert isinstance(avail, list)
    
    graph = get_narrative_graph_for_topic(top_id)
    assert "nodes" in graph
    assert "edges" in graph
    assert "topic" in graph
    assert len(graph["nodes"]) > 0

def test_evolution_endpoint():
    topics = get_topics(limit=1)
    top_id = topics[0]["id"]
    
    evol = get_topic_evolution(top_id)
    assert "timeline" in evol
    assert "total_steps" in evol
    assert "all_accumulated_entities" in evol

def test_cascades_endpoints():
    topics = get_topics(limit=1)
    top_id = topics[0]["id"]
    
    all_cascades = get_all_cascade_metrics()
    assert isinstance(all_cascades, list)
    
    detail = get_cascade_for_topic(top_id)
    assert "cascade_metrics" in detail
    assert "cascade_score" in detail["cascade_metrics"]

def test_evidence_endpoint():
    topics = get_topics(limit=1)
    top_id = topics[0]["id"]
    
    ev = get_topic_evidence(top_id)
    assert "evidence_record" in ev
    rec = ev["evidence_record"]
    assert "corroboration_level" in rec
    assert "corroboration_score" in rec

def test_impact_endpoint():
    topics = get_topics(limit=1)
    top_id = topics[0]["id"]
    
    imp = get_topic_social_impact(top_id)
    assert "impact_assessment" in imp
    assessment = imp["impact_assessment"]
    assert "primary_category" in assessment
    assert "potential_severity" in assessment

def test_predictions_endpoint():
    topics = get_topics(limit=1)
    top_id = topics[0]["id"]
    
    pred = get_topic_predictions(top_id)
    assert "predictions" in pred
    # The system now generates predictions per-horizon in batches,
    # so we check that we have at least the required horizons
    horizons = [p["horizon_hours"] for p in pred["predictions"]]
    assert 24 in horizons
    assert 48 in horizons
    assert 72 in horizons

def test_matrix_endpoint():
    matrix = get_classification_matrix()
    assert "quadrants" in matrix
    assert "Verified Breaking News" in matrix["quadrants"]
    assert "Viral Disinformation" in matrix["quadrants"]
    assert "Niche Fact" in matrix["quadrants"]
    assert "Isolated Rumor" in matrix["quadrants"]

def test_search_and_compare_endpoints():
    srch = search(q="news")
    assert "topics" in srch
    assert "articles" in srch
    
    topics = get_topics(limit=2)
    if len(topics) >= 2:
        comp = compare_topics(topic_a=topics[0]["id"], topic_b=topics[1]["id"])
        assert "comparison" in comp
        assert "topic_a" in comp
        assert "topic_b" in comp

def test_articles_and_sources_endpoints():
    arts = list_articles(limit=5)
    assert "count" in arts
    assert "articles" in arts
    
    srcs = list_sources()
    assert "count" in srcs
    assert "sources" in srcs

def test_collection_status_endpoint():
    status = get_collection_status()
    assert "status" in status
    assert "recent_logs" in status


def test_geography_country_endpoints():
    source_countries = get_source_country_stats()
    event_countries = get_event_country_stats()
    assert isinstance(source_countries, list)
    assert isinstance(event_countries, list)

    if source_countries:
        topics = get_topics_for_country(source_countries[0]["country"], type="source")
        assert isinstance(topics, list)
