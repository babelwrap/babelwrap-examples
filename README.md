# Babelwrap Examples

Official example projects for [BabelWrap](https://babelwrap.com) — the web, as an API, for your agents.

BabelWrap lets AI agents interact with any website through a simple API using natural language instead of DOM selectors. These examples show how to build agents that use BabelWrap to navigate the web, fill forms, shop, research, handle authentication, and automate complex workflows.

## Examples

| # | Example | Framework | Website | What It Does |
|---|---------|-----------|---------|-------------|
| 1 | [hello-babelwrap](./01-hello-babelwrap/) | Python SDK | books.toscrape.com | Quick intro — navigate, click, extract (no LLM key needed) |
| 2 | [map-and-discover](./02-map-and-discover/) | Python SDK | books.toscrape.com | **Site mapping** — map a site, use generated tools (no LLM key needed) |
| 3 | [claude-shopping-agent](./03-claude-shopping-agent/) | Anthropic SDK | saucedemo.com | Claude agent logs in, shops, checks out + **screenshots** |
| 4 | [openai-web-researcher](./04-openai-web-researcher/) | OpenAI SDK | Wikipedia + real sites | GPT-4o agent researches topics with **scroll + extract** |
| 5 | [agno-web-automation](./05-agno-web-automation/) | Agno + Claude | the-internet.herokuapp.com | **Auth, hover, keyboard, checkboxes, file upload** — every interaction |
| 6 | [agno-deal-finder](./06-agno-deal-finder/) | Agno + Claude | saucedemo.com | **Site mapping + batch actions** for efficient deal finding |
| 7 | [multi-site-researcher](./07-multi-site-researcher/) | Anthropic SDK | multiple sites | **Cookie auth persistence + screenshots + mapping** |

## Feature Coverage

| Feature | Ex1 | Ex2 | Ex3 | Ex4 | Ex5 | Ex6 | Ex7 |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Navigate, click, extract | X | | X | X | X | X | X |
| Fill forms + submit | | | X | | X | | X |
| Site mapping + tools | | X | | | | X | X |
| Screenshot | | | X | | | | X |
| Scroll pagination | | | | X | | | X |
| Hover | | | | | X | | |
| Keyboard press | | | | | X | | |
| File upload | | | | | X | | |
| Batch actions | | | | | | X | |
| Cookie auth persistence | | | | | | | X |

## Getting Started

### 1. Get API Keys

- **BabelWrap**: Sign up at [babelwrap.com](https://babelwrap.com) and create an API key
- **Anthropic**: Get a key at [console.anthropic.com](https://console.anthropic.com) (for examples 3, 5, 6, 7)
- **OpenAI**: Get a key at [platform.openai.com](https://platform.openai.com) (for example 4)

### 2. Clone and Configure

```bash
git clone https://github.com/babelwrap/babelwrap-examples.git
cd babelwrap-examples
cp .env.example .env
# Edit .env and add your API keys
```

### 3. Run Any Example

Each example has its own README. Start with Example 1 for basics, then jump to any agent example:

```bash
cd 05-agno-web-automation
pip install -r requirements.txt
python web_automation.py
```

## How the Examples Are Organized

**Examples 1-2** teach the BabelWrap SDK fundamentals — sessions, navigation, data extraction, and site mapping. No LLM API key needed.

**Examples 3-7** are the main event — **AI agents using BabelWrap as their web interaction tool**. Each showcases different capabilities on different websites:
- **Ex 3**: Full e-commerce checkout with visual proof (screenshots)
- **Ex 4**: Research across real websites with scroll+extract pagination
- **Ex 5**: Every interaction type — auth, hover, keyboard, upload, checkboxes
- **Ex 6**: Site mapping + batch operations for efficiency
- **Ex 7**: Authentication persistence with cookies + multi-site research

## Resources

- [BabelWrap Documentation](https://babelwrap.com/docs)
- [Python SDK Reference](https://babelwrap.com/docs/quickstart)
- [Site Mapping Guide](https://babelwrap.com/docs/site-mapping)
- [Agno Framework](https://github.com/agno-agi/agno)
