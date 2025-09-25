#!/usr/bin/env python3
"""
Test script to create a new task in Notion
"""

import os
import sys
import json
import requests
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
TASK_CONFIG_FILE = CACHE_DIR / "task_config.json"

# Load environment
load_dotenv(BASE_DIR / ".env")

def create_test_task():
    """Create a test task for Budget & Finance"""

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

    # Load task config to get database ID
    if TASK_CONFIG_FILE.exists():
        with open(TASK_CONFIG_FILE, 'r') as f:
            config = json.load(f)

        if not config.get("task_databases"):
            print("No task databases found. Run 'python notion_task_manager.py discover' first.")
            return

        # Use the first task database
        db_id = list(config["task_databases"].keys())[0]
        db_info = config["task_databases"][db_id]

        print(f"Creating task in database: {db_info['title']}")
        print(f"Database ID: {db_id}")
    else:
        print("No configuration found. Run 'python notion_task_manager.py discover' first.")
        return

    # Create the task
    url = "https://api.notion.com/v1/pages"

    # Task for Budget & Finance
    task_data = {
        "parent": {"database_id": db_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": "Review and finalize Q4 budget allocations"
                        }
                    }
                ]
            },
            "Status": {
                "status": {
                    "name": "Not started"
                }
            },
            "Priority": {
                "select": {
                    "name": "High Priority"
                }
            },
            "Due Date": {
                "date": {
                    "start": "2025-10-07"
                }
            }
        }
    }

    print("\nCreating task: 'Review and finalize Q4 budget allocations'")
    print("Priority: High Priority")
    print("Due Date: 2025-10-07")
    print("Status: Not started")

    try:
        response = requests.post(url, headers=headers, json=task_data)
        response.raise_for_status()

        result = response.json()
        task_id = result.get("id")

        print(f"\n[SUCCESS] Task created successfully!")
        print(f"Task ID: {task_id}")
        print(f"URL: {result.get('url', 'N/A')}")

        # Save to log
        log_file = CACHE_DIR / "tasks" / f"created_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'w') as f:
            json.dump({
                "created_at": datetime.now().isoformat(),
                "task_id": task_id,
                "task_name": "Review and finalize Q4 budget allocations",
                "properties": task_data["properties"]
            }, f, indent=2)

        print(f"Log saved to: {log_file}")

        return task_id

    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Error creating task: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

if __name__ == "__main__":
    print("=== Testing Task Creation for Budget & Finance ===\n")
    task_id = create_test_task()

    if task_id:
        print("\n[Next Steps]")
        print("1. Check your Notion to see the new task")
        print("2. Run 'python scripts/notion_task_manager.py sync' to pull and categorize")
        print("3. Check Docs/06_Budget_Finance/tasks.md to see if it was filtered correctly")