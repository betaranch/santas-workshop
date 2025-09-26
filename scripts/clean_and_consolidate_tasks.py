#!/usr/bin/env python3
"""
Clean up all existing tasks and create strategic deliverables only
1. Archives all existing tasks
2. Creates new strategic tasks without priorities
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from notion_task_manager import NotionTaskManager
from dotenv import load_dotenv

load_dotenv()

# Strategic consolidated tasks by project
STRATEGIC_TASKS = {
    "01_Permits_Legal": [
        "Complete permits and licensing package",
        "Establish insurance and liability coverage",
        "Ensure venue compliance and safety"
    ],

    "02_Space_Ops": [
        "Design and finalize venue layout",
        "Establish operational systems and procedures",
        "Install equipment and infrastructure",
        "Create service and safety protocols"
    ],

    "03_Theme_Design_Story": [
        "Develop brand identity and story world",
        "Design immersive environments and experiences",
        "Create atmosphere and sensory package",
        "Produce marketing and collateral materials"
    ],

    "04_Marketing_Sales": [
        "Launch pre-sales and ticketing systems",
        "Build social media and content strategy",
        "Develop corporate and group packages",
        "Execute PR and partnership outreach"
    ],

    "05_Team": [
        "Recruit and hire staff team",
        "Develop training and character programs",
        "Create operational policies and systems",
        "Build team culture and preparation"
    ],

    "06_Budget_Finance": [
        "Finalize budget and financial model",
        "Set up accounting and tracking systems",
        "Establish banking and cash management",
        "Create reporting and monitoring processes"
    ],

    "07_Vendors_Suppliers": [
        "Source and contract F&B suppliers",
        "Procure furniture and equipment",
        "Establish vendor relationships",
        "Source decor and themed elements"
    ],

    "08_Evaluation_Scaling": [
        "Design metrics and feedback systems",
        "Develop growth and expansion plans",
        "Create investor reporting framework"
    ]
}

# Project page IDs from setup_synced_blocks
PROJECT_PAGE_IDS = {
    "01_Permits_Legal": "278bc994-24ab-81b1-9fcc-d252f2d2aef9",
    "02_Space_Ops": "278bc994-24ab-8084-9709-f2c58e4f1665",
    "03_Theme_Design_Story": "278bc994-24ab-818c-acaa-c5f9bfa5a10f",
    "04_Marketing_Sales": "278bc994-24ab-819e-a7ed-d2d9b36722b1",
    "05_Team": "278bc994-24ab-8169-9f0c-cd764ec3a646",
    "06_Budget_Finance": "278bc994-24ab-80e9-8caa-f3ebf3b71cc9",
    "07_Vendors_Suppliers": "278bc994-24ab-81c6-881f-ff284e6fe7c7",
    "08_Evaluation_Scaling": "278bc994-24ab-810d-8442-c5489c07642b"
}

def main():
    """Clean and consolidate tasks"""

    manager = NotionTaskManager()

    print("="*60)
    print("TASK CONSOLIDATION PROCESS")
    print("="*60)

    # Step 1: Archive all existing tasks
    print("\nStep 1: Archiving all existing tasks...")
    current_tasks = manager.read_all_tasks()
    print(f"Found {len(current_tasks)} tasks to archive")

    archived_count = 0
    for task in current_tasks:
        task_id = task.get("id")
        if task_id:
            try:
                url = f"https://api.notion.com/v1/pages/{task_id}"
                response = manager._api_request("PATCH", url, {"archived": True})
                if response:
                    archived_count += 1
                    print(f"  Archived: {task.get('properties', {}).get('Name', 'Unknown')}")
            except Exception as e:
                print(f"  Failed to archive: {task_id}")

    print(f"Archived {archived_count} tasks")

    # Step 2: Create new strategic tasks
    print("\nStep 2: Creating strategic tasks...")

    created_count = 0
    failed_count = 0

    for project_folder, tasks in STRATEGIC_TASKS.items():
        project_id = PROJECT_PAGE_IDS.get(project_folder)
        if not project_id:
            print(f"[WARN] No project ID for {project_folder}")
            continue

        print(f"\n{project_folder}:")
        for task_name in tasks:
            # Create task WITHOUT priority
            task_id = manager.create_task(
                task_name=task_name,
                status="Not started",
                priority=None,  # NO PRIORITY
                project_id=project_id
            )

            if task_id:
                created_count += 1
                print(f"  [OK] {task_name}")
            else:
                failed_count += 1
                print(f"  [FAIL] {task_name}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Archived: {archived_count} granular tasks")
    print(f"Created: {created_count} strategic tasks")
    if failed_count:
        print(f"Failed: {failed_count} tasks")

    print("\nTotal strategic tasks: 32")
    print("These replace the previous 112 granular tasks")

if __name__ == "__main__":
    import sys

    # Check for --yes flag to skip confirmation
    if '--yes' in sys.argv:
        main()
    else:
        response = input("\nThis will ARCHIVE all 112 existing tasks and create 32 new strategic ones.\nContinue? (y/n): ")
        if response.lower() == 'y':
            main()
        else:
            print("Cancelled.")