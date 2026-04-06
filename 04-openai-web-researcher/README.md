# OpenAI Web Researcher -- GPT-4o Agent with BabelWrap

A GPT-4o agent that uses BabelWrap to visit multiple websites, extract information, and compile a research summary on a given topic -- all autonomously using OpenAI function calling.

## What this example does

The researcher agent receives a topic (default: "the Apollo 11 moon landing"), then:

1. Creates a BabelWrap browser session
2. Starts with Wikipedia -- navigates to the relevant article and reads it thoroughly
3. Uses the **scroll + extract pagination pattern** to get more content from long pages (scroll down, then extract again -- repeat to cover the full article)
4. Visits 1-2 additional sources for different perspectives
5. Closes the session and delivers a comprehensive summary with facts from each source

The entire research flow is driven by GPT-4o deciding which BabelWrap tools to call and when, using OpenAI's function calling mechanism.

## What you'll learn

- **OpenAI SDK function calling** -- defining tools with JSON Schema and handling the tool call loop
- **BabelWrap as agent tools** -- wrapping BabelWrap actions (navigate, click, extract, scroll, snapshot) as callable functions for an LLM agent
- **Scroll + extract pagination** -- scrolling down long pages and extracting multiple times to get full article content
- **Multi-site research pattern** -- how to let an agent autonomously browse multiple sites, gather information, and synthesize findings

## Prerequisites

- Python 3.10+
- A [BabelWrap](https://babelwrap.com) API key
- An [OpenAI](https://platform.openai.com) API key

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API keys
export BABELWRAP_API_KEY="your-babelwrap-key"
export OPENAI_API_KEY="your-openai-key"

# Run with the default topic
python researcher.py

# Or specify your own topic
python researcher.py "the history of the Internet"
```

## Environment variables

| Variable | Description |
|---|---|
| `BABELWRAP_API_KEY` | Your BabelWrap API key |
| `OPENAI_API_KEY` | Your OpenAI API key |
