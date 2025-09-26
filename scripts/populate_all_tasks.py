#!/usr/bin/env python3
"""
Populate all project tasks in Notion using NotionTaskManager
Deletes generic tasks and creates specific, actionable tasks for each project
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path to import notion_task_manager
sys.path.append(str(Path(__file__).parent))
from notion_task_manager import NotionTaskManager

# Project page IDs from our synced blocks mapping
PROJECT_IDS = {
    "01_Permits_Legal": "278bc994-24ab-81b1-9fcc-d252f2d2aef9",
    "02_Space_Ops": "278bc994-24ab-8084-9709-f2c58e4f1665",
    "03_Theme_Design_Story": "278bc994-24ab-818c-acaa-c5f9bfa5a10f",
    "04_Marketing_Sales": "278bc994-24ab-819e-a7ed-d2d9b36722b1",
    "05_Team": "278bc994-24ab-8169-9f0c-cd764ec3a646",
    "06_Budget_Finance": "278bc994-24ab-80e9-8caa-f3ebf3b71cc9",
    "07_Vendors_Suppliers": "278bc994-24ab-81c6-881f-ff284e6fe7c7",
    "08_Evaluation_Scaling": "278bc994-24ab-810d-8442-c5489c07642b"
}

# All tasks organized by project
ALL_TASKS = {
    "01_Permits_Legal": [
        "Call City of Bend Planning (541-388-5580) for initial consultation",
        "Schedule fire marshal inspection for occupancy permit",
        "Apply for OLCC temporary liquor license (8 week lead time!)",
        "Get quote for $2M liability insurance policy",
        "File for temporary food service permit with Deschutes County",
        "Research if 'speakeasy' theme triggers special permits",
        "Draft customer liability waivers",
        "Confirm ADA compliance requirements",
        "Check noise ordinance restrictions for entertainment",
        "Verify parking requirements for 75 guests",
        "Get business license from City of Bend",
        "File 'doing business as' (DBA) if needed"
    ],
    "02_Space_Ops": [
        "Create scaled floor plan in Figma showing 75-person capacity",
        "Map emergency exits and post evacuation routes",
        "Design queue/waiting area for overflow",
        "Plan coat check system for winter months",
        "Calculate bathroom capacity (1 per 40 guests minimum)",
        "Design bar layout for 2 bartenders working",
        "Create storage plan for inventory",
        "Install temporary lighting for ambiance",
        "Set up POS system and test credit card processing",
        "Configure space heaters for 3,300 sq ft",
        "Build photo backdrop areas (minimum 3)",
        "Create daily setup checklist (45 min target)",
        "Design breakdown procedure (30 min target)"
    ],
    "03_Theme_Design_Story": [
        "Write backstory: 'How elves party after hours'",
        "Create 5 character profiles for key staff roles",
        "Design 'portal' entry experience from street",
        "Script surprise moments (every 15 min as per doctrine)",
        "Create playlist mixing holiday with speakeasy jazz",
        "Design menu with themed cocktail names",
        "Source or create 'elf workshop' props",
        "Plan lighting design (warm, Instagram-worthy)",
        "Create scent profile (pine, cinnamon, leather)",
        "Design take-home token (builds return visits)",
        "Write social media photo captions bank",
        "Create 'secret password' system for entry"
    ],
    "04_Marketing_Sales": [
        "Reserve Instagram handle @elfspeakeasybend",
        "Design logo incorporating elf + prohibition elements",
        "Create 'soft opening' invite list (50 VIPs)",
        "Build simple booking website on Squarespace",
        "Set up Resy or OpenTable for reservations",
        "Price structure: $15 cocktails, $65 tasting menu",
        "Create press release for Bend Bulletin",
        "Contact 10 local influencers for opening week",
        "Design corporate party packages ($2K minimum)",
        "Create gift card/merchandise program",
        "Plan Black Friday promotion",
        "Set up Google Business listing",
        "Create TikTok content calendar (3x per week)"
    ],
    "05_Team": [
        "Write job descriptions: 2 bartenders, 4 servers, 2 hosts",
        "Post jobs on Bend Craigslist and Indeed",
        "Create interview questions testing personality fit",
        "Design 2-day training program",
        "Create character sheets for staff roles",
        "Source costume elements (elf ears, vests, etc.)",
        "Set up Homebase or When I Work for scheduling",
        "Create tip pooling policy",
        "Write opening night run-of-show",
        "Plan staff pre-shift meetings",
        "Create emergency contact list",
        "Design performance incentives"
    ],
    "06_Budget_Finance": [
        "Open business checking at Chase or Wells Fargo",
        "Set up QuickBooks or Wave accounting",
        "Create weekly cash flow projection",
        "Calculate precise break-even (# covers per night)",
        "Negotiate net-30 terms with suppliers",
        "Set par levels: 3 days alcohol, 2 days food",
        "Price COGS for each cocktail (target 18-22%)",
        "Budget marketing spend ($5K opening month)",
        "Create daily manager cash-out procedure",
        "Set aside 10% contingency fund",
        "Plan for 15% credit card fee impact",
        "Create investor update template"
    ],
    "07_Vendors_Suppliers": [
        "Get quotes from 3 alcohol distributors",
        "Source local spirits from Crater Lake/Bendistillery",
        "Find commercial ice supplier (300 lbs/night)",
        "Source vintage glassware from Cheerful Redesign",
        "Get linen service quotes (tablecloths, napkins)",
        "Find local bakery for appetizer partnership",
        "Source sustainable straws and napkins",
        "Get cleaning supply wholesale account",
        "Rent sound system from Epic Entertainment",
        "Source photo booth from ShutterBooth PDX",
        "Get security system quote from ADT",
        "Find snow removal service for parking"
    ],
    "08_Evaluation_Scaling": [
        "Install Tripleseat for event tracking",
        "Create post-visit email survey",
        "Set up NPS score tracking",
        "Document all operating procedures",
        "Track hourly sales patterns",
        "Analyze cocktail mix (bestsellers)",
        "Create monthly P&L review process",
        "Plan 'traveling speakeasy' model",
        "Research Portland expansion opportunity",
        "Document IP for potential licensing",
        "Create franchise operations manual",
        "Plan year 2 improvements list"
    ]
}

class TaskPopulator:
    def __init__(self):
        self.manager = NotionTaskManager()
        self.created_tasks = []
        self.deleted_tasks = []

        # Ensure we have database configured
        if not self.manager.config.get("task_databases"):
            print("No task database found. Running discovery...")
            self.manager.discover_task_databases()

    def get_existing_tasks(self):
        """Get all existing tasks from the database"""
        print("\nFetching existing tasks...")
        tasks = self.manager.read_all_tasks()
        print(f"Found {len(tasks)} existing tasks")
        return tasks

    def delete_generic_tasks(self, existing_tasks):
        """Delete overly generic tasks"""
        generic_keywords = [
            "Research and submit all planning permits",
            "Source and quote rustic furniture",
            "Procure themed plateware",
            "Develop marketing calendar",
            "Build sales pipeline",
            "Recruit and schedule",
            "Refine financing model",
            "New Task"
        ]

        for task in existing_tasks:
            task_name = task.get("name", "")

            # Check if it's generic
            for keyword in generic_keywords:
                if keyword.lower() in task_name.lower():
                    print(f"  Archiving generic task: {task_name[:50]}...")
                    if self.manager._archive_task(task["id"]):
                        self.deleted_tasks.append(task_name)
                    time.sleep(0.35)
                    break

    def create_task(self, task_name, project_key):
        """Create a single task with project association"""

        # Calculate due date based on priority
        if project_key in ["01_Permits_Legal", "05_Team"]:
            due_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
            priority = "Medium Priority"
        elif project_key in ["02_Space_Ops", "03_Theme_Design_Story", "04_Marketing_Sales"]:
            due_date = (datetime.now() + timedelta(days=18)).strftime("%Y-%m-%d")
            priority = "Low Priority"
        elif project_key in ["06_Budget_Finance", "07_Vendors_Suppliers"]:
            due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            priority = "Low Priority"
        else:  # 08_Evaluation_Scaling
            due_date = (datetime.now() + timedelta(days=35)).strftime("%Y-%m-%d")
            priority = "Low Priority"

        # Create task using the manager
        task_id = self.manager.create_task(
            task_name=task_name,
            status="Not started",
            priority=priority,  # No high priority as requested
            due_date=due_date,
            project_id=PROJECT_IDS.get(project_key)
        )

        if task_id:
            self.created_tasks.append(task_name)
            return True
        else:
            # Try without project if it failed
            if PROJECT_IDS.get(project_key):
                task_id = self.manager.create_task(
                    task_name=task_name,
                    status="Not started",
                    priority=priority,
                    due_date=due_date
                )
                if task_id:
                    self.created_tasks.append(task_name)
                    print(f"    Created without project relation")
                    return True
            return False

    def populate_all_tasks(self):
        """Main function to populate all tasks"""
        print("\n" + "="*60)
        print("TASK POPULATION PROCESS")
        print("="*60)

        # Step 1: Get existing tasks
        existing_tasks = self.get_existing_tasks()

        # Step 2: Delete generic tasks
        print("\nStep 1: Cleaning up generic tasks...")
        self.delete_generic_tasks(existing_tasks)
        print(f"  Deleted {len(self.deleted_tasks)} generic tasks")

        # Step 3: Create new specific tasks
        print("\nStep 2: Creating specific tasks for each project...")

        for project_key, tasks in ALL_TASKS.items():
            project_name = project_key.split("_", 1)[1].replace("_", " ")
            print(f"\n{project_key} - {project_name}:")

            success_count = 0
            for task in tasks:
                print(f"  Creating: {task[:60]}...")
                if self.create_task(task, project_key):
                    success_count += 1
                time.sleep(0.35)  # Rate limiting

            print(f"  Created {success_count}/{len(tasks)} tasks")

        # Summary
        print("\n" + "="*60)
        print("POPULATION COMPLETE")
        print("="*60)
        print(f"Deleted: {len(self.deleted_tasks)} generic tasks")
        print(f"Created: {len(self.created_tasks)} specific tasks")

        # Save operations log
        self.manager.save_operations_log()

        print("\nNext steps:")
        print("1. Run 'python scripts/notion.py sync' to pull new tasks")
        print("2. Run 'python scripts/generate_tasks_md.py' to generate task files")
        print("3. Check each project's tasks.md file")


def main():
    """Run the task population"""

    print("This will:")
    print("1. Delete existing generic/duplicate tasks")
    print("2. Create ~100 specific, actionable tasks")
    print("3. Tag each task with appropriate project")
    print("4. Set medium/low priority (no high priority as requested)")

    response = input("\nContinue? (y/n): ")

    if response.lower() == 'y':
        populator = TaskPopulator()
        populator.populate_all_tasks()
    else:
        print("Cancelled")


if __name__ == "__main__":
    main()