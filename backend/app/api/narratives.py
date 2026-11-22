from fastapi import APIRouter, HTTPException
from ..database.repository import get_topic_by_id, get_topics, get_entities_for_article
from ..services.narrative_service import build_react_flow_narrative_graph

router = APIRouter(prefix="/api/narratives", tags=["Information Narrative Tree"])

@router.get("")
def get_available_narrative_topics():
    topics = get_topics(limit=25)
    return [
        {
            "id": t["id"],
            "label": t["label"],
            "article_count": t.get("article_count", 0),
            "source_count": t.get("source_count", 0),
            "cascade_score": t.get("cascade_score", 0)
        }
        for t in topics
    ]

@router.get("/{topic_id}")
def get_narrative_graph_for_topic(topic_id: str):
    top = get_topic_by_id(topic_id)
    if not top:
        raise HTTPException(status_code=404, detail="Topic not found.")
        
    articles = top.get("articles", [])
    entities = []
    for a in articles:
        entities.extend(get_entities_for_article(a["id"]))
        
    graph = build_react_flow_narrative_graph(topic_id, articles, entities)
    return {
        "topic": {
            "id": top["id"],
            "label": top["label"],
            "cascade_score": top.get("cascade_score", 0),
            "sources": top.get("sources", [])
        },
        **graph
    }

