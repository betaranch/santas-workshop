#!/usr/bin/env python3
"""
Notion Task Manager - Dedicated module for task operations
Handles reading, deduplication, and updating tasks without interfering with other sync operations
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import requests
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
TASK_CACHE_DIR = CACHE_DIR / "tasks"
TASK_CONFIG_FILE = CACHE_DIR / "task_config.json"

# Create directories
CACHE_DIR.mkdir(exist_ok=True)
TASK_CACHE_DIR.mkdir(exist_ok=True)

# Load environment
load_dotenv(BASE_DIR / ".env")


class NotionTaskManager:
    """Dedicated manager for Notion tasks with read/write capabilities"""

    def __init__(self):
        # Get API key
        self.api_key = os.getenv("NOTION_API")
        if not self.api_key:
            print("ERROR: No NOTION_API key found in .env file")
            sys.exit(1)

        # Setup API headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Load task configuration
        self.config = self._load_config()

        # Track operations for audit
        self.operations_log = []

    def _load_config(self) -> Dict:
        """Load task-specific configuration"""
        if TASK_CONFIG_FILE.exists():
            with open(TASK_CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {"task_databases": {}}

    def _save_config(self):
        """Save task configuration"""
        with open(TASK_CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _api_request(self, method: str, url: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data or {})
            elif method == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data or {})
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                return None

            time.sleep(0.35)  # Rate limiting

            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._api_request(method, url, data)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"API error: {e}")
            return None

    def discover_task_databases(self) -> Dict[str, str]:
        """Discover all task databases in the workspace"""
        print("Discovering task databases...")

        search_url = "https://api.notion.com/v1/search"
        data = {"filter": {"value": "database", "property": "object"}}

        results = []
        has_more = True
        next_cursor = None

        while has_more:
            if next_cursor:
                data["start_cursor"] = next_cursor

            response = self._api_request("POST", search_url, data)
            if not response:
                break

            results.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            next_cursor = response.get("next_cursor")

        # Filter for task databases
        task_databases = {}
        for db in results:
            title = self._extract_title(db)
            if "task" in title.lower():
                db_id = db["id"]
                task_databases[db_id] = {
                    "title": title,
                    "id": db_id,
                    "created": db.get("created_time"),
                    "updated": db.get("last_edited_time")
                }
                print(f"  Found task database: {title}")

        # Update config
        self.config["task_databases"] = task_databases
        self.config["discovered_at"] = datetime.now().isoformat()
        self._save_config()

        return task_databases

    def _extract_title(self, obj: Dict) -> str:
        """Extract title from Notion object"""
        if "title" in obj:
            if isinstance(obj["title"], list) and obj["title"]:
                return obj["title"][0].get("text", {}).get("content", "Untitled")
        return "Untitled"

    def read_all_tasks(self, db_id: Optional[str] = None) -> List[Dict]:
        """Read all tasks from specified database or all task databases"""
        all_tasks = []

        if db_id:
            databases = {db_id: self.config["task_databases"].get(db_id)}
        else:
            databases = self.config["task_databases"]

        for database_id, db_info in databases.items():
            if not db_info:
                continue

            print(f"Reading tasks from {db_info.get('title', 'Unknown')}...")

            query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
            data = {"page_size": 100}

            has_more = True
            next_cursor = None

            while has_more:
                if next_cursor:
                    data["start_cursor"] = next_cursor

                response = self._api_request("POST", query_url, data)
                if not response:
                    break

                pages = response.get("results", [])
                for page in pages:
                    task = self._process_task_page(page)
                    task["database_id"] = database_id
                    all_tasks.append(task)

                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")

        print(f"Total tasks read: {len(all_tasks)}")
        return all_tasks

    def _process_task_page(self, page: Dict) -> Dict:
        """Process a task page into simplified format"""
        task = {
            "id": page["id"],
            "created": page.get("created_time"),
            "updated": page.get("last_edited_time"),
            "archived": page.get("archived", False),
            "properties": {}
        }

        # Extract all properties
        for prop_name, prop_data in page.get("properties", {}).items():
            prop_type = prop_data.get("type")

            if prop_type == "title":
                value = "".join([t["text"]["content"] for t in prop_data.get("title", [])])
            elif prop_type == "rich_text":
                value = "".join([t["text"]["content"] for t in prop_data.get("rich_text", [])])
            elif prop_type == "select":
                select = prop_data.get("select")
                value = select.get("name") if select else None
            elif prop_type == "status":
                status = prop_data.get("status")
                value = status.get("name") if status else None
            elif prop_type == "date":
                date = prop_data.get("date")
                value = date.get("start") if date else None
            elif prop_type == "people":
                value = [p.get("id") for p in prop_data.get("people", [])]
            elif prop_type == "relation":
                value = [r.get("id") for r in prop_data.get("relation", [])]
            else:
                value = prop_data

            task["properties"][prop_name] = value

        return task

    def find_duplicates(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Find duplicate tasks based on task name and project"""
        duplicates = {}
        task_signatures = {}

        for task in tasks:
            # Create signature from task name and project
            name = task["properties"].get("Name", "")
            projects = task["properties"].get("Projects", [])

            # Create a unique signature
            signature = f"{name}|{','.join(sorted(projects))}"

            if signature in task_signatures:
                if signature not in duplicates:
                    duplicates[signature] = [task_signatures[signature]]
                duplicates[signature].append(task)
            else:
                task_signatures[signature] = task

        # Filter to only actual duplicates
        actual_duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}

        return actual_duplicates

    def deduplicate_tasks(self, dry_run: bool = True) -> Dict:
        """Remove duplicate tasks, keeping the most recent"""
        print("\nStarting deduplication process...")

        # Read all tasks
        all_tasks = self.read_all_tasks()

        # Find duplicates
        duplicates = self.find_duplicates(all_tasks)

        if not duplicates:
            print("No duplicates found!")
            return {"status": "success", "duplicates_found": 0, "removed": 0}

        print(f"Found {len(duplicates)} sets of duplicate tasks")

        removed_count = 0
        kept_tasks = []
        removed_tasks = []

        for signature, task_group in duplicates.items():
            # Sort by creation time, keep the newest
            task_group.sort(key=lambda x: x["created"], reverse=True)

            keep_task = task_group[0]
            remove_tasks = task_group[1:]

            task_name = keep_task["properties"].get("Name", "Unknown")
            print(f"\nTask: {task_name}")
            print(f"  Keeping: {keep_task['id']} (created: {keep_task['created']})")

            for task in remove_tasks:
                print(f"  Removing: {task['id']} (created: {task['created']})")

                if not dry_run:
                    # Archive the duplicate task
                    success = self._archive_task(task["id"])
                    if success:
                        removed_count += 1
                        removed_tasks.append(task)
                else:
                    removed_count += 1
                    removed_tasks.append(task)

            kept_tasks.append(keep_task)

        # Save deduplication report
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "duplicates_found": len(duplicates),
            "tasks_removed": removed_count,
            "kept_tasks": kept_tasks,
            "removed_tasks": removed_tasks
        }

        report_file = TASK_CACHE_DIR / f"dedup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        if dry_run:
            print(f"\nDRY RUN: Would remove {removed_count} duplicate tasks")
            print(f"Report saved to: {report_file}")
        else:
            print(f"\nRemoved {removed_count} duplicate tasks")
            print(f"Report saved to: {report_file}")

        return report

    def _archive_task(self, task_id: str) -> bool:
        """Archive (soft delete) a task in Notion"""
        url = f"https://api.notion.com/v1/pages/{task_id}"
        data = {"archived": True}

        response = self._api_request("PATCH", url, data)

        if response:
            self.operations_log.append({
                "action": "archive",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
            return True
        else:
            self.operations_log.append({
                "action": "archive",
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "success": False
            })
            return False

    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update a task's properties"""
        url = f"https://api.notion.com/v1/pages/{task_id}"

        # Format properties for Notion API
        properties = {}
        for key, value in updates.items():
            if key == "Name":
                properties[key] = {"title": [{"text": {"content": value}}]}
            elif key == "Status":
                properties[key] = {"status": {"name": value}}
            elif key == "Priority":
                properties[key] = {"select": {"name": value}}
            elif key == "Due Date":
                properties[key] = {"date": {"start": value}}
            # Add more property types as needed

        data = {"properties": properties}

        response = self._api_request("PATCH", url, data)

        if response:
            self.operations_log.append({
                "action": "update",
                "task_id": task_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
            return True
        else:
            self.operations_log.append({
                "action": "update",
                "task_id": task_id,
                "updates": updates,
                "timestamp": datetime.now().isoformat(),
                "success": False
            })
            return False

    def create_task(self, task_name: str, status: str = "Not started",
                   priority: str = None, due_date: str = None,
                   project_id: str = None) -> Optional[str]:
        """Create a new task in the database"""
        # Get first database ID if not specified
        if not self.config.get("task_databases"):
            print("No task databases configured. Run 'discover' first.")
            return None

        db_id = list(self.config["task_databases"].keys())[0]
        url = "https://api.notion.com/v1/pages"

        # Build task properties
        task_data = {
            "parent": {"database_id": db_id},
            "properties": {
                "Name": {
                    "title": [{"text": {"content": task_name}}]
                },
                "Status": {
                    "status": {"name": status}
                }
            }
        }

        # Add optional properties
        if priority:
            task_data["properties"]["Priority"] = {
                "select": {"name": priority}
            }

        if due_date:
            task_data["properties"]["Due Date"] = {
                "date": {"start": due_date}
            }

        if project_id:
            task_data["properties"]["Projects"] = {
                "relation": [{"id": project_id}]
            }

        response = self._api_request("POST", url, task_data)

        if response:
            task_id = response.get("id")
            self.operations_log.append({
                "action": "create",
                "task_id": task_id,
                "task_name": task_name,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
            return task_id
        else:
            self.operations_log.append({
                "action": "create",
                "task_name": task_name,
                "timestamp": datetime.now().isoformat(),
                "success": False
            })
            return None

    def save_operations_log(self):
        """Save the operations log for audit"""
        if self.operations_log:
            log_file = TASK_CACHE_DIR / f"operations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w') as f:
                json.dump(self.operations_log, f, indent=2)
            print(f"Operations log saved to: {log_file}")

    def generate_project_task_files(self):
        """Generate filtered task.md files for each project folder"""
        print("\nGenerating project task files...")

        # Project keyword mappings
        project_keywords = {
            "01_Permits_Legal": ["permit", "legal", "license", "TCO", "zoning", "compliance", "insurance"],
            "02_Space_Ops": ["space", "operation", "layout", "furniture", "floor plan", "setup", "venue", "cocktail", "drink", "appetizer", "menu"],
            "03_Theme_Design_Story": ["theme", "design", "story", "vignette", "decoration", "figma", "aesthetic", "hearth"],
            "04_Marketing_Sales": ["marketing", "sales", "social", "instagram", "tiktok", "promotion", "pipeline", "corporate", "flask", "merch"],
            "05_Team": ["staff", "team", "recruit", "hiring", "schedule", "training", "bartender", "wait staff"],
            "06_Budget_Finance": ["budget", "finance", "expense", "revenue", "cost", "financing", "model", "track"],
            "07_Vendors_Suppliers": ["vendor", "supplier", "procure", "source", "quote", "glassware", "plateware", "props", "furniture"],
            "08_Evaluation_Scaling": ["evaluation", "scaling", "metrics", "growth", "expansion", "feedback", "analysis"]
        }

        # Read all tasks
        all_tasks = self.read_all_tasks()

        # Categorize tasks
        categorized_tasks = {project: [] for project in project_keywords.keys()}
        categorized_tasks["00_Uncategorized"] = []

        for task in all_tasks:
            task_name = task["properties"].get("Name", "")
            task_text = str(task_name).lower()

            matched = False
            for project, keywords in project_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in task_text:
                        categorized_tasks[project].append(task)
                        matched = True
                        break
                if matched:
                    break

            if not matched:
                categorized_tasks["00_Uncategorized"].append(task)

        # Generate task files for each project
        docs_dir = BASE_DIR / "Docs"

        for project, tasks in categorized_tasks.items():
            project_dir = docs_dir / project
            project_dir.mkdir(exist_ok=True)

            task_file = project_dir / "tasks.md"

            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(f"# Tasks for {project.replace('_', ' ')}\n\n")
                f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")

                if not tasks:
                    f.write("No tasks currently assigned to this project.\n")
                else:
                    # Group by priority
                    high_priority = [t for t in tasks if t["properties"].get("Priority") == "High Priority"]
                    normal_priority = [t for t in tasks if t["properties"].get("Priority") != "High Priority"]

                    if high_priority:
                        f.write("## 🔴 High Priority\n\n")
                        for task in high_priority:
                            self._write_task_to_file(f, task)

                    if normal_priority:
                        f.write("## Regular Tasks\n\n")
                        for task in normal_priority:
                            self._write_task_to_file(f, task)

                print(f"  Generated {project}/tasks.md with {len(tasks)} tasks")

        print(f"\nGenerated task files for {len(categorized_tasks)} projects")

    def _write_task_to_file(self, file, task):
        """Write a single task to the markdown file"""
        props = task["properties"]
        name = props.get("Name", "Untitled")
        status = props.get("Status", "No status")
        due_date = props.get("Due Date")
        priority = props.get("Priority", "Normal")

        file.write(f"### {name}\n")
        file.write(f"- **ID**: {task['id']}\n")
        file.write(f"- **Status**: {status}\n")
        file.write(f"- **Priority**: {priority}\n")
        if due_date:
            file.write(f"- **Due**: {due_date}\n")
        file.write("\n")


def main():
    """CLI interface for task management"""
    if len(sys.argv) < 2:
        print("""
=== Notion Task Manager ===

Usage:
  python notion_task_manager.py discover      # Discover task databases
  python notion_task_manager.py read          # Read all tasks
  python notion_task_manager.py duplicates    # Find duplicate tasks
  python notion_task_manager.py dedupe        # Remove duplicates (dry run)
  python notion_task_manager.py dedupe --run  # Remove duplicates (actual)

Example workflow:
  1. python notion_task_manager.py discover
  2. python notion_task_manager.py duplicates
  3. python notion_task_manager.py dedupe       # Review what will be removed
  4. python notion_task_manager.py dedupe --run # Actually remove duplicates
""")
        return

    command = sys.argv[1]

    # Initialize manager
    tm = NotionTaskManager()

    # Execute command
    if command == "discover":
        tm.discover_task_databases()

    elif command == "read":
        tasks = tm.read_all_tasks()

        # Save to cache
        cache_file = TASK_CACHE_DIR / f"all_tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, 'w') as f:
            json.dump(tasks, f, indent=2, default=str)

        print(f"Tasks saved to: {cache_file}")

    elif command == "duplicates":
        tasks = tm.read_all_tasks()
        duplicates = tm.find_duplicates(tasks)

        if duplicates:
            print(f"\nFound {len(duplicates)} sets of duplicate tasks:")
            for signature, task_group in duplicates.items():
                task_name = task_group[0]["properties"].get("Name", "Unknown")
                print(f"  • {task_name}: {len(task_group)} copies")
        else:
            print("No duplicates found!")

    elif command == "dedupe":
        dry_run = "--run" not in sys.argv
        report = tm.deduplicate_tasks(dry_run=dry_run)

        if not dry_run:
            tm.save_operations_log()

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()