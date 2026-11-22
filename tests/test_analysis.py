import pytest
from backend.app.database.schema import init_sqlite_db
from backend.app.database.repository import (
    save_articles, get_articles, get_topics, get_overview_metrics
)
from backend.app.services.nlp_service import extract_entities_from_text, compute_lexical_differences
from backend.app.services.cascade_service import compute_cascade_activity
from backend.app.services.evidence_service import evaluate_evidence_and_corroboration
from backend.app.services.impact_service import assess_social_impact
from backend.app.services.prediction_service import forecast_cascade_growth
from backend.app.services.matrix_service import classify_topic_in_matrix, build_matrix_overview
from backend.app.services.narrative_service import build_react_flow_narrative_graph
from backend.app.services.topic_service import cluster_articles_into_topics

def test_empty_database():
    metrics = get_overview_metrics()
    assert "total_articles" in metrics
    assert "distinct_publishers" in metrics

def test_entity_extraction():
    sample_text = "The UN and WHO declared a health emergency in Geneva after Dr. Tedros issued a warning about 500 cases."
    entities = extract_entities_from_text(sample_text, "test-art-1")
    assert len(entities) > 0
    types = [e["entity_type"] for e in entities]
    assert "ORG" in types or "GPE" in types or "PERSON" in types

def test_cascade_activity_calculation():
    articles = [
        {"id": "1", "title": "Headline 1", "source": "BBC World", "published_at": "2026-11-06T00:00:00Z"},
        {"id": "2", "title": "Headline 2", "source": "The Guardian", "published_at": "2026-11-06T01:00:00Z"},
        {"id": "3", "title": "Headline 3", "source": "UN News", "published_at": "2026-11-06T02:00:00Z"}
    ]
    sources = ["BBC World", "The Guardian", "UN News"]
    res = compute_cascade_activity(articles, sources)
    assert 0 <= res["cascade_score"] <= 100
    assert res["measured_volume"] == 3
    assert "social media" not in res["activity_trend"]

def test_evidence_evaluation():
    articles = [
        {"title": "Global climate pact signed", "source": "UN News", "description": "195 nations reach historic agreement."},
        {"title": "Climate deal finalized in Geneva", "source": "BBC World", "description": "195 countries agree on emissions goals."}
    ]
    sources = ["UN News", "BBC World"]
    evidence = evaluate_evidence_and_corroboration(articles, sources)
    assert evidence["corroboration_score"] > 30
    assert evidence["independent_sources_count"] == 2
    assert "methodology_note" in evidence

def test_impact_assessment():
    articles = [
        {"title": "New respiratory outbreak identified by hospitals", "description": "Public health agencies report cases in hospitals."}
    ]
    impact = assess_social_impact(articles, "Respiratory Health Crisis")
    assert impact["primary_category"] == "Public Health"
    assert impact["potential_severity"] in ["Low", "Moderate", "High", "Severe"]

def test_growth_prediction():
    articles = [{"id": f"art-{i}", "title": f"Article {i}"} for i in range(5)]
    preds = forecast_cascade_growth(articles, cascade_score=65.0)
    assert len(preds) == 3
    assert preds[0]["horizon_hours"] == 24
    assert preds[1]["horizon_hours"] == 48
    assert preds[2]["horizon_hours"] == 72
    assert preds[0]["expected_volume"] >= len(articles)

def test_classification_matrix():
    topic = {
        "id": "t1",
        "label": "Breaking Treaty Accord",
        "cascade_score": 75.0,
        "corroboration_score": 80.0,
        "articles": [{}, {}, {}],
        "sources": ["A", "B", "C"]
    }
    classification = classify_topic_in_matrix(topic)
    assert classification["quadrant"] == "Verified Breaking News"

def test_narrative_graph_react_flow_structure():
    articles = [
        {"id": "art-1", "title": "Initial report on summit", "source": "Source A", "published_at": "2026-11-06T00:00:00Z"},
        {"id": "art-2", "title": "Summit expands with climate details", "source": "Source B", "published_at": "2026-11-06T01:00:00Z"}
    ]
    entities = [
        {"article_id": "art-1", "entity_text": "Summit", "entity_type": "EVENT"},
        {"article_id": "art-2", "entity_text": "Summit", "entity_type": "EVENT"}
    ]
    graph = build_react_flow_narrative_graph("topic-1", articles, entities)
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["nodes"][0]["type"] == "customNarrativeNode"
    assert "position" in graph["nodes"][0]

def test_lexical_differences():
    diff = compute_lexical_differences(
        "Earthquake strikes regional coast causing tremors",
        "Earthquake strikes regional coast resulting in tsunami warnings and evacuations"
    )
    assert "earthquake" in diff["retained_terms"]
    assert "tsunami" in diff["new_terms"] or "evacuations" in diff["new_terms"]
