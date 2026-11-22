from typing import List, Dict, Any, Optional
from ..database.repository import get_topics, get_articles

def search_information_ecosystem(
    query: Optional[str] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    min_cascade_score: Optional[float] = None
) -> Dict[str, Any]:
    topics = get_topics(limit=200)
    all_articles = get_articles(limit=500)
    
    clean_q = (query or "").strip().lower()
    clean_src = (source or "").strip().lower()

    filtered_topics = []
    for t in topics:
        match_q = True
        if clean_q:
            in_label = clean_q in t["label"].lower()
            in_desc = clean_q in t.get("description", "").lower()
            in_kws = any(clean_q in kw.lower() for kw in t.get("keywords", []))
            match_q = in_label or in_desc or in_kws

        match_src = True
        if clean_src:
            match_src = any(clean_src in s.lower() for s in t.get("sources", []))

        match_score = True
        if min_cascade_score is not None:
            match_score = float(t.get("cascade_score", 0)) >= min_cascade_score

        if match_q and match_src and match_score:
            filtered_topics.append(t)

    # Filter articles
    filtered_articles = []
    if clean_q or clean_src:
        for a in all_articles:
            art_match_q = True
            if clean_q:
                art_match_q = clean_q in a["title"].lower() or clean_q in (a.get("description") or "").lower()
            art_match_src = True
            if clean_src:
                art_match_src = clean_src in (a.get("source") or "").lower()
            if art_match_q and art_match_src:
                filtered_articles.append(a)

    return {
        "topics": filtered_topics,
        "articles": filtered_articles[:50],
        "total_topic_matches": len(filtered_topics),
        "total_article_matches": len(filtered_articles)
    }

def compare_two_topics(topic_id_a: str, topic_id_b: str) -> Optional[Dict[str, Any]]:
    topics = get_topics(limit=500)
    topic_a = next((t for t in topics if t["id"] == topic_id_a), None)
    topic_b = next((t for t in topics if t["id"] == topic_id_b), None)
    
    if not topic_a or not topic_b:
        return None

    # Compare metrics
    shared_sources = list(set(topic_a.get("sources", [])).intersection(set(topic_b.get("sources", []))))
    shared_keywords = list(set(topic_a.get("keywords", [])).intersection(set(topic_b.get("keywords", []))))

    return {
        "topic_a": topic_a,
        "topic_b": topic_b,
        "comparison": {
            "cascade_score_diff": round(float(topic_a.get("cascade_score", 0)) - float(topic_b.get("cascade_score", 0)), 1),
            "corroboration_score_diff": round(float(topic_a.get("corroboration_score", 0)) - float(topic_b.get("corroboration_score", 0)), 1),
            "volume_diff": topic_a.get("article_count", 0) - topic_b.get("article_count", 0),
            "shared_sources": shared_sources,
            "shared_keywords": shared_keywords
        }
    }

