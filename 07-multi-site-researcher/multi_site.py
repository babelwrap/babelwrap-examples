"""Multi-Site Researcher — Claude agent that maps and researches across multiple websites.

Maps several websites using BabelWrap's site mapping feature, then uses
the auto-generated tools along with manual browsing to research a topic
across all mapped sites.
"""

import base64
import json
import os
import sys
from pathlib import Path

import anthropic
from babelwrap import BabelWrap, BabelWrapError

# --- BabelWrap setup ---

bw = BabelWrap(api_key=os.environ["BABELWRAP_API_KEY"])
session = None
mapped_sites: dict[str, str] = {}  # url -> site_id

# --- Tool definitions ---

TOOLS = [
    # Site mapping tools
    {
        "name": "map_site",
        "description": "Map a website so BabelWrap auto-generates tools for it. This explores the site's structure and creates callable tools. May take a minute for new sites. Returns the site_id needed for other mapping tools.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "The website URL to map, e.g. 'https://books.toscrape.com'"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "list_tools",
        "description": "List all auto-generated tools available for a mapped site. Shows tool names, descriptions, and parameters.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "The site ID returned by map_site"}
            },
            "required": ["site_id"],
        },
    },
    {
        "name": "run_tool",
        "description": "Execute a generated tool on a mapped site. Returns structured data from the site.",
        "input_schema": {
            "type": "object",
            "properties": {
                "site_id": {"type": "string", "description": "The site ID"},
                "tool_name": {"type": "string", "description": "Name of the tool to execute"},
                "params": {"type": "object", "description": "Parameters for the tool (varies by tool)", "default": {}},
            },
            "required": ["site_id", "tool_name"],
        },
    },
    # Manual browsing tools
    {
        "name": "browse",
        "description": "Open a browser and navigate to a URL. Use for manual browsing when mapped tools aren't sufficient. Returns the page snapshot.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"}
            },
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click an element in the browser. Describe what to click.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Natural language description of what to click"}
            },
            "required": ["target"],
        },
    },
    {
        "name": "extract",
        "description": "Extract structured data from the current browser page.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "What to extract in natural language"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "scroll_down",
        "description": "Scroll the current page down to see more content.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "close_browser",
        "description": "Close the browser session.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    # Screenshot and cookie tools
    {
        "name": "screenshot",
        "description": "Take a screenshot of the current page and save it as a PNG. Use for visual evidence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Short name for the screenshot file"}
            },
            "required": ["name"],
        },
    },
    {
        "name": "get_cookies",
        "description": "Get all cookies from the current browser session. Use after logging in to save auth cookies for reuse.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "new_session_with_cookies",
        "description": "Create a new browser session with previously saved cookies. Use to restore authentication without logging in again.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cookies_json": {"type": "string", "description": "JSON string of cookies from get_cookies"}
            },
            "required": ["cookies_json"],
        },
    },
]

# --- Helpers ---


def _save_screenshot(b64_data: str, filename: str) -> None:
    out_dir = Path("screenshots")
    out_dir.mkdir(exist_ok=True)
    (out_dir / filename).write_bytes(base64.b64decode(b64_data))


# --- Tool execution ---


def execute_tool(name: str, input: dict) -> str:
    global session

    try:
        # Mapping tools
        if name == "map_site":
            url = input["url"]
            # Check if already mapped
            sites = bw.list_sites()
            for s in sites if isinstance(sites, list) else []:
                site_url = s.get("start_url", s.get("url", ""))
                domain = url.replace("https://", "").replace("http://", "")
                if domain in site_url:
                    site_id = s.get("site_id") or s.get("id")
                    mapped_sites[url] = site_id
                    return f"Site already mapped. Site ID: {site_id}"

            result = bw.map_site(url)
            site_id = result.get("site_id") or result.get("id")
            mapped_sites[url] = site_id
            return f"Site mapped! Site ID: {site_id}. Use list_tools to see generated tools."

        elif name == "list_tools":
            resp = bw.site_tools(input["site_id"])
            tools = resp.get("tools", resp) if isinstance(resp, dict) else resp
            if isinstance(tools, list):
                lines = [f"Available tools ({len(tools)}):"]
                for t in tools:
                    lines.append(f"  - {t.get('name')}: {t.get('description', '')}")
                    params = t.get("params", t.get("parameters"))
                    if params:
                        lines.append(f"    Params: {json.dumps(params)}")
                return "\n".join(lines)
            return json.dumps(tools, indent=2)

        elif name == "run_tool":
            result = bw.execute_tool(
                input["site_id"],
                input["tool_name"],
                input.get("params", {}),
            )
            data = result.get("data", result.get("result", result))
            output = json.dumps(data, indent=2)
            if len(output) > 3000:
                output = output[:3000] + "\n... (truncated)"
            return output

        # Manual browsing tools
        elif name == "browse":
            if session is None:
                session = bw.create_session()
            snap = session.navigate(input["url"])
            return format_snapshot(snap)

        elif name == "click":
            if session is None:
                return "Error: Browse to a page first."
            snap = session.click(input["target"])
            return format_snapshot(snap)

        elif name == "extract":
            if session is None:
                return "Error: Browse to a page first."
            data = session.extract(input["query"])
            return json.dumps(data, indent=2)

        elif name == "scroll_down":
            if session is None:
                return "Error: Browse to a page first."
            snap = session.scroll("down")
            return format_snapshot(snap)

        elif name == "close_browser":
            if session:
                session.close()
                session = None
            return "Browser closed."

        elif name == "screenshot":
            if session is None:
                return "Error: Browse to a page first."
            img = session.screenshot()
            fname = input["name"].replace(" ", "-") + ".png"
            _save_screenshot(img, fname)
            return f"Screenshot saved: screenshots/{fname}"

        elif name == "get_cookies":
            if session is None:
                return "Error: No active session."
            # Use the underlying httpx client to call the cookies endpoint
            resp = bw._client.get(f"/sessions/{session.session_id}/cookies")
            from babelwrap.sdk import _check_response
            data = _check_response(resp)
            cookies_list = data.get("cookies", [])
            return json.dumps(cookies_list)

        elif name == "new_session_with_cookies":
            cookies = json.loads(input["cookies_json"])
            session = bw.create_session(cookies=cookies)
            return f"New session created with {len(cookies)} cookies: {session.session_id}"

        return f"Unknown tool: {name}"

    except BabelWrapError as e:
        return f"BabelWrap error: [{e.code}] {e.message}"
    except Exception as e:
        return f"Error: {e}"


def format_snapshot(snap) -> str:
    parts = [f"Page: {snap.title}", f"URL: {snap.url}"]
    if snap.content:
        text = snap.content[:600]
        if len(snap.content) > 600:
            text += "..."
        parts.append(f"\nContent: {text}")
    if snap.navigation:
        parts.append(f"\nNav: {', '.join(snap.navigation[:8])}")
    if snap.inputs:
        parts.append("\nFields:")
        for i in snap.inputs:
            parts.append(f"  - {i.label} ({i.type})")
    if snap.actions:
        parts.append("\nActions:")
        for a in snap.actions[:12]:
            parts.append(f"  - {a.label} [{a.type}]")
    if snap.alerts:
        for a in snap.alerts:
            parts.append(f"\nAlert: [{a.type}] {a.text}")
    return "\n".join(parts)


# --- Agent loop ---


def run_agent(task: str):
    client = anthropic.Anthropic()

    system = """You are a research agent that investigates topics across multiple websites.

You have two types of tools:
1. **Site mapping tools** (preferred): Map a website to auto-generate tools, then use those tools for fast, structured data access. Use map_site → list_tools → run_tool.
2. **Manual browsing tools** (fallback): Browse pages directly when mapping isn't suitable or you need to see specific page content.

Research strategy:
1. Map the relevant websites first — this gives you powerful generated tools
2. Use generated tools to efficiently query each site for relevant data
3. Fall back to manual browsing only when generated tools don't cover what you need
4. Synthesize findings from all sites into a comprehensive summary with sources
5. Close the browser when done

Always prefer mapped tools over manual browsing — they're faster and return cleaner data.

You can also: take screenshots for visual evidence, extract cookies after login, and create new sessions with saved cookies to demonstrate authentication persistence."""

    messages = [{"role": "user", "content": task}]

    print(f"Research Task: {task}\n")
    print("=" * 60)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        assistant_content = response.content
        tool_results = []

        for block in assistant_content:
            if block.type == "text":
                print(f"\nAgent: {block.text}")
            elif block.type == "tool_use":
                print(f"\n> {block.name}({json.dumps(block.input, separators=(',', ':'))})")
                result = execute_tool(block.name, block.input)
                print(f"  → {result[:200]}{'...' if len(result) > 200 else ''}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        if response.stop_reason == "end_turn":
            break

        if tool_results:
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    print("\n" + "=" * 60)


# --- Main ---


def main():
    for key in ["BABELWRAP_API_KEY", "ANTHROPIC_API_KEY"]:
        if key not in os.environ:
            print(f"Error: {key} not set", file=sys.stderr)
            sys.exit(1)

    task = sys.argv[1] if len(sys.argv) > 1 else (
        "Demonstrate authentication persistence and multi-site research:\n"
        "1. Browse to https://the-internet.herokuapp.com/login\n"
        "2. Log in with username 'tomsmith' and password 'SuperSecretPassword!'\n"
        "3. Take a screenshot of the secure area\n"
        "4. Extract the session cookies with get_cookies\n"
        "5. Close the browser, then create a NEW session with those cookies\n"
        "6. Navigate to https://the-internet.herokuapp.com/secure to verify you're still logged in\n"
        "7. Take a screenshot to prove auth persisted\n"
        "8. Then use the already-mapped books.toscrape.com to get book categories and details\n"
        "9. Summarize: what authentication persistence means and what data you found"
    )

    try:
        run_agent(task)
    finally:
        if session:
            session.close()
        bw.close()


if __name__ == "__main__":
    main()
