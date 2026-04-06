# Hello BabelWrap — Your First Script

A minimal example that navigates a live bookstore website, extracts structured data, clicks through pagination, and uses browser history — all driven by natural language.

## What This Example Does

The script opens [books.toscrape.com](https://books.toscrape.com) in a BabelWrap session and:

1. **Navigates** to the bookstore homepage and prints the page title, URL, and navigation links.
2. **Extracts** every book title and price on page 1 as structured data (a list of dicts).
3. **Clicks** the "next" button using a natural-language target — no CSS selectors needed.
4. **Extracts** books from page 2 the same way.
5. **Goes back** to page 1 using `session.back()` (browser-history navigation).
6. **Takes a snapshot** to confirm the current page state.

## What You'll Learn

- Creating a `BabelWrap` client and a `Session` (both are context managers).
- Navigating to a URL with `session.navigate(url)`.
- Clicking elements with natural language via `session.click(target)`.
- Extracting structured data with `session.extract(query)`.
- Reading `Snapshot` attributes: `.title`, `.url`, `.navigation`, `.inputs`, `.actions`.
- Navigating browser history with `session.back()`.
- Taking a snapshot of the current page with `session.snapshot()`.

## Prerequisites

- **Python 3.10+**
- A **BabelWrap API key** — set it as an environment variable:
  ```bash
  export BABELWRAP_API_KEY="your-api-key-here"
  ```

## Quick Start

```bash
# Clone the repo and enter this example
git clone https://github.com/anthropomorphic-ai/babelwrap-examples.git
cd babelwrap-examples/01-hello-babelwrap

# Install dependencies
pip install -r requirements.txt

# Set your API key
export BABELWRAP_API_KEY="your-api-key-here"

# Run the script
python hello.py
```

## How the Code Works

The script follows a straightforward pattern:

1. **Client setup** — `BabelWrap(api_key=...)` creates the client. Using it as a context manager ensures cleanup.
2. **Session creation** — `bw.create_session()` spins up a managed browser session. The `with` block auto-closes it when done.
3. **Navigate** — `session.navigate(url)` loads a page and returns a `Snapshot` with metadata about the page (title, URL, navigation links, form inputs, available actions).
4. **Extract** — `session.extract(query)` takes a plain-English description of the data you want and returns it as a list of dicts (or a single dict).
5. **Click** — `session.click("next")` finds the element matching your description and clicks it, returning a new `Snapshot` of the resulting page.
6. **Back** — `session.back()` navigates back in the browser history, just like pressing the back button.
7. **Snapshot** — `session.snapshot()` captures the current page state without performing any action.

## Expected Output

```
Page: All products | Books to Scrape - Sandbox
URL:  https://books.toscrape.com/
Navigation: ['Home', 'Books', 'Travel', 'Mystery', 'Historical Fiction']

--- Page 1 Books ---
  A Light in the Attic — £51.77
  Tipping the Velvet — £53.74
  Soumission — £50.10
  Sharp Objects — £47.82
  Sapiens: A Brief History of Humankind — £54.23
  ... (20 books total)

Navigated to: https://books.toscrape.com/catalogue/page-2.html

--- Page 2 Books ---
  In Her Wake — £12.84
  How Music Works — £37.32
  Foolproof Preserving — £30.52
  Chase Me — £25.27
  Black Dust — £34.53
  ... (20 books total)

Back to: https://books.toscrape.com/
Current page title: All products | Books to Scrape - Sandbox

Done! Session auto-closed.
```
