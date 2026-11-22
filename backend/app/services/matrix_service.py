from typing import List, Dict, Any

def classify_topic_in_matrix(topic: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classifies a topic into the 2x2 Research Information Classification Matrix:
      1. Verified Breaking News (Cascade Activity >= 50, Corroboration >= 50)
      2. Niche Fact (Cascade Activity < 50, Corroboration >= 50)
      3. Isolated Rumor / Unverified Thread (Cascade Activity < 50, Corroboration < 50)
      4. High-Cascade Uncorroborated / Potential Viral Disinformation (Cascade Activity >= 50, Corroboration < 50)
    """
    cascade_score = float(topic.get("cascade_score", 0))
    corroboration_score = float(topic.get("corroboration_score", 0))

    if cascade_score >= 50 and corroboration_score >= 50:
        quadrant = "Verified Breaking News"
        description = "High journalistic cascade activity validated by multi-source institutional corroboration."
        color_tone = "blue"
    elif cascade_score < 50 and corroboration_score >= 50:
        quadrant = "Niche Fact"
        description = "Supported by reliable independent sources, but with localized or specialized coverage."
        color_tone = "lavender"
    elif cascade_score < 50 and corroboration_score < 50:
        quadrant = "Isolated Rumor"
        description = "Low activity, single-source reporting with unverified evidentiary backing."
        color_tone = "yellow"
    else:
        quadrant = "Viral Disinformation"
        description = (
            "Rapid cascade expansion with severe deficit in independent multi-source corroboration. "
            "Requires critical evidentiary verification."
        )
        color_tone = "pink"

    return {
        "topic_id": topic["id"],
        "label": topic["label"],
        "cascade_score": cascade_score,
        "corroboration_score": corroboration_score,
        "quadrant": quadrant,
        "description": description,
        "color_tone": color_tone,
        "article_count": topic.get("article_count", len(topic.get("articles", []))),
        "source_count": topic.get("source_count", len(topic.get("sources", []))),
        "criteria": {
            "activity_threshold": 50.0,
            "corroboration_threshold": 50.0,
            "measured_activity": cascade_score,
            "measured_corroboration": corroboration_score
        }
    }

def build_matrix_overview(topics: List[Dict[str, Any]]) -> Dict[str, Any]:
    quadrants = {
        "Verified Breaking News": [],
        "Niche Fact": [],
        "Isolated Rumor": [],
        "Viral Disinformation": []
    }
    
    for t in topics:
        c = classify_topic_in_matrix(t)
        quadrants[c["quadrant"]].append(c)

    return {
        "quadrants": quadrants,
        "total_classified": len(topics),
        "research_caveat": (
            "Academic Classification Taxonomy: High activity with low corroboration is categorized for heightened "
            "evidentiary review. It does not constitute a legal or factual adjudication of deliberate falsehood."
        )
    }

