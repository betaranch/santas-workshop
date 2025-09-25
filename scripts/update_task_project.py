#!/usr/bin/env python3
"""
Update the Q4 budget task to assign it to the Budget & Finance project
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

def update_task_project():
    """Update the Q4 budget task to set its project"""

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

    # The task ID we created
    task_id = "279bc994-24ab-818e-bece-f5e0bee9d4dc"

    # Update URL
    url = f"https://api.notion.com/v1/pages/{task_id}"

    # Update data - add the Projects field with the correct relation ID
    # Budget & Finance project ID: 278bc994-24ab-80e9-8caa-f3ebf3b71cc9
    update_data = {
        "properties": {
            "Projects": {
                "relation": [
                    {"id": "278bc994-24ab-80e9-8caa-f3ebf3b71cc9"}
                ]
            }
        }
    }

    print(f"Updating task {task_id[:8]}...")
    print("Setting project to: 06_Budget_Finance")

    try:
        response = requests.patch(url, headers=headers, json=update_data)
        response.raise_for_status()

        result = response.json()
        print(f"\n[SUCCESS] Task updated successfully!")

        # Verify the update
        projects = result["properties"].get("Projects", {}).get("relation", [])
        if projects:
            print(f"Projects set successfully (ID: {projects[0]['id'][:8]}...)")
        else:
            print("WARNING: Projects field appears empty in response")

        return True

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Error updating task: {e}")
        if hasattr(e, 'response') and e.response:
            try:
                error_data = e.response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    print("=== Updating Q4 Budget Task Project ===\n")
    success = update_task_project()

    if success:
        print("\n[Next Steps]")
        print("1. Run 'python scripts/notion_task_manager.py read' to pull the updated task")
        print("2. Run 'python scripts/generate_tasks_md.py' to regenerate project files")
        print("3. Check Docs/06_Budget_Finance/tasks.md to verify it appears correctly")