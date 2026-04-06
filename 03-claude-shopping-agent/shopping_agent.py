"""Claude Shopping Agent -- an AI agent that shops using BabelWrap.

Claude receives BabelWrap tools (navigate, click, fill, submit, extract, screenshot,
wait_for) and autonomously browses saucedemo.com, picks a product, and completes checkout.
"""

import base64
import json
import os
import sys
from pathlib import Path

import anthropic
from babelwrap import BabelWrap, BabelWrapError

# --- BabelWrap client setup ---

bw = BabelWrap(api_key=os.environ["BABELWRAP_API_KEY"])
session = None

# --- Tool definitions for Claude ---

TOOLS = [
    {
        "name": "create_session",
        "description": "Create a new browser session. Call this first before any other action.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "navigate",
        "description": "Navigate the browser to a URL. Returns a snapshot of the page showing inputs, actions, and content.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "The URL to navigate to"}},
            "required": ["url"],
        },
    },
    {
        "name": "click",
        "description": "Click an element on the page. Use natural language to describe what to click, e.g. 'Add to cart button' or 'Login button'. Returns updated page snapshot.",
        "input_schema": {
            "type": "object",
            "properties": {"target": {"type": "string", "description": "Natural language description of the element to click"}},
            "required": ["target"],
        },
    },
    {
        "name": "fill",
        "description": "Fill a form field with a value. Use natural language to describe the field, e.g. 'Username field' or 'Email input'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Natural language description of the field to fill"},
                "value": {"type": "string", "description": "The value to enter"},
            },
            "required": ["target", "value"],
        },
    },
    {
        "name": "extract",
        "description": "Extract structured data from the current page using a natural language query. Returns JSON data.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "What data to extract, e.g. 'all product names and prices'"}},
            "required": ["query"],
        },
    },
    {
        "name": "wait_for",
        "description": "Wait for a condition on the page before continuing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to wait for on the page"},
                "url_contains": {"type": "string", "description": "URL fragment to wait for"},
            },
        },
    },
    {
        "name": "screenshot",
        "description": "Take a screenshot of the current page. Saves it as a PNG file. Use this to capture visual evidence of key steps.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "A short name for the screenshot, e.g. 'login-page' or 'order-confirmation'"}
            },
            "required": ["name"],
        },
    },
    {
        "name": "close_session",
        "description": "Close the browser session. Call this when done.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
]

# --- Helpers ---


def _save_screenshot(b64_data: str, filename: str) -> None:
    """Save a base64 PNG screenshot to the screenshots/ directory."""
    out_dir = Path("screenshots")
    out_dir.mkdir(exist_ok=True)
    (out_dir / filename).write_bytes(base64.b64decode(b64_data))


# --- Tool execution ---


def execute_tool(name: str, input: dict) -> str:
    """Execute a BabelWrap tool and return the result as a string for Claude."""
    global session

    try:
        if name == "create_session":
            session = bw.create_session()
            return f"Session created: {session.session_id}"

        if session is None:
            return "Error: No active session. Call create_session first."

        if name == "navigate":
            snap = session.navigate(input["url"])
            return format_snapshot(snap)

        elif name == "click":
            snap = session.click(input["target"])
            return format_snapshot(snap)

        elif name == "fill":
            snap = session.fill(input["target"], input["value"])
            return f"Filled '{input['target']}' with '{input['value']}'"

        elif name == "extract":
            data = session.extract(input["query"])
            return json.dumps(data, indent=2)

        elif name == "wait_for":
            result = session.wait_for(
                text=input.get("text"),
                url_contains=input.get("url_contains"),
            )
            timed_out = result.get("timed_out", False)
            return "Condition met." if not timed_out else "Timed out waiting."

        elif name == "screenshot":
            img_b64 = session.screenshot()
            filename = input["name"].replace(" ", "-") + ".png"
            _save_screenshot(img_b64, filename)
            return f"Screenshot saved: screenshots/{filename}"

        elif name == "close_session":
            session.close()
            session = None
            return "Session closed."

        else:
            return f"Unknown tool: {name}"

    except BabelWrapError as e:
        return f"BabelWrap error: [{e.code}] {e.message}"
    except Exception as e:
        return f"Error: {e}"


def format_snapshot(snap) -> str:
    """Format a BabelWrap snapshot into a concise string for Claude."""
    parts = [f"Page: {snap.title}", f"URL: {snap.url}"]

    if snap.content:
        content = snap.content[:500]
        if len(snap.content) > 500:
            content += "..."
        parts.append(f"\nContent: {content}")

    if snap.inputs:
        parts.append("\nForm Fields:")
        for inp in snap.inputs:
            parts.append(f"  - {inp.label} (type: {inp.type}, id: {inp.id})")

    if snap.actions:
        parts.append("\nActions:")
        for act in snap.actions[:15]:
            primary = " [PRIMARY]" if act.primary else ""
            parts.append(f"  - {act.label} ({act.type}){primary}")

    if snap.alerts:
        parts.append("\nAlerts:")
        for alert in snap.alerts:
            parts.append(f"  - [{alert.type}] {alert.text}")

    return "\n".join(parts)


# --- Agent loop ---


def run_agent(task: str):
    """Run the Claude shopping agent with an agentic tool-use loop."""
    client = anthropic.Anthropic()

    system = """You are a shopping assistant agent. You have access to BabelWrap tools that let you control a web browser.

Your workflow:
1. Create a browser session
2. Navigate to the store
3. Browse products and find what the user wants
4. Add items to cart
5. Complete the checkout process
6. Close the session when done

Always read the page snapshot carefully before deciding your next action. Use natural language to describe elements you want to interact with.

Take screenshots at key moments (after login, when viewing products, at order confirmation) to capture visual evidence."""

    messages = [{"role": "user", "content": task}]

    print(f"Task: {task}\n")
    print("=" * 60)

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=system,
            tools=TOOLS,
            messages=messages,
        )

        # Process response content blocks
        assistant_content = response.content
        tool_results = []

        for block in assistant_content:
            if block.type == "text":
                print(f"\nAgent: {block.text}")

            elif block.type == "tool_use":
                print(f"\n> Tool: {block.name}({json.dumps(block.input)})")
                result = execute_tool(block.name, block.input)
                print(f"  Result: {result[:200]}{'...' if len(result) > 200 else ''}")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        # If the model stopped because it's done (no more tool calls), we're finished
        if response.stop_reason == "end_turn":
            break

        # If there were tool calls, send results back
        if tool_results:
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    print("\n" + "=" * 60)
    print("Agent finished.")


# --- Main ---


def main():
    if "BABELWRAP_API_KEY" not in os.environ:
        print("Error: BABELWRAP_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    task = """Go to https://www.saucedemo.com and complete a purchase:
1. Log in with username "standard_user" and password "secret_sauce"
2. Browse the products and pick the cheapest item
3. Add it to the cart
4. Complete the checkout with name "Jane Doe" and zip code "94105"
5. Confirm the order
6. Take screenshots at each key step for visual verification"""

    try:
        run_agent(task)
    finally:
        if session:
            session.close()
        bw.close()


if __name__ == "__main__":
    main()
