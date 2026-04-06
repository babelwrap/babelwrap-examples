"""Map and Discover — automatic website tools.

Map a website once. BabelWrap explores it, discovers its structure,
and generates tools you can call with simple parameters.
No sessions. No navigation. No selectors. Just tools.
"""

import json
import os
import sys
import time

from babelwrap import BabelWrap


def main():
    api_key = os.environ["BABELWRAP_API_KEY"]

    with BabelWrap(api_key=api_key) as bw:
        target_url = "https://books.toscrape.com"

        # Step 1: Check if site is already mapped and ready
        print("Checking for existing site mapping...")
        site_id = None
        sites = bw.list_sites()
        for site in sites:
            domain = site.get("domain", "")
            if "books.toscrape" in domain and site.get("status") == "ready":
                site_id = site.get("site_id") or site.get("id")
                print(f"  Found existing mapping: {site_id}")
                break

        # Step 2: Map the site if not already mapped
        if not site_id:
            print(f"\nMapping {target_url}...")
            print("  BabelWrap is exploring the site — this may take a few minutes.\n")
            result = bw.map_site(target_url)

            # map_site returns an order; poll list_sites until ready
            site_id = result.get("site_id")
            if not site_id:
                print("  Mapping started. Waiting for explorer to finish...")
                for i in range(30):
                    time.sleep(15)
                    sites = bw.list_sites()
                    for s in sites:
                        if "books.toscrape" in s.get("domain", ""):
                            if s["status"] == "ready":
                                site_id = s["site_id"]
                                break
                            elif s["status"] == "failed":
                                print(f"  Mapping failed.")
                                sys.exit(1)
                    if site_id:
                        break
                    print(f"  [{(i+1)*15}s] Still exploring...")

            if not site_id:
                print("  Mapping timed out.")
                sys.exit(1)

            print(f"  Mapping complete! Site ID: {site_id}")

        # Step 3: List all generated tools
        print("\n--- Generated Tools ---")
        tools_response = bw.site_tools(site_id)
        tools = tools_response.get("tools", [])
        tool_names = []
        for tool in tools:
            name = tool.get("name", "unknown")
            desc = tool.get("description", "")
            params = tool.get("params", [])
            tool_names.append(name)
            print(f"\n  {name}")
            print(f"    {desc}")
            if params:
                for p in params:
                    req = " (required)" if p.get("required") else ""
                    print(f"    - {p.get('name')}: {p.get('type', 'string')}{req}")

        # Step 4: Execute the discovered tools dynamically
        print(f"\n--- Executing Tools ---\n")

        # Find and run a "categories" or "list" tool
        cat_tool = next((t for t in tool_names if "categor" in t), None)
        if cat_tool:
            print(f"1. Running '{cat_tool}'...")
            try:
                result = bw.execute_tool(site_id, cat_tool, {})
                data = result.get("data", result.get("result", result))
                print(f"   {json.dumps(data, indent=4)[:1000]}")
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print("1. No category tool found, skipping.")

        # Find and run a "list" or "browse" tool
        list_tool = next((t for t in tool_names if "list" in t and "categor" not in t), None)
        if list_tool:
            print(f"\n2. Running '{list_tool}'...")
            try:
                result = bw.execute_tool(site_id, list_tool, {})
                data = result.get("data", result.get("result", result))
                if isinstance(data, list):
                    for item in data[:5]:
                        title = item.get("title", item.get("name", "N/A"))
                        price = item.get("price", "")
                        print(f"   {title} {price}")
                    if len(data) > 5:
                        print(f"   ... ({len(data)} total)")
                else:
                    print(f"   {json.dumps(data, indent=4)[:500]}")
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print("\n2. No list tool found, skipping.")

        # Find and run a "details" tool
        detail_tool = next((t for t in tool_names if "detail" in t), None)
        if detail_tool:
            print(f"\n3. Running '{detail_tool}'...")
            # Try to figure out the right param from the tool definition
            tool_def = next((t for t in tools if t["name"] == detail_tool), {})
            params = tool_def.get("params", [])
            test_params = {}
            for p in params:
                if p.get("required"):
                    # Use a sample value based on the param name
                    if "slug" in p["name"] or "id" in p["name"]:
                        test_params[p["name"]] = "a-light-in-the-attic_1000"
                    else:
                        test_params[p["name"]] = "test"
            try:
                result = bw.execute_tool(site_id, detail_tool, test_params)
                data = result.get("data", result.get("result", result))
                print(f"   {json.dumps(data, indent=4)[:1000]}")
            except Exception as e:
                print(f"   Error: {e}")
        else:
            print("\n3. No detail tool found, skipping.")

        print("\n--- Summary ---")
        print(f"BabelWrap generated {len(tools)} tools for {target_url}.")
        print("Map once, use forever. No sessions. No selectors. Just tools.")


if __name__ == "__main__":
    main()
