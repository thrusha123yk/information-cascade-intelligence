from typing import List, Dict, Any

def build_react_flow_narrative_graph(topic_id: str, articles: List[Dict[str, Any]], entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Constructs an interactive narrative tree graph structure formatted specifically for React Flow.
    Generates nodes and labeled edges representing chronological and evidentiary relationships.
    """
    if not articles:
        return {"nodes": [], "edges": [], "summary": "No articles available for narrative construction."}

    # Sort articles chronologically by published_at or collected_at
    sorted_articles = sorted(
        articles,
        key=lambda a: (a.get("published_at") or a.get("collected_at") or "")
    )

    nodes = []
    edges = []

    # Map entities to article_ids
    entities_by_article = {}
    for ent in entities:
        aid = ent.get("article_id")
        entities_by_article.setdefault(aid, []).append(ent)

    # Initial report (root node)
    root_art = sorted_articles[0]
    root_id = root_art["id"]
    root_entities = entities_by_article.get(root_id, [])

    nodes.append({
        "id": root_id,
        "type": "customNarrativeNode",
        "position": {"x": 250, "y": 40},
        "data": {
            "title": root_art["title"],
            "publisher": root_art.get("source", "Unknown Source"),
            "published_at": root_art.get("published_at") or root_art.get("collected_at"),
            "url": root_art.get("url"),
            "node_type": "initial_report",
            "badge": "Initial Discovery",
            "origin": root_art.get("origin", "RSS"),
            "entities": [e["entity_text"] for e in root_entities[:5]],
            "description": (root_art.get("description") or "")[:200]
        }
    })

    # Subsequent articles branched from root or preceding updates
    parent_id = root_id
    y_step = 140
    x_offsets = [-260, 0, 260]

    for idx, art in enumerate(sorted_articles[1:], start=1):
        art_id = art["id"]
        art_entities = entities_by_article.get(art_id, [])
        art_ent_names = set(e["entity_text"] for e in art_entities)
        root_ent_names = set(e["entity_text"] for e in root_entities)

        # Classify relationship
        shared_ents = art_ent_names.intersection(root_ent_names)
        new_ents = art_ent_names - root_ent_names

        is_different_source = art.get("source") != root_art.get("source")
        
        if len(new_ents) > 1:
            rel_type = "adds_details"
            edge_label = "Adds New Findings"
            badge = "Detailed Expansion"
            node_type = "expansion"
        elif idx == len(sorted_articles) - 1 and len(sorted_articles) > 2:
            rel_type = "reports_update"
            edge_label = "Reports Update"
            badge = "Latest Update"
            node_type = "update"
        elif is_different_source and len(shared_ents) > 0:
            rel_type = "corroborates"
            edge_label = "Corroborates Report"
            badge = "Cross-Publisher Corroboration"
            node_type = "corroboration"
        else:
            rel_type = "divergent_claim"
            edge_label = "Related Narrative Variant"
            badge = "Narrative Variant"
            node_type = "variant"

        col = (idx - 1) % 3
        row = (idx - 1) // 3 + 1
        pos_x = 250 + x_offsets[col]
        pos_y = 40 + (row * y_step)

        nodes.append({
            "id": art_id,
            "type": "customNarrativeNode",
            "position": {"x": pos_x, "y": pos_y},
            "data": {
                "title": art["title"],
                "publisher": art.get("source", "Unknown Source"),
                "published_at": art.get("published_at") or art.get("collected_at"),
                "url": art.get("url"),
                "node_type": node_type,
                "badge": badge,
                "origin": art.get("origin", "RSS"),
                "entities": [e["entity_text"] for e in art_entities[:5]],
                "description": (art.get("description") or "")[:200]
            }
        })

        # Connect edge from root or last update
        edges.append({
            "id": f"e-{root_id}-{art_id}",
            "source": root_id,
            "target": art_id,
            "label": edge_label,
            "animated": node_type in ("update", "corroboration"),
            "data": {
                "relationship_type": rel_type,
                "shared_entities_count": len(shared_ents)
            }
        })

    return {
        "topic_id": topic_id,
        "nodes": nodes,
        "edges": edges,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "root_article_id": root_id,
        "summary": f"Narrative tree of {len(nodes)} reports mapped across {len(set(a.get('source') for a in articles))} publishers."
    }

