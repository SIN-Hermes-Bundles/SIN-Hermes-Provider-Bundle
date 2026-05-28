import json
import logging
from typing import Any

from tools.registry import registry

logger = logging.getLogger(__name__)

TOOL_SEARCH_SCHEMA = {
    "name": "tool_search",
    "description": (
        "Search for tools by keyword. Returns full tool schemas that you can "
        "then call directly. Use this when you need a tool that isn't already "
        "loaded \u2014 check the tool catalog in your system prompt for available tools."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Search keywords \u2014 tool name, action verb, or what you're "
                    "trying to do (e.g., 'read file', 'search web', 'git')"
                ),
            },
        },
        "required": ["query"],
    },
}

TOOL_DETAILS_SCHEMA = {
    "name": "tool_details",
    "description": (
        "Load the full schema for a specific tool by exact name. "
        "Use when you know which tool you need from the catalog."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Exact tool name from the catalog",
            },
        },
        "required": ["name"],
    },
}

_DEFAULT_MAX_RESULTS = 5
_TOOLSET_NAME = "_tool_search"


def _match_score(query: str, tool_name: str, tool_description: str) -> float:
    query_lower = query.lower()
    name_lower = tool_name.lower()
    desc_lower = tool_description.lower()

    if query_lower == name_lower:
        return 1.0

    score = 0.0

    if query_lower in name_lower:
        score = max(score, 0.8)
    elif name_lower in query_lower:
        score = max(score, 0.7)

    query_words = set(query_lower.replace("_", " ").replace("-", " ").split())
    name_words = set(name_lower.replace("_", " ").replace("-", " ").split())
    desc_words = set(desc_lower.replace("_", " ").replace("-", " ").split())

    if query_words:
        name_overlap = len(query_words & name_words) / len(query_words)
        desc_overlap = len(query_words & desc_words) / len(query_words)
        score = max(score, name_overlap * 0.9, desc_overlap * 0.5)

    return score


def search_tools(args: dict[str, Any], **kwargs) -> str:
    query = args.get("query", "").strip()
    if not query:
        return json.dumps({"error": "query is required", "matched_count": 0, "tools": []})

    catalog = registry.get_catalog()
    scored = []
    for entry in catalog:
        if entry["name"] in ("tool_search", "tool_details"):
            continue
        s = _match_score(query, entry["name"], entry["description"])
        if s > 0.1:
            scored.append((s, entry["name"]))

    scored.sort(key=lambda x: -x[0])
    top_names = [name for _, name in scored[:_DEFAULT_MAX_RESULTS]]

    schemas = []
    for name in top_names:
        schema = registry.get_single_definition(name)
        if schema:
            schemas.append(schema)

    logger.info(
        "tool_search(%r): %d matches from %d catalog entries, returning %d schemas",
        query, len(scored), len(catalog), len(schemas),
    )

    return json.dumps({
        "matched_count": len(schemas),
        "tools": schemas,
        "hint": (
            "These tool schemas are now loaded. You can call them directly "
            "on your next action. If you don't see what you need, try a "
            "different search query."
        ),
    })


def get_tool_details(args: dict[str, Any], **kwargs) -> str:
    name = args.get("name", "").strip()
    if not name:
        return json.dumps({"error": "name is required"})

    schema = registry.get_single_definition(name)
    if not schema:
        return json.dumps({
            "error": f"Tool '{name}' not found or unavailable. "
                     "Use tool_search(query) to find available tools.",
        })

    return json.dumps({"matched_count": 1, "tools": [schema]})


def register_tool_search():
    if registry._tools.get("tool_search"):
        return

    registry.register(
        name="tool_search",
        toolset=_TOOLSET_NAME,
        schema=TOOL_SEARCH_SCHEMA,
        handler=search_tools,
        description="Search for and load tool schemas by keyword",
        emoji="\U0001f50d",
    )
    registry.register(
        name="tool_details",
        toolset=_TOOLSET_NAME,
        schema=TOOL_DETAILS_SCHEMA,
        handler=get_tool_details,
        description="Load full schema for a specific tool by name",
        emoji="\U0001f50d",
    )
