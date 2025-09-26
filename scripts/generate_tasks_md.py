#!/usr/bin/env python3
"""
Generate tasks.md files for each project folder
Filters tasks from the cached Notion tasks database
"""

import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class TaskGenerator:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / "Docs"
        self.cache_dir = self.base_dir / "cache"

        # Project keyword mappings - expanded for better coverage
        self.project_keywords = {
            "01_Permits_Legal": [
                "permit", "legal", "license", "TCO", "zoning", "compliance", "insurance",
                "DBA", "liability", "waiver", "noise ordinance", "city of bend", "planning",
                "ordinance", "filing", "business as"
            ],
            "02_Space_Ops": [
                "space", "operation", "layout", "furniture", "floor plan", "setup", "venue",
                "run-of-show", "parking", "bathroom", "capacity", "coat check", "emergency",
                "exit", "evacuation", "cleaning", "storage", "inventory", "POS system",
                "credit card processing", "manager", "procedure", "par level", "alcohol",
                "food", "covers"
            ],
            "03_Theme_Design_Story": [
                "theme", "design", "story", "vignette", "decoration", "figma", "aesthetic",
                "password", "secret", "scent", "profile", "playlist", "jazz", "holiday",
                "surprise", "moments", "photo", "backdrop", "lighting", "ambiance",
                "pine", "cinnamon", "leather"
            ],
            "04_Marketing_Sales": [
                "marketing", "sales", "social", "instagram", "tiktok", "promotion", "pipeline",
                "corporate", "google business", "influencer", "press release", "bulletin",
                "soft opening", "VIP", "invite", "reservation", "resy", "opentable",
                "opening week", "press", "listing"
            ],
            "05_Team": [
                "staff", "team", "recruit", "hiring", "schedule", "training", "bartender",
                "wait staff", "emergency contact", "interview", "personality fit", "job",
                "craigslist", "indeed", "tip pooling", "homebase", "when i work",
                "scheduling", "policy", "questions"
            ],
            "06_Budget_Finance": [
                "budget", "finance", "expense", "revenue", "cost", "financing", "model",
                "track", "P&L", "profit", "loss", "credit card fee", "contingency fund",
                "cash-out", "cash flow", "break-even", "quickbooks", "wave", "accounting",
                "business checking", "chase", "wells fargo", "monthly", "weekly",
                "projection", "15%", "10%"
            ],
            "07_Vendors_Suppliers": [
                "vendor", "supplier", "procure", "source", "quote", "glassware", "plateware",
                "props", "snow removal", "sound system", "epic entertainment", "rent",
                "wholesale", "supply", "cleaning supply", "net-30", "terms", "ADT",
                "security system", "linen", "ice", "spirits", "crater lake", "bendistillery",
                "shutterboot", "sustainable", "straws", "napkins", "cheerful redesign"
            ],
            "08_Evaluation_Scaling": [
                "evaluation", "scaling", "metrics", "growth", "expansion", "feedback",
                "analysis", "year 2", "improvement", "investor update", "IP", "intellectual",
                "property", "licensing", "document", "procedures", "post-visit", "survey",
                "email", "NPS", "tripleseat", "event tracking", "portland"
            ]
        }

        self.load_tasks()

    def load_tasks(self):
        """Load tasks from cached Notion data"""
        # Try content directory first (from notion.py sync) - most up-to-date
        content_dir = self.cache_dir / "content"
        if content_dir.exists():
            # Look for tasks_*.json files from notion.py sync
            task_files = sorted(content_dir.glob("tasks_*.json"))
            if task_files:
                # Use the most recent tasks file
                latest_file = task_files[-1]
                print(f"[INFO] Loading tasks from {latest_file.name}")
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                print(f"[INFO] Loaded {len(self.tasks)} tasks from cache")
                return

        # Fallback to tasks directory
        tasks_dir = self.cache_dir / "tasks"
        if tasks_dir.exists():
            task_files = sorted(tasks_dir.glob("all_tasks_*.json"))
            if task_files:
                # Use the most recent all_tasks file
                latest_file = task_files[-1]
                print(f"[INFO] Loading tasks from {latest_file.name}")
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                return

        # Final fallback
        content_dir = self.cache_dir / "content"
        if not content_dir.exists():
            print("[ERROR] No cache/content directory. Run 'python scripts/notion.py sync' first.")
            self.tasks = []
            return

        # Look for Tasks database files (db_278bc994-24ab-8136-b84a-c02ba029cd33 is Tasks)
        task_files = sorted(content_dir.glob("db_278bc994-24ab-8136-b84a-c02ba029cd33_*.json"))

        if not task_files:
            print("[ERROR] No cached Tasks data. Run 'python scripts/notion.py sync' first.")
            self.tasks = []
            return

        # Use the most recent file
        tasks_file = task_files[-1]

        with open(tasks_file, 'r') as f:
            data = json.load(f)
            # The tasks are stored directly as a list
            self.tasks = data if isinstance(data, list) else []

        print(f"[INFO] Loaded {len(self.tasks)} tasks from cache")

    def categorize_task(self, task):
        """Determine which project(s) a task belongs to"""
        # Extract task name from properties
        task_name = ""
        props = task.get("properties", {})
        if "Name" in props:
            task_name = props["Name"]
        elif "Task" in props:
            task_name = props["Task"]

        # Handle different property formats
        if isinstance(task_name, dict):
            # Might be a rich text property
            if "title" in task_name:
                texts = task_name.get("title", [])
                if texts and isinstance(texts, list):
                    task_name = texts[0].get("text", {}).get("content", "") if texts else ""
            elif "rich_text" in task_name:
                texts = task_name.get("rich_text", [])
                if texts and isinstance(texts, list):
                    task_name = texts[0].get("text", {}).get("content", "") if texts else ""

        task_text = str(task_name).lower()
        categories = []

        for project, keywords in self.project_keywords.items():
            for keyword in keywords:
                if keyword.lower() in task_text:
                    categories.append(project)
                    break  # One keyword match is enough per project

        # If no category found, check for general keywords
        if not categories:
            if any(word in task_text for word in ["cocktail", "drink", "appetizer", "menu"]):
                categories.append("02_Space_Ops")  # Operations includes F&B
            elif any(word in task_text for word in ["flask", "merch", "merchandise"]):
                categories.append("04_Marketing_Sales")  # Merch is marketing

        return categories if categories else ["00_Uncategorized"]

    def format_task_markdown(self, tasks, project_name):
        """Format tasks as markdown"""
        if not tasks:
            return f"# Tasks for {project_name}\n\n*No tasks currently assigned to this project.*\n"

        md = f"# Tasks for {project_name}\n\n"
        md += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        md += f"**Total Tasks: {len(tasks)}**\n\n"
        md += f"## Tasks\n\n"

        for task in tasks:
            md += self.format_single_task(task)

        return md

    def format_single_task(self, task):
        """Format a single task"""
        props = task.get("properties", {})

        # Extract task name
        task_name = self.extract_property_text(props, "Name") or "Untitled Task"

        # Extract status
        status = props.get("Status", "Not started")
        if isinstance(status, dict):
            status = status.get("status", {}).get("name", "Not started") if "status" in status else status
        elif isinstance(status, str):
            pass  # Already a string

        status_emoji = {
            "Not started": "⬜",
            "Not Started": "⬜",
            "In Progress": "🔄",
            "In progress": "🔄",
            "Complete": "✅",
            "Completed": "✅",
            "Done": "✅",
            "Blocked": "🚫"
        }.get(status, "⬜")

        md = f"### {status_emoji} {task_name}\n\n"
        md += "---\n\n"
        return md

    def extract_property_text(self, props, key):
        """Extract text from various property formats"""
        if key not in props:
            return None

        prop = props[key]

        if isinstance(prop, str):
            return prop
        elif isinstance(prop, dict):
            # Title or rich text property
            if "title" in prop:
                texts = prop.get("title", [])
                if texts and isinstance(texts, list):
                    return texts[0].get("text", {}).get("content", "") if texts else None
            elif "rich_text" in prop:
                texts = prop.get("rich_text", [])
                if texts and isinstance(texts, list):
                    return texts[0].get("text", {}).get("content", "") if texts else None
            elif "select" in prop:
                return prop["select"].get("name")

        return str(prop) if prop else None

    def generate_all_tasks_files(self):
        """Generate tasks.md for all projects"""
        # Categorize all tasks
        project_tasks = {project: [] for project in self.project_keywords.keys()}
        project_tasks["00_Uncategorized"] = []

        for task in self.tasks:
            categories = self.categorize_task(task)
            for category in categories:
                if category in project_tasks:
                    project_tasks[category].append(task)

        # Generate files
        for project, tasks in project_tasks.items():
            if project == "00_Uncategorized" and not tasks:
                continue  # Skip if no uncategorized tasks

            # Determine project name
            project_names = {
                "01_Permits_Legal": "Permits & Legal",
                "02_Space_Ops": "Space & Operations",
                "03_Theme_Design_Story": "Theme, Design & Story",
                "04_Marketing_Sales": "Marketing & Sales",
                "05_Team": "Team",
                "06_Budget_Finance": "Budget & Finance",
                "07_Vendors_Suppliers": "Vendors & Suppliers",
                "08_Evaluation_Scaling": "Evaluation & Scaling",
                "00_Uncategorized": "Uncategorized"
            }

            project_name = project_names.get(project, project)

            # Create directory if needed
            if project == "00_Uncategorized":
                project_dir = self.docs_dir / "00_Uncategorized"
            else:
                project_dir = self.docs_dir / project

            project_dir.mkdir(exist_ok=True)

            # Generate markdown
            markdown = self.format_task_markdown(tasks, project_name)

            # Write file
            tasks_file = project_dir / "tasks.md"
            with open(tasks_file, 'w', encoding='utf-8') as f:
                f.write(markdown)

            print(f"[OK] Generated {tasks_file} ({len(tasks)} tasks)")

        # Summary
        total_tasks = sum(len(tasks) for tasks in project_tasks.values())
        categorized = total_tasks - len(project_tasks.get("00_Uncategorized", []))

        print(f"\n[SUMMARY]")
        print(f"  Total tasks: {len(self.tasks)}")
        print(f"  Categorized: {categorized}")
        print(f"  Uncategorized: {len(project_tasks.get('00_Uncategorized', []))}")


def main():
    generator = TaskGenerator()

    if generator.tasks:
        generator.generate_all_tasks_files()
    else:
        print("[INFO] First, sync tasks from Notion:")
        print("  python scripts/notion.py sync")


if __name__ == "__main__":
    main()