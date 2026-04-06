# Claude Shopping Agent

An AI agent built with the Anthropic Python SDK that uses BabelWrap to autonomously shop on an e-commerce site. Claude receives browser-control tools, reasons about what it sees on each page, and decides what action to take next -- navigating to a store, browsing products, adding items to the cart, and completing checkout without any human intervention.

## What you'll learn

- **Anthropic SDK tool_use**: Defining custom tools and handling `tool_use` / `tool_result` message blocks with `client.messages.create()`
- **BabelWrap actions as Claude tools**: Wrapping `navigate`, `click`, `fill`, `extract`, and `wait_for` so Claude can call them by name
- **Agentic loop pattern**: A `while True` loop that sends Claude's tool calls to BabelWrap, feeds results back, and repeats until Claude decides it's done (`stop_reason == "end_turn"`)
- **Screenshot capture**: Taking screenshots at key moments during the workflow and saving them locally as PNG files for visual verification

## Prerequisites

- Python 3.10+
- A [BabelWrap](https://babelwrap.com) API key
- An [Anthropic](https://console.anthropic.com) API key

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your API keys
export BABELWRAP_API_KEY="your-babelwrap-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# 3. Run the agent
python shopping_agent.py
```

## How the code works

1. **Tool definitions** -- A list of tool schemas (`TOOLS`) describes every browser action Claude can take: `create_session`, `navigate`, `click`, `fill`, `extract`, `screenshot`, `wait_for`, and `close_session`. Each schema includes a natural-language description so Claude knows when and how to use it.

2. **Tool execution** -- `execute_tool()` maps each tool name to the corresponding BabelWrap SDK call. It returns a string result (page snapshot, extracted data, or error message) that gets sent back to Claude.

3. **Snapshot formatting** -- `format_snapshot()` turns a BabelWrap page snapshot into a concise text summary containing the page title, URL, visible content, form fields, clickable actions, and any alerts. This gives Claude everything it needs to reason about the page.

4. **Agent loop** -- `run_agent()` drives the conversation:
   - Send the user's task to Claude along with the available tools.
   - Read the response blocks. Text blocks are printed; `tool_use` blocks are executed against BabelWrap.
   - Tool results are appended to the message history and sent back to Claude.
   - The loop continues until `stop_reason == "end_turn"`, meaning Claude has nothing left to do.

5. **Screenshot capture** -- The `screenshot` tool calls `session.screenshot()` to grab a base64-encoded PNG of the current page, then `_save_screenshot()` decodes and writes it to the `screenshots/` directory. The agent is prompted to take screenshots at key moments (after login, product view, order confirmation) for visual evidence.

6. **Default task** -- Out of the box the agent logs into saucedemo.com, finds the cheapest product, adds it to the cart, fills in checkout details, confirms the order, and saves screenshots at each key step.

## Environment variables

| Variable | Description |
|---|---|
| `BABELWRAP_API_KEY` | Your BabelWrap API key |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
