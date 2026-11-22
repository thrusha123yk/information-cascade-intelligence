import re
from typing import List, Dict, Any

# Domain keywords mapping for explainable research impact categorization
DOMAIN_PATTERNS = {
    "Public Health": [
        "health", "outbreak", "virus", "disease", "vaccine", "hospital", "who", "pandemic",
        "medical", "flu", "epidemic", "infection", "cancer", "sanitation", "water", "mental health"
    ],
    "Environment": [
        "climate", "emissions", "wildfire", "weather", "warming", "carbon", "cyclone", "hurricane",
        "flood", "drought", "biodiversity", "ocean", "pollution", "glacier", "renewable", "earthquake"
    ],
    "Public Safety": [
        "security", "attack", "safety", "conflict", "blast", "evacuation", "military", "police",
        "emergency", "hazard", "threat", "disaster", "strike", "defense", "casualty"
    ],
    "Economy": [
        "market", "inflation", "trade", "jobs", "rates", "banking", "prices", "stocks", "tariff",
        "supply chain", "currency", "debt", "growth", "energy", "oil", "cost of living"
    ],
    "Government & Public Policy": [
        "government", "election", "parliament", "law", "court", "policy", "sanctions", "treaty",
        "diplomacy", "minister", "president", "vote", "regulation", "rights", "un", "bill"
    ],
    "Technology & Society": [
        "ai", "artificial intelligence", "cyber", "internet", "social media", "privacy", "algorithm",
        "data", "space", "telecom", "automation", "surveillance", "semiconductor", "biotech"
    ]
}

def assess_social_impact(articles: List[Dict[str, Any]], topic_label: str) -> Dict[str, Any]:
    """
    Evaluates potential societal impact across 6 research domains.
    Provides severity, urgency, evidentiary explanation, and identifies affected populations/regions.
    """
    combined_text = (topic_label + " " + " ".join([
        (a.get("title", "") + " " + (a.get("description") or "")) for a in articles
    ])).lower()

    # Domain scoring
    scores = {}
    for domain, kws in DOMAIN_PATTERNS.items():
        score = sum(len(re.findall(rf"\b{kw}\b", combined_text)) for kw in kws)
        scores[domain] = score

    sorted_domains = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_category = sorted_domains[0][0] if sorted_domains[0][1] > 0 else "Government & Public Policy"

    # Detect high severity keywords
    high_sev_words = ["fatal", "catastrophic", "emergency", "crisis", "state of emergency", "casualties", "collapse", "severe", "threat", "disaster"]
    high_count = sum(1 for w in high_sev_words if w in combined_text)
    
    if high_count >= 3 or len(articles) >= 6:
        potential_severity = "High"
        urgency_level = "Immediate"
    elif high_count >= 1 or len(articles) >= 3:
        potential_severity = "Moderate"
        urgency_level = "Developing"
    else:
        potential_severity = "Low"
        urgency_level = "Monitored"

    # Identify affected geographic areas or populations strictly from evidence
    locations = set()
    for a in articles:
        if a.get("location") and a["location"] not in ("Global", "International"):
            locations.add(a["location"])
        # Simple extraction from title
        for loc in ["Ukraine", "Gaza", "Lebanon", "Sudan", "United States", "Europe", "Asia", "India", "China", "United Kingdom", "Pacific"]:
            if loc.lower() in (a.get("title", "") + " " + (a.get("description") or "")).lower():
                locations.add(loc)

    affected_area = ", ".join(list(locations)[:3]) if locations else "Global / Multi-regional"
    affected_population = f"Communities within {affected_area}" if locations else "General public / international stakeholders"

    # Formulate transparent research rationale
    supporting_sources = list({a.get("source") for a in articles if a.get("source")})
    rationale = (
        f"Assessed as '{primary_category}' based on frequent co-occurrence of domain descriptors across {len(articles)} reports. "
        f"Potential severity is evaluated as '{potential_severity}' (urgency: {urgency_level}) due to observed discussion of "
        f"{'critical safety/operational hazards' if high_count > 0 else 'developing socio-economic developments'}. "
        f"Corroborating coverage is cited by: {', '.join(supporting_sources[:4])}."
    )

    return {
        "primary_category": primary_category,
        "potential_severity": potential_severity,
        "urgency_level": urgency_level,
        "affected_population": affected_population,
        "affected_area": affected_area,
        "rationale": rationale,
        "supporting_sources": supporting_sources,
        "all_category_relevance": {k: min(100, v * 20) for k, v in scores.items()},
        "research_disclaimer": "Potential impact represents qualitative research categorization, not an emergency directive or official safety advisory."
    }

