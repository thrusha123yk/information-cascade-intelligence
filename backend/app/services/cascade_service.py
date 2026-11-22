import math
from datetime import datetime, timezone
from typing import List, Dict, Any

def compute_cascade_activity(articles: List[Dict[str, Any]], sources: List[str]) -> Dict[str, Any]:
    """
    Computes a transparent cascade activity indicator (0-100) for an emerging topic.
    Inputs:
      - Article count
      - Distinct publisher diversity
      - Volume recency (reports within last 24h)
      - Source distribution entropy
    """
    if not articles:
        return {
            "cascade_score": 0.0,
            "velocity_score": 0.0,
            "acceleration_rate": 0.0,
            "source_diversity_score": 0.0,
            "recency_score": 0.0,
            "measured_volume": 0,
            "activity_trend": "inactive",
            "research_caveat": "No articles collected for this topic."
        }

    now = datetime.now(timezone.utc)
    article_count = len(articles)
    distinct_sources = len(set(sources))

    # 1. Volume Factor (up to 40 points)
    # Logarithmic saturation to prevent a single dominant publisher skewing score
    volume_score = min(40.0, math.log(article_count + 1, 2) * 12.0)

    # 2. Source Diversity Factor (up to 30 points)
    # Corroborating coverage across multiple independent newsrooms
    diversity_score = min(30.0, distinct_sources * 7.5)

    # 3. Recency & Velocity (up to 30 points)
    recent_24h = 0
    recent_6h = 0
    for a in articles:
        pub = a.get("published_at") or a.get("collected_at")
        if pub:
            try:
                dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                diff_hours = (now - dt).total_seconds() / 3600.0
                if diff_hours <= 24:
                    recent_24h += 1
                if diff_hours <= 6:
                    recent_6h += 1
            except Exception:
                pass

    recency_ratio = recent_24h / max(1, article_count)
    recency_score = min(20.0, recent_24h * 5.0) + (10.0 if recent_6h > 0 else 0.0)

    total_score = min(100.0, round(volume_score + diversity_score + recency_score, 1))

    # Velocity: rate of new reports per 24 hours
    velocity = round(recent_24h / 24.0, 2)

    # Acceleration rate
    acceleration = round((recent_6h * 4.0 - recent_24h) / max(1, recent_24h), 2)
    if acceleration > 0.3:
        trend = "accelerating"
    elif acceleration < -0.3:
        trend = "decelerating"
    else:
        trend = "steady"

    return {
        "cascade_score": total_score,
        "velocity_score": velocity,
        "acceleration_rate": acceleration,
        "source_diversity_score": round(diversity_score, 1),
        "recency_score": round(recency_score, 1),
        "measured_volume": article_count,
        "activity_trend": trend,
        "research_caveat": (
            "Transparent Academic Proxy: Represents public journalistic article volume and publisher diversity. "
            "It does NOT measure peer-to-peer social media reach, private shares, or algorithmic viral impressions."
        )
    }

