"""Agno Deal Finder — an agent that maps sites and finds the best deals.

Combines Agno agent framework with BabelWrap's site mapping feature.
The agent maps an e-commerce site, discovers its auto-generated tools,
then uses those tools to find and compare deals.
"""

import json
import os
import sys

from agno.agent import Agent
from agno.models.anthropic import Claude
from babelwrap import BabelWrap, BabelWrapError

# --- BabelWrap setup ---

_bw = BabelWrap(api_key=os.environ["BABELWRAP_API_KEY"])
_mapped_sites: dict[str, str] = {}  # url -> site_id cache
_discovered_tools: dict[str, list] = {}  # site_id -> tools list


# --- Mapping tools ---

def map_website(url: str) -> str:
    """Map a website to discover its structure and auto-generate tools.
    BabelWrap will explore the site and create callable tools for browsing,
    searching, and extracting data. This may take a minute for new sites."""
    try:
        # Check if already mapped
        sites = _bw.list_sites()
        for site in sites if isinstance(sites, list) else []:
            site_url = site.get("start_url", site.get("url", ""))
            if url.replace("https://", "").replace("http://", "") in site_url:
                site_id = site.get("site_id") or site.get("id")
                _mapped_sites[url] = site_id
                return f"Site already mapped! Site ID: {site_id}. Use list_site_tools to see available tools."

        result = _bw.map_site(url)
        site_id = result.get("site_id") or result.get("id")
        _mapped_sites[url] = site_id
        return f"Site mapped successfully! Site ID: {site_id}. Use list_site_tools to see what tools were generated."
    except BabelWrapError as e:
        return f"Mapping error: {e.message}"


def list_site_tools(site_id: str) -> str:
    """List all auto-generated tools for a mapped site. Each tool has a name,
    description, and parameters that you can call with use_site_tool."""
    try:
        resp = _bw.site_tools(site_id)
        tools = resp.get("tools", resp) if isinstance(resp, dict) else resp
        if isinstance(tools, list):
            _discovered_tools[site_id] = tools
            lines = [f"Found {len(tools)} tools for site {site_id}:\n"]
            for t in tools:
                name = t.get("name", "unknown")
                desc = t.get("description", "")
                params = t.get("params", t.get("parameters", {}))
                lines.append(f"  - {name}: {desc}")
                if params:
                    lines.append(f"    Parameters: {json.dumps(params)}")
            return "\n".join(lines)
        return f"Tools response: {json.dumps(tools, indent=2)}"
    except BabelWrapError as e:
        return f"Error listing tools: {e.message}"


def use_site_tool(site_id: str, tool_name: str, params_json: str = "{}") -> str:
    """Execute a generated tool on a mapped site.
    Pass the site_id, the tool name (from list_site_tools), and parameters as a JSON string.
    Example: use_site_tool("abc123", "search_books", '{"query": "science"}')"""
    try:
        params = json.loads(params_json)
        result = _bw.execute_tool(site_id, tool_name, params)
        data = result.get("data", result.get("result", result))
        return json.dumps(data, indent=2)
    except json.JSONDecodeError:
        return f"Error: Invalid JSON for params: {params_json}"
    except BabelWrapError as e:
        return f"Tool execution error: {e.message}"


# --- Manual browsing tools (fallback) ---

_session = None


def open_browser(url: str) -> str:
    """Open a browser and navigate to a URL. Use this for manual browsing
    when mapped tools aren't enough."""
    global _session
    try:
        _session = _bw.create_session()
        snap = _session.navigate(url)
        return _format_page(snap)
    except BabelWrapError as e:
        return f"Browser error: {e.message}"


def browse_click(target: str) -> str:
    """Click an element in the browser. Describe what to click in natural language."""
    if not _session:
        return "Error: Open a browser first."
    try:
        snap = _session.click(target)
        return _format_page(snap)
    except BabelWrapError as e:
        return f"Click error: {e.message}"


def browse_extract(query: str) -> str:
    """Extract structured data from the current browser page."""
    if not _session:
        return "Error: Open a browser first."
    try:
        data = _session.extract(query)
        return json.dumps(data, indent=2)
    except BabelWrapError as e:
        return f"Extract error: {e.message}"


def batch_actions(actions_json: str) -> str:
    """Execute multiple browser actions in a single call for efficiency.
    Pass a JSON array of actions, each with 'action' and optional 'target', 'value' fields.
    Example: [{"action": "click", "target": "checkbox 1"}, {"action": "click", "target": "checkbox 2"}]
    Actions: navigate, click, fill, submit, extract, scroll."""
    if not _session:
        return "Error: Open a browser first."
    try:
        actions = json.loads(actions_json)
        result = _session.batch(actions, continue_on_error=True)
        # Format batch results
        steps = result.get("results", [])
        lines = [f"Batch executed {len(steps)} actions:"]
        for i, step in enumerate(steps):
            status = "OK" if step.get("success") else "FAILED"
            error = f" — {step.get('error', '')}" if not step.get("success") else ""
            lines.append(f"  Step {i+1}: {status}{error}")
        return "\n".join(lines)
    except json.JSONDecodeError:
        return f"Error: Invalid JSON: {actions_json}"
    except BabelWrapError as e:
        return f"Batch error: {e.message}"


def close_browser() -> str:
    """Close the browser session."""
    global _session
    if _session:
        _session.close()
        _session = None
    return "Browser closed."


def _format_page(snap) -> str:
    """Format a browser snapshot into a readable string for the agent."""
    parts = [f"Page: {snap.title}", f"URL: {snap.url}"]
    if snap.content:
        parts.append(f"\nContent: {snap.content[:500]}...")
    if snap.actions:
        parts.append("\nActions:")
        for a in snap.actions[:10]:
            parts.append(f"  - {a.label} [{a.type}]")
    return "\n".join(parts)


# --- Agent ---

INSTRUCTIONS = [
    "You are a deal-finding agent. You help users find the best prices and deals on websites.",
    "",
    "Your superpowers:",
    "1. MAP websites — BabelWrap will explore a site and auto-generate tools for it",
    "2. USE generated tools — browse categories, search products, get details, all via simple tool calls",
    "3. COMPARE — analyze prices across categories to find the best value",
    "",
    "Preferred workflow:",
    "1. Map the website(s) the user mentions",
    "2. List the generated tools to see what's available",
    "3. Use generated tools to browse categories and collect prices",
    "4. Analyze and compare to find the best deals",
    "5. Present findings with specific prices and recommendations",
    "",
    "Use mapped site tools whenever possible — they're faster and more reliable than manual browsing.",
    "Fall back to manual browser tools only if mapped tools don't cover what you need.",
    "",
    "When you need to perform multiple quick actions in sequence, use batch_actions",
    "for efficiency — it executes all actions in one API call instead of many.",
]


def create_deal_finder() -> Agent:
    """Create and return the deal-finding agent."""
    return Agent(
        name="Deal Finder",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[
            # Mapping tools (primary)
            map_website,
            list_site_tools,
            use_site_tool,
            # Manual browsing tools (fallback)
            open_browser,
            browse_click,
            browse_extract,
            batch_actions,
            close_browser,
        ],
        instructions=INSTRUCTIONS,
        markdown=True,
    )


# --- Main ---

def main():
    if "BABELWRAP_API_KEY" not in os.environ:
        print("Error: BABELWRAP_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    agent = create_deal_finder()

    task = sys.argv[1] if len(sys.argv) > 1 else (
        "Map https://www.saucedemo.com to discover its tools. "
        "Then use the generated tools to browse products and find the cheapest item. "
        "Also demonstrate the batch_actions tool by opening a browser to saucedemo.com, "
        "logging in (username: standard_user, password: secret_sauce), and then using "
        "batch to click 'Add to cart' on multiple products in one call."
    )

    print(f"Task: {task}\n")

    try:
        agent.print_response(task, stream=True)
    finally:
        if _session:
            _session.close()
        _bw.close()


if __name__ == "__main__":
    main()
