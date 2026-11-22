import re
from collections import Counter
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Standard English stopwords + journalistic noise words
STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "are", "was", "has", "have", "had",
    "will", "into", "after", "over", "its", "their", "about", "says", "said", "new", "latest",
    "more", "than", "how", "why", "what", "who", "when", "where", "been", "which", "were",
    "would", "could", "should", "also", "some", "other", "them", "then", "just", "both",
    "under", "such", "only", "first", "most", "year", "years", "time", "press", "news",
    "report", "reports", "reported", "update", "live", "amid", "amidst", "near", "today",
    "reuters", "associated", "broadcast", "daily", "alert", "breaking"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s\-\.\,\']", " ", text)
    return " ".join(text.split())

def build_tfidf_similarity(corpus: List[str]) -> Tuple[Any, Any]:
    if not corpus:
        return None, None
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=4000,
            ngram_range=(1, 2),
            min_df=1
        )
        matrix = vectorizer.fit_transform(corpus)
        sim_matrix = cosine_similarity(matrix)
        return vectorizer, sim_matrix
    except Exception:
        return None, None

def extract_keywords(texts: List[str], top_n: int = 7) -> List[str]:
    combined = " ".join(texts).lower()
    words = re.findall(r"\b[a-zA-Z]{4,20}\b", combined)
    filtered = [w for w in words if w not in STOP_WORDS]
    counts = Counter(filtered)
    return [w for w, _ in counts.most_common(top_n)]

# Rule-based and pattern-based Entity Extraction for research context
def extract_entities_from_text(text: str, article_id: str) -> List[Dict[str, Any]]:
    if not text:
        return []
    
    entities = []
    seen = set()

    # 1. Organizations & Institutions (acronyms or capitalized patterns)
    org_pattern = r"\b(?:UN|WHO|NASA|NATO|EU|CDC|FDA|IMF|OPEC|COP\d+|IPCC|USGS|NOAA|WMO|[A-Z][a-z]+ (?:Agency|Department|Ministry|Committee|Council|Organization|Commission|Administration|Institute|Center|Force|Union|Bank|Court))\b"
    for match in re.finditer(org_pattern, text):
        val = match.group(0).strip()
        if val not in seen and len(val) > 2:
            seen.add(val)
            entities.append({
                "article_id": article_id,
                "entity_text": val,
                "entity_type": "ORG",
                "salience": 0.85,
                "context": text[max(0, match.start() - 30):min(len(text), match.end() + 30)].strip()
            })

    # 2. Geopolitical Entities / Locations
    loc_pattern = r"\b(?:United States|United Kingdom|Ukraine|Russia|China|Gaza|Israel|Iran|Lebanon|India|Germany|France|Japan|Syria|Sudan|Taiwan|Washington|London|Kyiv|Moscow|Beijing|Geneva|Brussels|Paris|Tokyo|New Delhi|Jerusalem|Tehran|Pacific|Atlantic|Arctic|Red Sea|Mediterranean)\b"
    for match in re.finditer(loc_pattern, text):
        val = match.group(0).strip()
        if val not in seen:
            seen.add(val)
            entities.append({
                "article_id": article_id,
                "entity_text": val,
                "entity_type": "GPE",
                "salience": 0.80,
                "context": text[max(0, match.start() - 30):min(len(text), match.end() + 30)].strip()
            })

    # 3. Notable Persons / Leaders (Capitalized Title + Surname patterns)
    person_pattern = r"\b(?:President|Prime Minister|Secretary-General|Chancellor|Dr\.|King|Queen)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b"
    for match in re.finditer(person_pattern, text):
        full = match.group(0).strip()
        if full not in seen:
            seen.add(full)
            entities.append({
                "article_id": article_id,
                "entity_text": full,
                "entity_type": "PERSON",
                "salience": 0.75,
                "context": text[max(0, match.start() - 25):min(len(text), match.end() + 25)].strip()
            })

    # 4. Quantities & Metrics (Death tolls, percentages, monetary values)
    quant_pattern = r"\b(?:\$\d+(?:\.\d+)?\s*(?:billion|million|trillion)?|\d+(?:\,\d+)?\s*(?:people|fatalities|casualties|deaths|injuries|percent|%|tonnes|km|miles))\b"
    for match in re.finditer(quant_pattern, text, re.IGNORECASE):
        val = match.group(0).strip()
        if val not in seen:
            seen.add(val)
            entities.append({
                "article_id": article_id,
                "entity_text": val,
                "entity_type": "QUANTITY",
                "salience": 0.70,
                "context": text[max(0, match.start() - 20):min(len(text), match.end() + 20)].strip()
            })

    # 5. Scientific / Environmental / Crisis Events
    event_pattern = r"\b(?:Earthquake|Cyclone|Hurricane|Typhoon|Wildfire|Outbreak|Ceasefire|Summit|Election|Sanctions|Strike|Treaty|Pandemic|Drought|Flood)\b"
    for match in re.finditer(event_pattern, text, re.IGNORECASE):
        val = match.group(0).capitalize()
        if val not in seen:
            seen.add(val)
            entities.append({
                "article_id": article_id,
                "entity_text": val,
                "entity_type": "EVENT",
                "salience": 0.78,
                "context": text[max(0, match.start() - 25):min(len(text), match.end() + 25)].strip()
            })

    return entities

def compute_lexical_differences(text_early: str, text_later: str) -> Dict[str, Any]:
    words_early = set(re.findall(r"\b[a-zA-Z]{4,}\b", text_early.lower())) - STOP_WORDS
    words_later = set(re.findall(r"\b[a-zA-Z]{4,}\b", text_later.lower())) - STOP_WORDS
    
    retained = sorted(list(words_early.intersection(words_later)))
    newly_added = sorted(list(words_later - words_early))
    omitted = sorted(list(words_early - words_later))
    
    overlap_ratio = len(retained) / max(1, len(words_early.union(words_later)))
    
    return {
        "retained_terms": retained[:10],
        "new_terms": newly_added[:10],
        "omitted_terms": omitted[:10],
        "overlap_ratio": round(overlap_ratio, 3)
    }

