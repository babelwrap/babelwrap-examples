"""OpenAI Web Researcher -- a GPT-4o agent that researches topics using BabelWrap.

The agent navigates to multiple websites, extracts relevant information,
and compiles a research summary -- all autonomously using function calling.
"""

import json
import os
import sys

from openai import OpenAI
from babelwrap import BabelWrap, BabelWrapError

# --- BabelWrap setup ---

bw = BabelWrap(api_key=os.environ["BABELWRAP_API_KEY"])
session = None

# --- Tool definitions for OpenAI ---

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_session",
            "description": "Create a new browser session. Call this first before any browsing action.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": (
                "Navigate the browser to a URL. Returns a snapshot of the page "
                "with its content, inputs, actions, and navigation links."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to",
                    }
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": (
                "Click an element on the page described in natural language. "
                "Returns the updated page snapshot."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Natural language description of what to click",
                    }
                },
                "required": ["target"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "extract",
            "description": (
                "Extract structured data from the current page. "
                "Describe what you want in natural language."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What to extract, e.g. 'all article titles and summaries'",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "scroll",
            "description": "Scroll the page to see more content. Use this on long pages to reveal additional text before extracting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {"type": "string", "enum": ["up", "down"], "description": "Scroll direction"},
                    "amount": {"type": "string", "enum": ["page", "half"], "description": "How much to scroll (default: page)"},
                },
                "required": ["direction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "snapshot",
            "description": (
                "Read the current page state without performing any action. "
                "Useful to re-read the page after scrolling."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_session",
            "description": "Close the browser session and free resources.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

# --- Tool execution ---


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a BabelWrap tool and return the result as text."""
    global session

    try:
        if name == "create_session":
            session = bw.create_session()
            return f"Browser session created: {session.session_id}"

        if session is None:
            return "Error: No active session. Call create_session first."

        if name == "navigate":
            snap = session.navigate(arguments["url"])
            return format_snapshot(snap)
        elif name == "click":
            snap = session.click(arguments["target"])
            return format_snapshot(snap)
        elif name == "extract":
            data = session.extract(arguments["query"])
            return json.dumps(data, indent=2)
        elif name == "scroll":
            snap = session.scroll(arguments.get("direction", "down"), arguments.get("amount", "page"))
            return format_snapshot(snap)
        elif name == "snapshot":
            snap = session.snapshot()
            return format_snapshot(snap)
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
    """Format a BabelWrap snapshot for the agent."""
    parts = [f"Page: {snap.title}", f"URL: {snap.url}"]

    if snap.content:
        content = snap.content[:1200]
        if len(snap.content) > 1200:
            content += "..."
        parts.append(f"\nContent:\n{content}")

    if snap.navigation:
        parts.append(f"\nNavigation: {', '.join(snap.navigation[:10])}")

    if snap.inputs:
        parts.append("\nForm Fields:")
        for inp in snap.inputs:
            parts.append(f"  - {inp.label} ({inp.type})")

    if snap.actions:
        parts.append("\nClickable Elements:")
        for act in snap.actions[:15]:
            parts.append(f"  - {act.label} ({act.type})")

    return "\n".join(parts)


# --- Agent loop ---


def run_researcher(topic: str):
    """Run the GPT-4o research agent."""
    client = OpenAI()

    system = f"""You are a web research agent. You have BabelWrap browser tools to navigate websites and extract information.

Your task: Research the given topic by visiting relevant websites.

Research strategy:
1. Create a browser session
2. Start with Wikipedia — navigate to the relevant article, scroll down to read more content, extract key facts
3. Visit 1-2 additional sources for different perspectives
4. Use the scroll tool to see more content on long pages — scroll and extract multiple times
5. After gathering enough information, close the session
6. Provide a comprehensive research summary with facts from each source

Be thorough but efficient. Scroll down on long pages to get more content before extracting."""

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": f"Research this topic and give me a comprehensive summary: {topic}",
        },
    ]

    print(f"Research Topic: {topic}\n")
    print("=" * 60)

    while True:
        response = client.chat.completions.create(
            model="gpt-4o",
            tools=TOOLS,
            messages=messages,
        )

        message = response.choices[0].message

        # If the model wants to call tools
        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                print(f"\n> Tool: {name}({json.dumps(args)})")
                result = execute_tool(name, args)
                print(
                    f"  Result: {result[:200]}"
                    f"{'...' if len(result) > 200 else ''}"
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

        # If the model is done (no tool calls, has content)
        elif message.content:
            print(f"\n{'=' * 60}")
            print("\nResearch Summary:\n")
            print(message.content)
            break

        else:
            break

    print(f"\n{'=' * 60}")
    print("Research complete.")


# --- Main ---


def main():
    if "BABELWRAP_API_KEY" not in os.environ:
        print("Error: BABELWRAP_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # Default research topic (can be customized)
    topic = sys.argv[1] if len(sys.argv) > 1 else "the Apollo 11 moon landing"

    try:
        run_researcher(topic)
    finally:
        if session:
            session.close()
        bw.close()


if __name__ == "__main__":
    main()
