# Map and Discover — Automatic Website Tools

Map a website once. BabelWrap explores it, discovers its structure, and generates callable tools — no sessions, no navigation, no selectors. Just call the tools with simple parameters.

## What This Example Does

The script maps [books.toscrape.com](https://books.toscrape.com) and then uses the auto-generated tools to:

1. **Checks** for an existing site mapping (so you only map once).
2. **Maps** the site if needed — BabelWrap crawls the site, identifies entities, page types, and interactions, then generates tools.
3. **Lists** all generated tools with their names, descriptions, and parameters.
4. **Searches** for books by keyword using `execute_tool("search_books", ...)`.
5. **Gets details** for a specific book using `execute_tool("get_book_details", ...)`.
6. **Lists categories** using `execute_tool("list_categories", ...)`.

### The Key Insight

**Map once, use forever** — BabelWrap explores the site for you and generates tools you can call with simple parameters. No browser sessions. No CSS selectors. No click-by-click navigation. The mapper does the hard work once, and every subsequent call is a clean function invocation.

## What You'll Learn

- Listing existing site mappings with `bw.list_sites()`.
- Mapping a new site with `bw.map_site(url)`.
- Discovering generated tools with `bw.site_tools(site_id)`.
- Executing tools with `bw.execute_tool(site_id, tool_name, params)`.
- Handling varying response shapes gracefully (tool names and response formats depend on what the mapper discovers).

## Comparison with Example 1

Example 1 (`01-hello-babelwrap`) extracts book data from the same site using manual session-based navigation: open a session, navigate to a URL, extract data, click "next", extract again, go back. It works, but you write every step.

This example gets the **same data with zero manual navigation**. After mapping, each operation is a single `execute_tool()` call. The mapper already knows how the site works — you just ask for what you want.

| | Example 1 (Session) | Example 4 (Mapped) |
|---|---|---|
| Setup | Create session, navigate | Map site once |
| Search books | Navigate + extract + click | `execute_tool("search_books", {"query": "science"})` |
| Book details | Navigate to page + extract | `execute_tool("get_book_details", {"title": "..."})` |
| List categories | Navigate + extract | `execute_tool("list_categories", {})` |
| Selectors needed | None (natural language) | None (auto-generated tools) |
| Session required | Yes | No |

## Prerequisites

- **Python 3.10+**
- A **BabelWrap API key** — set it as an environment variable:
  ```bash
  export BABELWRAP_API_KEY="your-api-key-here"
  ```
- A **usage plan** that includes site mapping. Mapping consumes additional credits because BabelWrap crawls and analyzes the site structure.

## Quick Start

```bash
# Clone the repo and enter this example
git clone https://github.com/anthropomorphic-ai/babelwrap-examples.git
cd babelwrap-examples/04-map-and-discover

# Install dependencies
pip install -r requirements.txt

# Set your API key
export BABELWRAP_API_KEY="your-api-key-here"

# Run the script
python map_and_use.py
```

## How the Code Works

The script follows three phases:

### Phase 1: Map (or reuse)

```python
sites = bw.list_sites()          # Check for existing mappings
result = bw.map_site(target_url) # Map if needed — BabelWrap crawls the site
site_id = result.get("site_id") or result.get("id")
```

`map_site()` is the expensive call. BabelWrap navigates the entire site, identifies page types (listing pages, detail pages, search), discovers entities (books, categories), and generates tools. This runs once; after that, the site ID is reused.

### Phase 2: Discover

```python
tools_response = bw.site_tools(site_id)  # See what tools were generated
```

`site_tools()` returns the full list of auto-generated tools, including their names, descriptions, and parameter schemas. The exact tools depend on what the mapper found — a bookstore gets `search_books`, `get_book_details`, `list_categories`; a news site might get `search_articles`, `get_article`, `list_topics`.

### Phase 3: Execute

```python
result = bw.execute_tool(site_id, "search_books", {"query": "science"})
result = bw.execute_tool(site_id, "get_book_details", {"title": "A Light in the Attic"})
result = bw.execute_tool(site_id, "list_categories", {})
```

Each `execute_tool()` call runs the named tool with the given parameters. BabelWrap handles all the navigation, waiting, and extraction internally. You get structured data back.

## Expected Output

First run (mapping required):

```
Checking for existing site mapping...

Mapping https://books.toscrape.com...
  BabelWrap is exploring the site — this may take a minute.

  Mapping complete! Site ID: site_abc123

  Discovered entities: books, categories
  Discovered page types: listing, detail, search

--- Generated Tools ---

  search_books
    Search for books by keyword
    Parameters: {"query": "string"}

  get_book_details
    Get full details for a specific book
    Parameters: {"title": "string"}

  list_categories
    List all book categories
    Parameters: {}

--- Executing Tools ---

1. Searching for 'science' books...
   The Grand Design — £13.76
   The Elegant Universe — £15.49
   A Short History of Nearly Everything — £23.65
   ... (8 results)

2. Getting book details...
   {
       "title": "A Light in the Attic",
       "price": "£51.77",
       "availability": "In stock (22 available)",
       "rating": 3,
       "description": "It's hard to imagine a world without ..."
   }

3. Listing all categories...
   - Travel
   - Mystery
   - Historical Fiction
   - Sequential Art
   - Classics
   - Philosophy
   - Romance
   - Womens Fiction
   - Science
   - Poetry
   ... (50 categories total)

--- Summary ---
Three execute_tool() calls replaced 20+ lines of manual navigation.
Map once, use forever. No sessions. No selectors. Just tools.
```

Subsequent runs (mapping cached):

```
Checking for existing site mapping...
  Found existing mapping: site_abc123

--- Generated Tools ---
  ...
```

The mapping step is skipped entirely — tools are ready immediately.
