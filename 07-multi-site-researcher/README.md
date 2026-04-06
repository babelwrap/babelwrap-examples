# Multi-Site Researcher — Claude Agent with Site Mapping

A Claude-powered research agent that maps multiple websites using BabelWrap's site mapping feature, discovers auto-generated tools for each site, and then researches a topic across all of them using a combination of generated tools and manual browsing.

This is the most advanced example in the series. It demonstrates the full power of combining an agentic loop with dynamic tool discovery across multiple sites.

## What this example does

1. **Maps multiple websites** — The agent calls `map_site` on each relevant website, which triggers BabelWrap to explore the site's structure and auto-generate callable tools.
2. **Discovers generated tools** — After mapping, the agent uses `list_tools` to see what tools BabelWrap created for each site (e.g., search, list categories, get product details).
3. **Researches across sites** — The agent uses `run_tool` to execute generated tools for fast, structured data access. When generated tools don't cover a need, it falls back to manual browsing (`browse`, `click`, `extract`).
4. **Synthesizes findings** — Results from all sites are combined into a comprehensive summary with sources.

## What you'll learn

- **Anthropic SDK `tool_use`** with dynamic tool discovery — the agent's available actions grow as it maps new sites
- **Multi-site mapping** — mapping several websites in a single session and querying across all of them
- **Combining generated tools with manual browsing** — using auto-generated tools as the primary data access method and falling back to direct page browsing when needed
- **Cookie-based authentication persistence** — extracting session cookies after login and reusing them in a new browser session to stay authenticated
- **Screenshot capture** — saving visual evidence of page state as PNG files during the research flow
- **Agentic loop pattern** — the standard Anthropic SDK loop: send messages, process tool calls, append results, repeat until `end_turn`

## Key insight

Map multiple sites first, then let the agent use the generated tools to efficiently gather structured data from all of them. Generated tools are faster and return cleaner data than manual browsing, so they should be the primary method. Manual browsing fills in the gaps.

## Prerequisites

- Python 3.10+
- A [BabelWrap](https://babelwrap.com) API key
- An [Anthropic](https://console.anthropic.com) API key

## Quick start

```bash
cd 07-multi-site-researcher
pip install -r requirements.txt

export BABELWRAP_API_KEY="your-babelwrap-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# Run with the default research task (compare book sites)
python multi_site.py

# Or provide your own research task
python multi_site.py "Map https://news.ycombinator.com and https://lobste.rs. Compare the top stories on both sites right now."
```

## How it works

The agent has two categories of tools:

**Site mapping tools (preferred):**
- `map_site` — Map a website to auto-generate tools for it
- `list_tools` — List the generated tools for a mapped site
- `run_tool` — Execute a generated tool to get structured data

**Manual browsing tools (fallback):**
- `browse` — Navigate to a URL and get a page snapshot
- `click` — Click an element on the current page
- `extract` — Extract structured data from the current page
- `scroll_down` — Scroll down to see more content
- `close_browser` — Close the browser session

**Cookie & screenshot tools:**
- `screenshot` — Take a screenshot of the current page and save it as a PNG for visual evidence
- `get_cookies` — Extract all cookies from the current browser session (useful after logging in)
- `new_session_with_cookies` — Create a new browser session with previously saved cookies to restore authentication without logging in again

The agent decides which tools to use based on the research task. It typically maps sites first, then queries them using generated tools, and only falls back to manual browsing when necessary.
