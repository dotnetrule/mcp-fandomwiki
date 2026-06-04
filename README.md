# Fandom Wiki MCP Server

A generic [Model Context Protocol](https://modelcontextprotocol.io/) server for fetching data from any [Fandom](https://www.fandom.com/) wiki.

## Tools

| Tool | Description |
|------|-------------|
| `search_wiki` | Search for articles on any Fandom wiki |
| `get_article` | Fetch the full text of an article |
| `get_article_summary` | Fetch just the intro/summary of an article |
| `list_category_members` | List pages that belong to a category |
| `get_wiki_info` | Get general info and stats about a wiki |

Every tool accepts a `wiki` parameter — the subdomain of the Fandom wiki you want to query:

| Wiki | `wiki` value |
|------|-------------|
| ogame.fandom.com | `"ogame"` |
| minecraft.fandom.com | `"minecraft"` |
| starwars.fandom.com | `"starwars"` |
| leagueoflegends.fandom.com | `"leagueoflegends"` |

## Installation

```bash
pip install .
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install .
```

## Usage

Run the server directly:

```bash
fandom-wiki-mcp
```

Or via the MCP CLI:

```bash
mcp run src/fandom_wiki_mcp/server.py
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "fandom-wiki": {
      "command": "fandom-wiki-mcp"
    }
  }
}
```

Or with `uv` (no global install needed):

```json
{
  "mcpServers": {
    "fandom-wiki": {
      "command": "uvx",
      "args": ["--from", "/path/to/mcp-fandomwiki", "fandom-wiki-mcp"]
    }
  }
}
```

## Example Prompts

- *"Search the OGame wiki for 'Graviton Technology'"*
- *"Get the full article for 'Creeper' from the Minecraft wiki"*
- *"List pages in the 'Ships' category on the Star Wars wiki"*
- *"What stats does the League of Legends wiki have?"*
