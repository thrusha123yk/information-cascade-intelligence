from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Simple whitelist to filter out generic categories and non-countries
# In a full-scale app, we would use a more robust geonames/ISO database
VALID_COUNTRIES = {
    "United States": "US", "USA": "US", "United Kingdom": "GB", "UK": "GB",
    "India": "IN", "China": "CN", "Russia": "RU", "Germany": "DE",
    "France": "FR", "Japan": "JP", "Canada": "CA", "Australia": "AU",
    "Brazil": "BR", "Ukraine": "UA", "Israel": "IL", "Gaza": "PS",
    "Iran": "IR", "Sudan": "SD", "Syria": "SY", "Russia": "RU", "Russian": "RU"
}

CANONICAL_COUNTRIES = {
    "USA": "United States",
    "UK": "United Kingdom",
    "Gaza": "Palestine",
    "Russian": "Russia",
}

def extract_event_country(text: str) -> Dict[str, Any]:
    if not text:
        return {"country": "Unknown", "confidence": 0.0}

    normalized = f" {text.lower()} "
    found = {}
    for country, code in VALID_COUNTRIES.items():
        if f" {country.lower()} " in normalized or (
            country == "United States" and " u.s. " in normalized
        ):
            canonical = CANONICAL_COUNTRIES.get(country, country)
            found[canonical] = found.get(canonical, 0) + normalized.count(
                f" {country.lower()} "
            )

    if not found:
        return {"country": "Unknown", "confidence": 0.0}

    best_country = max(found, key=found.get)
    confidence = min(1.0, found[best_country] / 5.0) # Heuristic confidence

    return {
        "country": best_country,
        "confidence": round(confidence, 2)
    }
