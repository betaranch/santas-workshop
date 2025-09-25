#!/usr/bin/env python3
"""
Find ALL pages in the workspace to locate missing project pages
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def find_all_pages():
    api_key = os.getenv("NOTION_API")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Search for ALL pages
    url = "https://api.notion.com/v1/search"
    data = {
        "filter": {
            "property": "object",
            "value": "page"
        },
        "page_size": 100,
        "sort": {
            "direction": "descending",
            "timestamp": "last_edited_time"
        }
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        results = response.json().get("results", [])

        print(f"Found {len(results)} total pages:\n")
        print("="*60)

        # Look for project pages
        project_keywords = [
            "Permits", "Legal",
            "Space", "Operations",
            "Theme", "Design", "Story",
            "Marketing", "Sales",
            "Team",
            "Budget", "Finance",
            "Vendors", "Suppliers",
            "Evaluation", "Scaling"
        ]

        found_projects = {}

        for page in results:
            # Get title
            title = ""
            props = page.get("properties", {})
            for prop_name in ["Name", "Title", "title"]:
                if prop_name in props:
                    title_prop = props[prop_name]
                    if title_prop.get("type") == "title":
                        texts = title_prop.get("title", [])
                        if texts:
                            title = texts[0].get("text", {}).get("content", "")
                            break

            if not title:
                title = f"Untitled ({page['id'][:8]}...)"

            # Check if it matches any project keywords
            title_lower = title.lower()
            is_project = False

            for keyword in project_keywords:
                if keyword.lower() in title_lower:
                    is_project = True
                    if title not in found_projects:
                        found_projects[title] = page["id"]
                        print(f"[PROJECT] {title}")
                        print(f"          ID: {page['id']}")
                        print(f"          URL: {page['url']}")
                        print()
                    break

            # Show all pages for debugging
            if not is_project:
                print(f"[PAGE]    {title[:60]}")

        print("\n" + "="*60)
        print(f"SUMMARY: Found {len(found_projects)} project-related pages")

        # Save to file for reference
        with open("cache/all_pages.json", "w") as f:
            json.dump({
                "found_projects": found_projects,
                "all_pages": [
                    {
                        "title": get_title(p),
                        "id": p["id"],
                        "url": p["url"]
                    }
                    for p in results
                ]
            }, f, indent=2)

        print("\nSaved full list to cache/all_pages.json")

    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def get_title(page):
    """Extract title from page object"""
    props = page.get("properties", {})
    for prop_name in ["Name", "Title", "title"]:
        if prop_name in props:
            title_prop = props[prop_name]
            if title_prop.get("type") == "title":
                texts = title_prop.get("title", [])
                if texts:
                    return texts[0].get("text", {}).get("content", "")
    return "Untitled"

if __name__ == "__main__":
    find_all_pages()