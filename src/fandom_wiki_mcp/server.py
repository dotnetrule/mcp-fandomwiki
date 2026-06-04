"""MCP server for fetching data from any Fandom wiki."""

import re
from typing import Any

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("fandom-wiki")

_client = httpx.AsyncClient(
    timeout=30.0,
    headers={"User-Agent": "fandom-wiki-mcp/0.1 (github.com/dotnetrule/mcp-fandomwiki)"},
    follow_redirects=True,
)


def _base(wiki: str) -> str:
    return f"https://{wiki}.fandom.com"


def _mediawiki_url(wiki: str) -> str:
    return f"{_base(wiki)}/api.php"


def _strip_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "sup", "table"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    # Collapse excessive blank lines
    return re.sub(r"\n{3,}", "\n\n", text).strip()


@mcp.tool()
async def search_wiki(wiki: str, query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search for articles on a Fandom wiki.

    Args:
        wiki: Wiki subdomain (e.g. "ogame", "minecraft", "starwars").
        query: Search query string.
        limit: Maximum number of results to return (default 10, max 50).
    """
    limit = min(limit, 50)
    url = f"{_base(wiki)}/api/v1/Search/List"
    params = {"query": query, "limit": limit, "namespaces": "0"}
    resp = await _client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "id": item.get("id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "snippet": _strip_html(item.get("snippet", "")),
        }
        for item in data.get("items", [])
    ]


@mcp.tool()
async def get_article(wiki: str, title: str) -> dict[str, Any]:
    """Fetch the full text content of a wiki article.

    Args:
        wiki: Wiki subdomain (e.g. "ogame", "minecraft", "starwars").
        title: Exact article title.
    """
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts|info",
        "explaintext": "1",
        "inprop": "url",
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
    }
    resp = await _client.get(_mediawiki_url(wiki), params=params)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return {"error": "Article not found"}
    page = pages[0]
    if page.get("missing"):
        return {"error": f"Article '{title}' not found"}
    return {
        "title": page.get("title"),
        "url": page.get("fullurl") or f"{_base(wiki)}/wiki/{page['title'].replace(' ', '_')}",
        "content": page.get("extract", ""),
    }


@mcp.tool()
async def get_article_summary(wiki: str, title: str) -> dict[str, Any]:
    """Fetch just the introductory summary of a wiki article.

    Args:
        wiki: Wiki subdomain (e.g. "ogame", "minecraft", "starwars").
        title: Exact article title.
    """
    params = {
        "action": "query",
        "titles": title,
        "prop": "extracts|info",
        "exintro": "1",
        "explaintext": "1",
        "inprop": "url",
        "redirects": "1",
        "format": "json",
        "formatversion": "2",
    }
    resp = await _client.get(_mediawiki_url(wiki), params=params)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return {"error": "Article not found"}
    page = pages[0]
    if page.get("missing"):
        return {"error": f"Article '{title}' not found"}
    return {
        "title": page.get("title"),
        "url": page.get("fullurl") or f"{_base(wiki)}/wiki/{page['title'].replace(' ', '_')}",
        "summary": page.get("extract", ""),
    }


@mcp.tool()
async def list_category_members(wiki: str, category: str, limit: int = 20) -> dict[str, Any]:
    """List pages that belong to a category on a Fandom wiki.

    Args:
        wiki: Wiki subdomain (e.g. "ogame", "minecraft", "starwars").
        category: Category name, with or without the "Category:" prefix.
        limit: Maximum number of results (default 20, max 500).
    """
    limit = min(limit, 500)
    if not category.lower().startswith("category:"):
        category = f"Category:{category}"
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": category,
        "cmlimit": limit,
        "cmtype": "page",
        "format": "json",
        "formatversion": "2",
    }
    resp = await _client.get(_mediawiki_url(wiki), params=params)
    resp.raise_for_status()
    data = resp.json()
    members = data.get("query", {}).get("categorymembers", [])
    return {
        "category": category,
        "wiki": wiki,
        "count": len(members),
        "pages": [
            {
                "title": m.get("title"),
                "url": f"{_base(wiki)}/wiki/{m['title'].replace(' ', '_')}",
            }
            for m in members
        ],
    }


@mcp.tool()
async def get_wiki_info(wiki: str) -> dict[str, Any]:
    """Get general information about a Fandom wiki.

    Args:
        wiki: Wiki subdomain (e.g. "ogame", "minecraft", "starwars").
    """
    params = {
        "action": "query",
        "meta": "siteinfo",
        "siprop": "general|statistics|namespaces",
        "format": "json",
        "formatversion": "2",
    }
    resp = await _client.get(_mediawiki_url(wiki), params=params)
    resp.raise_for_status()
    data = resp.json()
    query = data.get("query", {})
    general = query.get("general", {})
    stats = query.get("statistics", {})
    return {
        "wiki": wiki,
        "base_url": _base(wiki),
        "name": general.get("sitename"),
        "main_page": general.get("mainpage"),
        "language": general.get("lang"),
        "articles": stats.get("articles"),
        "pages": stats.get("pages"),
        "edits": stats.get("edits"),
        "images": stats.get("images"),
        "users": stats.get("users"),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
