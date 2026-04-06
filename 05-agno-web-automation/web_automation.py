"""Agno Web Automation — demonstrating every BabelWrap interaction type.

An Agno agent explores the-internet.herokuapp.com and demonstrates:
authentication, hover, keyboard, forms, checkboxes, and file upload.
"""

import json
import os
import sys
import tempfile

from agno.agent import Agent
from agno.models.anthropic import Claude
from babelwrap import BabelWrap, BabelWrapError

_bw = BabelWrap(api_key=os.environ["BABELWRAP_API_KEY"])
_session = None


# --- BabelWrap tools ---


def create_browser() -> str:
    """Create a browser session. Call this first."""
    global _session
    _session = _bw.create_session()
    return f"Browser ready: {_session.session_id}"


def go_to(url: str) -> str:
    """Navigate to a URL. Returns page content, form fields, and available actions."""
    if not _session:
        return "Error: Create browser first."
    try:
        snap = _session.navigate(url)
        return _fmt(snap)
    except BabelWrapError as e:
        return f"Error: {e.message}"


def click_element(target: str) -> str:
    """Click an element. Describe what to click in natural language."""
    if not _session:
        return "Error: Create browser first."
    try:
        snap = _session.click(target)
        return f"Clicked '{target}'.\n{_fmt(snap)}"
    except BabelWrapError as e:
        return f"Error: {e.message}"


def type_text(field: str, text: str) -> str:
    """Type text into a form field. Describe the field in natural language."""
    if not _session:
        return "Error: Create browser first."
    try:
        _session.fill(field, text)
        return f"Typed '{text}' into '{field}'"
    except BabelWrapError as e:
        return f"Error: {e.message}"


def submit_form(target: str = "") -> str:
    """Submit a form. Optionally specify which form."""
    if not _session:
        return "Error: Create browser first."
    try:
        snap = _session.submit(target or None)
        return f"Form submitted.\n{_fmt(snap)}"
    except BabelWrapError as e:
        return f"Error: {e.message}"


def press_key(key: str) -> str:
    """Press a keyboard key. Examples: 'Enter', 'Tab', 'Escape', 'ArrowDown'."""
    if not _session:
        return "Error: Create browser first."
    try:
        snap = _session.press(key)
        return f"Pressed '{key}'.\n{_fmt(snap)}"
    except BabelWrapError as e:
        return f"Error: {e.message}"


def hover_over(target: str) -> str:
    """Hover the mouse over an element. Useful for revealing tooltips or hidden content."""
    if not _session:
        return "Error: Create browser first."
    try:
        snap = _session.hover(target)
        return f"Hovering over '{target}'.\n{_fmt(snap)}"
    except BabelWrapError as e:
        return f"Error: {e.message}"


def get_page_data(query: str) -> str:
    """Extract structured data from the current page using a natural language query."""
    if not _session:
        return "Error: Create browser first."
    try:
        data = _session.extract(query)
        return json.dumps(data, indent=2)
    except BabelWrapError as e:
        return f"Error: {e.message}"


def upload_file(target: str, filename: str) -> str:
    """Upload a file to a file input element. Creates a test file and uploads it."""
    if not _session:
        return "Error: Create browser first."
    try:
        # Create a temporary test file to upload
        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=f"_{filename}", delete=False
        )
        tmp.write(f"Test file uploaded by BabelWrap agent\nFilename: {filename}\n")
        tmp.close()
        snap = _session.upload(target, tmp.name)
        os.unlink(tmp.name)
        return f"Uploaded '{filename}'.\n{_fmt(snap)}"
    except BabelWrapError as e:
        return f"Error: {e.message}"
    except Exception as e:
        return f"Upload error: {e}"


def read_page() -> str:
    """Read the current page state without performing any action."""
    if not _session:
        return "Error: Create browser first."
    try:
        snap = _session.snapshot()
        return _fmt(snap)
    except BabelWrapError as e:
        return f"Error: {e.message}"


def close_browser() -> str:
    """Close the browser session."""
    global _session
    if _session:
        _session.close()
        _session = None
    return "Browser closed."


def _fmt(snap) -> str:
    """Format a snapshot for the agent."""
    parts = [f"Page: {snap.title}", f"URL: {snap.url}"]
    if snap.content:
        parts.append(f"\nContent: {snap.content[:500]}...")
    if snap.inputs:
        parts.append("\nForm Fields:")
        for i in snap.inputs:
            req = " (required)" if i.required else ""
            parts.append(f"  - {i.label}: {i.type}{req}")
    if snap.actions:
        parts.append("\nActions:")
        for a in snap.actions[:15]:
            parts.append(f"  - {a.label} [{a.type}]")
    if snap.alerts:
        parts.append("\nAlerts:")
        for a in snap.alerts:
            parts.append(f"  - [{a.type}] {a.text}")
    return "\n".join(parts)


# --- Agent ---

INSTRUCTIONS = [
    "You are a web automation agent that demonstrates BabelWrap's full interaction capabilities.",
    "You will visit the-internet.herokuapp.com and test different UI patterns.",
    "",
    "For each page, explain what you're about to do and what the result demonstrates.",
    "",
    "Available interaction types to demonstrate:",
    "1. AUTHENTICATION: Login with credentials, verify success",
    "2. HOVER: Hover to reveal hidden content",
    "3. KEYBOARD: Press keys and verify they register",
    "4. CHECKBOXES: Toggle checkboxes on/off",
    "5. FILE UPLOAD: Upload a test file",
    "6. DROPDOWN: Select options from dropdowns",
    "",
    "Go through each type systematically. Report what you observe after each action.",
]


def create_agent() -> Agent:
    return Agent(
        name="Web Automation Demo",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[
            create_browser,
            go_to,
            click_element,
            type_text,
            submit_form,
            press_key,
            hover_over,
            get_page_data,
            upload_file,
            read_page,
            close_browser,
        ],
        instructions=INSTRUCTIONS,
        markdown=True,
    )


def main():
    if "BABELWRAP_API_KEY" not in os.environ:
        print("Error: BABELWRAP_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    agent = create_agent()

    task = sys.argv[1] if len(sys.argv) > 1 else (
        "Demonstrate BabelWrap's full interaction capabilities on the-internet.herokuapp.com:\n"
        "1. Go to /login — log in with username 'tomsmith' and password 'SuperSecretPassword!'\n"
        "2. Go to /hovers — hover over the user avatars to reveal hidden profile links\n"
        "3. Go to /key_presses — press Enter, Tab, and Escape keys\n"
        "4. Go to /checkboxes — toggle both checkboxes\n"
        "5. Go to /upload — upload a test file\n"
        "6. Go to /dropdown — select 'Option 2' from the dropdown\n"
        "Close the browser when done and summarize what you demonstrated."
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
