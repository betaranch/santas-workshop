#!/usr/bin/env python3
"""
Discover the Projects field configuration in the Tasks database
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

def discover_projects():
    """Discover the Projects field configuration"""

    # Get API key
    api_key = os.getenv("NOTION_API")
    if not api_key:
        print("ERROR: No NOTION_API key found in .env file")
        return

    # Setup headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    # Get the Tasks database ID
    db_id = "278bc994-24ab-8136-b84a-c02ba029cd33"

    # Get database schema
    url = f"https://api.notion.com/v1/databases/{db_id}"

    print(f"Fetching database schema...")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.json()

        # Check if Projects property exists
        if "Projects" in result.get("properties", {}):
            projects_prop = result["properties"]["Projects"]
            print("\nProjects field configuration:")
            print(f"  Type: {projects_prop.get('type')}")

            if projects_prop.get("type") == "relation":
                print(f"  Database ID: {projects_prop['relation'].get('database_id')}")

                # Get the related database
                related_db_id = projects_prop['relation'].get('database_id')
                if related_db_id:
                    print(f"\nFetching related Projects database...")
                    related_url = f"https://api.notion.com/v1/databases/{related_db_id}/query"

                    related_response = requests.post(related_url, headers=headers, json={})
                    related_response.raise_for_status()

                    projects_data = related_response.json()

                    print(f"\nAvailable projects ({len(projects_data['results'])} total):")

                    project_mapping = {}
                    for project in projects_data['results']:
                        # Get project name
                        title_prop = project['properties'].get('Name', {}).get('title', [])
                        if title_prop:
                            project_name = title_prop[0]['text']['content']
                            project_id = project['id']
                            project_mapping[project_name] = project_id
                            print(f"  - {project_name}: {project_id}")

                    # Save the mapping
                    cache_file = BASE_DIR / "cache" / "project_mapping.json"
                    with open(cache_file, 'w') as f:
                        json.dump(project_mapping, f, indent=2)

                    print(f"\nProject mapping saved to: {cache_file}")

                    # Look for Budget & Finance project
                    budget_projects = [name for name in project_mapping.keys()
                                     if 'budget' in name.lower() or 'finance' in name.lower() or '06' in name]

                    if budget_projects:
                        print(f"\nBudget/Finance related projects found:")
                        for name in budget_projects:
                            print(f"  - {name}: {project_mapping[name]}")
                    else:
                        print("\nNo Budget/Finance project found. You may need to create one.")

            elif projects_prop.get("type") == "multi_select":
                print(f"  Options: {projects_prop.get('multi_select', {}).get('options', [])}")

        else:
            print("Projects property not found in database schema")

    except requests.exceptions.RequestException as e:
        print(f"\nError fetching database schema: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    print("=== Discovering Projects Configuration ===\n")
    discover_projects()