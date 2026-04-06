"""Hello BabelWrap — your first script.

Navigate a bookstore, extract data, and browse pages — all with natural language.
"""

import json
import os

from babelwrap import BabelWrap


def main():
    api_key = os.environ["BABELWRAP_API_KEY"]

    with BabelWrap(api_key=api_key) as bw:
        with bw.create_session() as session:
            # Navigate to the bookstore
            snap = session.navigate("https://books.toscrape.com")
            print(f"Page: {snap.title}")
            print(f"URL:  {snap.url}")
            print(f"Navigation: {snap.navigation[:5]}")
            print()

            # Extract structured data with a natural language query
            print("--- Page 1 Books ---")
            books = session.extract("all book titles and prices on this page")
            for book in books[:5]:
                print(f"  {book.get('title', 'N/A')} — {book.get('price', 'N/A')}")
            print(f"  ... ({len(books)} books total)")
            print()

            # Click "next" to go to page 2 — natural language targeting
            snap = session.click("next")
            print(f"Navigated to: {snap.url}")
            print()

            # Extract from page 2
            print("--- Page 2 Books ---")
            books_p2 = session.extract("all book titles and prices on this page")
            for book in books_p2[:5]:
                print(f"  {book.get('title', 'N/A')} — {book.get('price', 'N/A')}")
            print(f"  ... ({len(books_p2)} books total)")
            print()

            # Go back to page 1
            snap = session.back()
            print(f"Back to: {snap.url}")

            # Confirm with snapshot
            snap = session.snapshot()
            print(f"Current page title: {snap.title}")

    print("\nDone! Session auto-closed.")


if __name__ == "__main__":
    main()
