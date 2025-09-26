#!/usr/bin/env python3
"""
Consolidate granular tasks into strategic deliverables
"""

import os
import json
from pathlib import Path
from datetime import datetime
from notion_task_manager import NotionTaskManager
from dotenv import load_dotenv

load_dotenv()

# Strategic consolidated tasks by project
STRATEGIC_TASKS = {
    "01_Permits_Legal": [
        "Complete all permits and licenses package (TCO, liquor, food, business)",
        "Establish liability protection and insurance coverage",
        "Ensure ADA and safety compliance for venue",
        "Legal review of customer agreements and waivers"
    ],

    "02_Space_Ops": [
        "Design and finalize venue layout for 75-person capacity",
        "Establish daily operational procedures and checklists",
        "Set up complete inventory and supply chain system",
        "Create emergency and safety protocols",
        "Develop service standards and flow management",
        "Install and test all equipment and systems"
    ],

    "03_Theme_Design_Story": [
        "Create complete brand identity and visual system",
        "Develop immersive story world and character bible",
        "Design signature experiences and surprise moments",
        "Build atmosphere package (lighting, sound, scent)",
        "Create photo-worthy installations and backdrops",
        "Design and produce all collateral materials"
    ],

    "04_Marketing_Sales": [
        "Launch pre-sales campaign (target 70% capacity)",
        "Build social media presence and content strategy",
        "Develop corporate and group sales packages",
        "Create PR and influencer outreach program",
        "Set up reservation and ticketing systems",
        "Design merchandise and upsell programs"
    ],

    "05_Team": [
        "Recruit and hire complete staff (8-10 people)",
        "Develop training program and character guides",
        "Create staff handbook and operational policies",
        "Design performance and compensation structure",
        "Build team culture and pre-opening preparation"
    ],

    "06_Budget_Finance": [
        "Finalize complete budget and financial model",
        "Set up accounting and financial tracking systems",
        "Establish cash management and banking",
        "Create financial reporting and monitoring process",
        "Develop pricing strategy and revenue optimization"
    ],

    "07_Vendors_Suppliers": [
        "Source and contract all F&B suppliers",
        "Procure furniture, fixtures, and equipment",
        "Establish vendor relationships and payment terms",
        "Source all themed decor and props",
        "Set up utilities and service contracts"
    ],

    "08_Evaluation_Scaling": [
        "Design success metrics and tracking systems",
        "Create guest feedback and improvement process",
        "Develop franchise/expansion playbook",
        "Build investor reporting framework",
        "Plan year 2 growth strategy"
    ]
}

def main():
    """Consolidate tasks in Notion"""

    # Initialize manager
    manager = NotionTaskManager()

    # Project page IDs from setup_synced_blocks
    project_page_ids = {
        "01_Permits_Legal": "278bc994-24ab-81b1-9fcc-d252f2d2aef9",
        "02_Space_Ops": "278bc994-24ab-8084-9709-f2c58e4f1665",
        "03_Theme_Design_Story": "278bc994-24ab-818c-acaa-c5f9bfa5a10f",
        "04_Marketing_Sales": "278bc994-24ab-819e-a7ed-d2d9b36722b1",
        "05_Team": "278bc994-24ab-8169-9f0c-cd764ec3a646",
        "06_Budget_Finance": "278bc994-24ab-80e9-8caa-f3ebf3b71cc9",
        "07_Vendors_Suppliers": "278bc994-24ab-81c6-881f-ff284e6fe7c7",
        "08_Evaluation_Scaling": "278bc994-24ab-810d-8442-c5489c07642b"
    }

    # Get current tasks to archive
    print("[INFO] Fetching current tasks to archive...")
    current_tasks = manager.read_all_tasks()

    # Archive existing tasks by marking them as "Archived" or deleting
    print(f"[INFO] Found {len(current_tasks)} existing tasks")

    # Clear existing tasks (mark as archived or delete)
    archived_count = 0
    for task in current_tasks:
        task_id = task.get("id")
        if task_id:
            # Archive the task using the API
            try:
                url = f"https://api.notion.com/v1/pages/{task_id}"
                response = manager._api_request("PATCH", url, {"archived": True})
                if response:
                    archived_count += 1
            except Exception as e:
                print(f"[WARN] Could not archive task {task_id}: {e}")

    print(f"[INFO] Archived {archived_count} existing granular tasks")

    # Add new strategic tasks
    created_count = 0
    failed_count = 0

    for project_folder, tasks in STRATEGIC_TASKS.items():
        print(f"\n[INFO] Adding tasks for {project_folder}...")

        # Get project ID from folder name
        project_id = project_page_ids.get(project_folder)
        if not project_id:
            print(f"[WARN] No project ID found for {project_folder}")
            continue

        for task_name in tasks:
            # Create task without priority
            task_id = manager.create_task(
                task_name=task_name,
                status="Not started",
                priority=None,  # No priority per user request
                project_id=project_id
            )

            if task_id:
                created_count += 1
                print(f"  [OK] Created: {task_name}")
            else:
                failed_count += 1
                print(f"  [ERROR] Failed: {task_name}")

    print(f"\n[SUMMARY]")
    print(f"  Created: {created_count} strategic tasks")
    print(f"  Failed: {failed_count}")
    print(f"  Total: {created_count + failed_count}")

    # Cache the new tasks
    print("\n[INFO] Caching new task structure...")
    cache_dir = Path(__file__).parent.parent / "cache" / "content"
    cache_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cache_file = cache_dir / f"strategic_tasks_{timestamp}.json"

    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(STRATEGIC_TASKS, f, indent=2, ensure_ascii=False)

    print(f"[OK] Strategic tasks cached to {cache_file.name}")

if __name__ == "__main__":
    main()