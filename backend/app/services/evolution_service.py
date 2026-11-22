from datetime import datetime
from typing import List, Dict, Any
from .nlp_service import compute_lexical_differences

def analyze_information_evolution(articles: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes temporal and semantic evolution of information across reports.
    Identifies newly introduced vs persistent entities, lexical drift, and claim shifts.
    """
    if not articles:
        return {"timeline": [], "evolution_summary": "Insufficient data to analyze evolution."}

    # Sort articles chronologically
    sorted_articles = sorted(
        articles,
        key=lambda a: (a.get("published_at") or a.get("collected_at") or "")
    )

    entities_by_article = {}
    for ent in entities:
        entities_by_article.setdefault(ent.get("article_id"), []).append(ent)

    timeline_steps = []
    accumulated_entities = set()
    initial_text = (sorted_articles[0].get("title", "") + " " + (sorted_articles[0].get("description") or ""))

    for idx, art in enumerate(sorted_articles):
        aid = art["id"]
        art_ents = entities_by_article.get(aid, [])
        current_ent_texts = set(e["entity_text"] for e in art_ents)
        
        newly_appearing_entities = list(current_ent_texts - accumulated_entities)
        persistent_entities = list(current_ent_texts.intersection(accumulated_entities))
        
        current_text = (art.get("title", "") + " " + (art.get("description") or ""))
        lex_diff = compute_lexical_differences(initial_text, current_text)

        # Distinguish research verification tiers
        if idx == 0:
            evidence_classification = "Confirmed Textual Baseline"
            notes = "Original observed report defining the initial vocabulary and scope."
        elif len(newly_appearing_entities) > 0 and lex_diff["overlap_ratio"] < 0.6:
            evidence_classification = "Confirmed Textual Difference"
            notes = f"Novel claims introduced. Added entities: {', '.join(newly_appearing_entities[:3])}"
        elif lex_diff["overlap_ratio"] >= 0.6:
            evidence_classification = "Similarity-Based Relationship"
            notes = "High lexical consistency with primary narrative thread; consistent framing."
        else:
            evidence_classification = "Unverified Interpretation"
            notes = "Significant lexical drift observed; secondary interpretations emerging."

        step = {
            "step_index": idx + 1,
            "article_id": aid,
            "title": art["title"],
            "source": art.get("source", "Unknown"),
            "published_at": art.get("published_at") or art.get("collected_at"),
            "url": art.get("url"),
            "newly_appearing_entities": newly_appearing_entities,
            "persistent_entities": persistent_entities,
            "new_terms": lex_diff["new_terms"],
            "retained_terms": lex_diff["retained_terms"],
            "overlap_ratio": lex_diff["overlap_ratio"],
            "evidence_classification": evidence_classification,
            "analysis_notes": notes
        }
        timeline_steps.append(step)
        accumulated_entities.update(current_ent_texts)

    return {
        "total_steps": len(timeline_steps),
        "initial_report": sorted_articles[0]["title"],
        "latest_report": sorted_articles[-1]["title"],
        "all_accumulated_entities": list(accumulated_entities),
        "timeline": timeline_steps,
        "methodology_note": (
            "Temporal evolution tracks explicit textual delta and entity emergence across verified publisher timestamps. "
            "It differentiates verified textual diffs from hypothetical narrative drift."
        )
    }

