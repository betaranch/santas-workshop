#!/usr/bin/env python3
"""
Unified Notion Manager - Everything in One Place
Simple, clear, powerful.
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import requests
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
CONFIG_FILE = CACHE_DIR / "notion_config.json"

# Create directories
CACHE_DIR.mkdir(exist_ok=True)
(CACHE_DIR / "content").mkdir(exist_ok=True)
(CACHE_DIR / "indexes").mkdir(exist_ok=True)

# Load environment
load_dotenv(BASE_DIR / ".env")

class NotionManager:
    """One class to manage everything Notion"""

    def __init__(self):
        # Get API key
        self.api_key = os.getenv("NOTION_API")
        if not self.api_key:
            print("ERROR: No NOTION_API key found in .env file")
            sys.exit(1)

        # Get workspace URL and extract page ID
        workspace_url = os.getenv("NOTION_WORKSPACE_URL", "")
        self.page_id = self._extract_page_id(workspace_url)

        # Setup API headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Load cached config if exists
        self.config = self._load_config()

    def _extract_page_id(self, url: str) -> str:
        """Extract page ID from Notion URL"""
        if not url:
            # If no URL, try to load from cached config
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('page_id', '')
            return ''

        # Extract ID from URL (last 32 chars without hyphens)
        match = re.search(r'([a-f0-9]{32})', url.replace('-', ''))
        if match:
            raw_id = match.group(1)
            # Format with hyphens
            return f"{raw_id[:8]}-{raw_id[8:12]}-{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:]}"
        return ''

    def _load_config(self) -> Dict:
        """Load cached configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self):
        """Save configuration to cache"""
        with open(CONFIG_FILE, 'w') as f:
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

    def discover(self, force: bool = False):
        """Discover all databases and save configuration"""
        if self.config.get('databases') and not force:
            print("Using cached configuration. Use --force to rediscover.")
            return

        print("Discovering Notion workspace structure...")

        if not self.page_id:
            print("ERROR: No page ID found. Check your NOTION_WORKSPACE_URL in .env")
            return

        # Search for all databases
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

        # Process databases
        databases = {}
        for db in results:
            db_id = db["id"]
            title = self._extract_title(db)

            # Categorize by title
            category = self._categorize_database(title)

            databases[category] = {
                "id": db_id,
                "title": title,
                "created": db.get("created_time"),
                "updated": db.get("last_edited_time")
            }

            print(f"  Found: {title} -> {category}")

        # Save configuration
        self.config = {
            "page_id": self.page_id,
            "discovered_at": datetime.now().isoformat(),
            "databases": databases
        }
        self._save_config()

        print(f"\nDiscovered {len(databases)} databases")
        print(f"Configuration saved to: {CONFIG_FILE}")

    def _extract_title(self, obj: Dict) -> str:
        """Extract title from Notion object"""
        if "title" in obj:
            if isinstance(obj["title"], list) and obj["title"]:
                return obj["title"][0].get("text", {}).get("content", "Untitled")
        return "Untitled"

    def _categorize_database(self, title: str) -> str:
        """Categorize database by title"""
        title_lower = title.lower()

        if "task" in title_lower:
            return "tasks"
        elif "project" in title_lower:
            return "projects"
        elif "note" in title_lower or "resource" in title_lower:
            return "notes"
        else:
            # Clean name for use as key
            return re.sub(r'[^a-z0-9_]', '_', title_lower)

    def sync(self):
        """Sync all data from Notion"""
        if not self.config.get('databases'):
            print("WARNING: No configuration found. Running discovery first...")
            self.discover()

        print("Syncing data from Notion...")

        total_pages = 0

        for category, db_info in self.config['databases'].items():
            db_id = db_info['id']
            title = db_info['title']

            print(f"\nSyncing {title}...")

            # Query database
            query_url = f"https://api.notion.com/v1/databases/{db_id}/query"
            data = {"page_size": 100}

            pages = []
            has_more = True
            next_cursor = None

            while has_more:
                if next_cursor:
                    data["start_cursor"] = next_cursor

                response = self._api_request("POST", query_url, data)
                if not response:
                    break

                pages.extend(response.get("results", []))
                has_more = response.get("has_more", False)
                next_cursor = response.get("next_cursor")

            # Process pages
            processed_pages = []
            for page in pages:
                processed = self._process_page(page)
                processed_pages.append(processed)

            # Save to cache
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cache_file = CACHE_DIR / "content" / f"{category}_{timestamp}.json"

            with open(cache_file, 'w') as f:
                json.dump(processed_pages, f, indent=2, default=str)

            print(f"  Synced {len(processed_pages)} items")
            total_pages += len(processed_pages)

        # Create indexes
        self._create_indexes()

        print(f"\nSync complete! Total items: {total_pages}")

    def _process_page(self, page: Dict) -> Dict:
        """Process a Notion page into simplified format"""
        processed = {
            "id": page["id"],
            "created": page.get("created_time"),
            "updated": page.get("last_edited_time"),
            "properties": {}
        }

        # Extract property values
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
            elif prop_type == "number":
                value = prop_data.get("number")
            elif prop_type == "checkbox":
                value = prop_data.get("checkbox")
            elif prop_type == "multi_select":
                value = [opt.get("name") for opt in prop_data.get("multi_select", [])]
            elif prop_type == "people":
                value = [p.get("id") for p in prop_data.get("people", [])]
            elif prop_type == "relation":
                value = [r.get("id") for r in prop_data.get("relation", [])]
            else:
                value = str(prop_data)

            processed["properties"][prop_name] = value

        return processed

    def _create_indexes(self):
        """Create AI-ready indexes from synced data"""
        print("\nCreating AI indexes...")

        # Load latest task data
        task_files = list((CACHE_DIR / "content").glob("tasks_*.json"))
        if not task_files:
            print("  WARNING: No task data found")
            return

        with open(sorted(task_files)[-1], 'r') as f:
            tasks = json.load(f)

        # Create indexes
        indexes = {
            "high_priority": [],
            "upcoming_deadlines": [],
            "no_status": [],
            "summary": {
                "total_tasks": len(tasks),
                "by_status": {},
                "by_priority": {}
            }
        }

        for task in tasks:
            props = task.get("properties", {})

            # High priority
            priority = props.get("Priority")
            if priority and "high" in str(priority).lower():
                indexes["high_priority"].append({
                    "name": props.get("Name"),
                    "due": props.get("Due Date"),
                    "status": props.get("Status")
                })

            # Upcoming deadlines
            due_date = props.get("Due Date")
            if due_date:
                indexes["upcoming_deadlines"].append({
                    "name": props.get("Name"),
                    "due": due_date,
                    "priority": priority
                })

            # No status
            if not props.get("Status"):
                indexes["no_status"].append(props.get("Name"))

            # Summary counts
            status = props.get("Status", "No Status")
            indexes["summary"]["by_status"][status] = indexes["summary"]["by_status"].get(status, 0) + 1

            if priority:
                indexes["summary"]["by_priority"][priority] = indexes["summary"]["by_priority"].get(priority, 0) + 1

        # Sort deadlines
        indexes["upcoming_deadlines"].sort(key=lambda x: x.get("due", "9999"))

        # Save indexes
        for index_name, index_data in indexes.items():
            index_file = CACHE_DIR / "indexes" / f"{index_name}.json"
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2, default=str)

        print(f"  Created {len(indexes)} indexes")

    def status(self):
        """Show current status"""
        print("\n=== Notion Manager Status ===\n")

        # Configuration
        if self.config:
            print("Configuration:")
            print(f"  Page ID: {self.config.get('page_id', 'Not set')}")
            print(f"  Discovered: {self.config.get('discovered_at', 'Never')}")
            print(f"  Databases: {len(self.config.get('databases', {}))}")

            if self.config.get('databases'):
                for category, info in self.config['databases'].items():
                    print(f"    - {info['title']} ({category})")
        else:
            print("ERROR: No configuration found. Run 'discover' first.")

        # Cache status
        print("\nCache Status:")
        content_files = list((CACHE_DIR / "content").glob("*.json"))
        index_files = list((CACHE_DIR / "indexes").glob("*.json"))

        print(f"  Content files: {len(content_files)}")
        print(f"  Index files: {len(index_files)}")

        # Latest sync
        if content_files:
            latest = sorted(content_files)[-1]
            mod_time = datetime.fromtimestamp(latest.stat().st_mtime)
            print(f"  Last sync: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Quick summary from indexes
        summary_file = CACHE_DIR / "indexes" / "summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary = json.load(f)
                print(f"\nTask Summary:")
                print(f"  Total tasks: {summary.get('total_tasks', 0)}")

                if summary.get('by_status'):
                    print("  By status:")
                    for status, count in summary['by_status'].items():
                        print(f"    - {status}: {count}")

    def analyze(self):
        """Show AI analysis of current state"""
        print("\n=== AI Analysis of Project State ===\n")

        # Load indexes
        high_priority = self._load_index("high_priority")
        deadlines = self._load_index("upcoming_deadlines")
        no_status = self._load_index("no_status")
        summary = self._load_index("summary")

        if not summary:
            print("ERROR: No data to analyze. Run 'sync' first.")
            return

        # Analysis
        print("KEY INSIGHTS:\n")

        # High priority items
        if high_priority:
            print(f"WARNING: {len(high_priority)} HIGH PRIORITY items need attention:")
            for item in high_priority[:5]:  # Top 5
                print(f"   • {item['name'][:50]}...")
                if item.get('due'):
                    print(f"     Due: {item['due']}")

        # Upcoming deadlines
        if deadlines:
            print(f"\n{len(deadlines)} items with deadlines:")
            for item in deadlines[:5]:  # Next 5
                print(f"   • {item['name'][:50]}...")
                print(f"     Due: {item['due']}")

        # No status items
        if no_status:
            print(f"\n{len(no_status)} items without status (need triage)")

        # Recommendations
        print("\nRECOMMENDATIONS:\n")

        if len(high_priority) > 10:
            print("1. Too many high-priority items. Consider re-prioritizing.")

        if len(no_status) > 5:
            print("2. Many items lack status. Schedule a triage session.")

        if deadlines and deadlines[0]['due'] < datetime.now().isoformat():
            print("3. You have OVERDUE items! Address immediately.")

        not_started = summary.get('by_status', {}).get('Not started', 0)
        total = summary.get('total_tasks', 1)
        if not_started / total > 0.7:
            print("4. Over 70% of tasks not started. Break down into smaller tasks.")

    def _load_index(self, name: str) -> Any:
        """Load an index file"""
        index_file = CACHE_DIR / "indexes" / f"{name}.json"
        if index_file.exists():
            with open(index_file, 'r') as f:
                return json.load(f)
        return None


def main():
    """CLI interface"""
    if len(sys.argv) < 2:
        print("""
=== Notion Manager - Simple & Powerful ===

Usage:
  python notion.py discover    # Find all databases (first time)
  python notion.py sync        # Pull latest data from Notion
  python notion.py status      # Show current status
  python notion.py analyze     # AI analysis and recommendations

Options:
  --force                      # Force rediscovery of databases

First time? Run: python notion.py discover
""")
        return

    command = sys.argv[1]
    force = "--force" in sys.argv

    # Initialize manager
    nm = NotionManager()

    # Execute command
    if command == "discover":
        nm.discover(force=force)
    elif command == "sync":
        nm.sync()
    elif command == "status":
        nm.status()
    elif command == "analyze":
        nm.analyze()
    else:
        print(f"ERROR: Unknown command: {command}")
        print("Run 'python notion.py' for help")


if __name__ == "__main__":
    main()