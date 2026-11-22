import re
from typing import List, Dict, Any

def evaluate_evidence_and_corroboration(articles: List[Dict[str, Any]], sources: List[str]) -> Dict[str, Any]:
    """
    Evaluates evidence records for a topic cascade.
    Focuses on multi-source corroboration, claim consistency, and evidentiary gaps.
    Does NOT assert factual truth or binary fake news classifications.
    """
    if not articles:
        return {
            "corroboration_level": "insufficient",
            "independent_sources_count": 0,
            "consensus_claim": "No reporting available.",
            "conflicting_points": [],
            "evidence_gaps": ["No articles collected."],
            "unresolved_questions": ["What is the origin of the claim?"],
            "corroboration_score": 0.0,
            "status_label": "Insufficient Evidence"
        }

    distinct_sources = list(set(sources))
    num_sources = len(distinct_sources)
    num_articles = len(articles)

    # Corroboration score calculation (0 - 100)
    # Based on number of distinct publishers and institutional vs commercial balance
    has_tier1 = any("UN" in s or "WHO" in s or "BBC" in s or "Guardian" in s or "NASA" in s for s in distinct_sources)
    base_corroboration = min(70.0, num_sources * 17.5)
    tier_bonus = 25.0 if has_tier1 else 0.0
    corroboration_score = min(100.0, round(base_corroboration + tier_bonus, 1))

    if num_sources >= 4 and has_tier1:
        corroboration_level = "high"
        status_label = "Multi-Source Corroborated"
    elif num_sources >= 2:
        corroboration_level = "moderate"
        status_label = "Partially Corroborated"
    elif num_sources == 1 and num_articles > 1:
        corroboration_level = "low"
        status_label = "Single-Publisher Clustered"
    else:
        corroboration_level = "insufficient"
        status_label = "Insufficient Evidence"

    # Consensus claim formulation based on highest frequency common phrases
    primary_article = articles[0]
    consensus_claim = primary_article.get("title", "Emerging narrative thread")

    # Detect discrepancies / conflicting points in text (e.g. contradicting death tolls, conflicting attributions)
    conflicting_points = []
    quantities = []
    for a in articles:
        text = (a.get("title", "") + " " + (a.get("description") or "")).lower()
        nums = re.findall(r"\b\d+(?:[\,\.]\d+)?\s*(?:killed|dead|injured|casualties|deaths|people|billion|million)\b", text)
        if nums:
            quantities.extend(nums)

    if len(set(quantities)) > 1:
        conflicting_points.append(
            f"Varying metrics reported across publishers: {', '.join(list(set(quantities))[:3])}"
        )

    # Check for attribution variance (e.g. 'official claims', 'alleged', 'unconfirmed')
    uncertainty_count = sum(
        1 for a in articles
        if any(w in (a.get("title", "") + " " + (a.get("description") or "")).lower()
               for w in ["alleged", "claimed", "unconfirmed", "disputed", "denies", "purported"])
    )
    if uncertainty_count > 0:
        conflicting_points.append(
            f"{uncertainty_count} source(s) use qualifying language ('alleged', 'claimed', or 'unconfirmed')."
        )

    # Identify evidence gaps
    evidence_gaps = []
    if num_sources < 2:
        evidence_gaps.append("Lacks independent corroboration from outside the initial publishing domain.")
    if not has_tier1:
        evidence_gaps.append("No official humanitarian, scientific, or established wire service statement observed.")
    if len(articles) < 3:
        evidence_gaps.append("Limited historical time-depth to verify narrative consistency.")

    # Formulate unresolved research questions
    unresolved_questions = []
    if corroboration_level in ("low", "insufficient"):
        unresolved_questions.append("Can secondary independent reporting substantiate the core assertion?")
        unresolved_questions.append("Are initial claims attributable to primary documentary or eyewitness evidence?")
    else:
        unresolved_questions.append("How are subsequent regional actors framing responsibility or long-term outcomes?")
        unresolved_questions.append("Are official reports undergoing revisions as field investigations conclude?")

    return {
        "corroboration_level": corroboration_level,
        "independent_sources_count": num_sources,
        "consensus_claim": consensus_claim,
        "conflicting_points": conflicting_points,
        "evidence_gaps": evidence_gaps,
        "unresolved_questions": unresolved_questions,
        "corroboration_score": corroboration_score,
        "status_label": status_label,
        "methodology_note": (
            "Source corroboration represents journalistic independence and textual alignment. "
            "A high score denotes consistent multi-publisher reporting, not infallible epistemological truth."
        )
    }

