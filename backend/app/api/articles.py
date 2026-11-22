from fastapi import APIRouter, Query
from typing import Optional
from ..database.repository import get_articles, get_sources

router = APIRouter(prefix="/api", tags=["Articles & Sources"])

@router.get("/articles")
def list_articles(
    limit: int = 100,
    offset: int = 0,
    source: Optional[str] = None,
    search: Optional[str] = None
):
    lim = int(limit) if not hasattr(limit, "default") else 100
    off = int(offset) if not hasattr(offset, "default") else 0
    src = str(source) if source is not None and not hasattr(source, "default") else None
    srch = str(search) if search is not None and not hasattr(search, "default") else None
    items = get_articles(limit=lim, offset=off, source=src, search=srch)
    return {
        "count": len(items),
        "articles": items
    }

@router.get("/sources")
def list_sources():
    sources = get_sources()
    return {
        "count": len(sources),
        "sources": sources
    }
