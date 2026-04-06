# Agno Deal Finder -- Site Mapping + Agent Intelligence

An Agno agent that maps an e-commerce site using BabelWrap's site mapping feature, discovers the auto-generated tools, then uses those tools to find and compare the best deals by category. Includes a `batch_actions` tool for executing multiple browser actions in a single API call.

## What this example does

1. **Maps a website** -- BabelWrap explores the site's structure and auto-generates callable tools (browse categories, search products, extract details, etc.)
2. **Discovers tools dynamically** -- The agent doesn't know the site's structure ahead of time. It calls `list_site_tools` to see what BabelWrap created.
3. **Uses generated tools to collect data** -- The agent calls the discovered tools to browse categories, gather prices, and pull product details.
4. **Compares and recommends** -- The agent analyzes the collected data to find the best deals and presents a summary with prices, categories, and availability.

If the generated tools don't cover a specific need, the agent can fall back to manual browser-based browsing as a secondary strategy. For multi-step browser interactions (e.g., adding several items to a cart), the `batch_actions` tool executes multiple actions in one API call for efficiency.

## What you'll learn

- Combining Agno agents with BabelWrap site mapping
- Dynamic tool discovery -- the agent learns what it can do at runtime
- Executing auto-generated tools via `execute_tool`
- Batch operations -- executing multiple browser actions in one API call
- Designing agents with primary and fallback tool strategies
- Passing structured parameters through simple-type Agno tool interfaces

## Key insight

The agent doesn't know the site's structure ahead of time. It discovers it through mapping. This means the same agent code works against any site BabelWrap can map -- no per-site customization required.

## Prerequisites

- Python 3.10+
- A [BabelWrap](https://babelwrap.com) API key
- An [Anthropic](https://console.anthropic.com) API key

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API keys
export BABELWRAP_API_KEY="your-babelwrap-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Run with the default task (browse saucedemo.com products and demo batch actions)
python deal_finder.py

# Or pass a custom task
python deal_finder.py "Map https://www.saucedemo.com and find the cheapest product"
```

## How it works

```
User prompt
    |
    v
Agno Agent (Claude)
    |
    |-- map_website(url)          --> BabelWrap maps the site, returns site_id
    |-- list_site_tools(site_id)  --> BabelWrap returns auto-generated tools
    |-- use_site_tool(site_id, tool_name, params) --> Execute a generated tool
    |
    |-- (fallback) open_browser / browse_click / browse_extract / batch_actions
    |
    v
Deal summary with prices, categories, and recommendations
```

The agent's instructions tell it to prefer the mapping workflow (`map -> list tools -> use tools`) over manual browsing. The manual browser tools exist as a fallback for edge cases the generated tools don't cover.
