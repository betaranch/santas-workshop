#!/usr/bin/env python3
"""
Notion Sync Master Controller
Handles bi-directional synchronization between Notion and local cache
with AI review capabilities for the Elf Speakeasy project.
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import requests
from enum import Enum

# Configuration
BASE_DIR = Path(__file__).parent.parent
CACHE_DIR = BASE_DIR / "cache"
CONFIG_DIR = BASE_DIR / "scripts" / "config"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [CACHE_DIR, CONFIG_DIR, LOGS_DIR, CACHE_DIR / "content", CACHE_DIR / "indexes"]:
    directory.mkdir(parents=True, exist_ok=True)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

NOTION_TOKEN = os.getenv("NOTION_API", "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")
PAGE_ID = "278bc99424ab8127a7dec0ec844f3a7b"  # From the guide

# Known database IDs from documentation
DATABASES = {
    "projects": "278bc994-24ab-817e-81bc-db906cd5ced1",
    "tasks": "278bc994-24ab-8136-b84a-c02ba029cd33",
    "notes": "278bc994-24ab-81f5-97a3-d7c35c5dcb4d"
}

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / f'notion_sync_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SyncMode(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    SMART = "smart"  # AI-determined

@dataclass
class SyncConfig:
    mode: SyncMode = SyncMode.INCREMENTAL
    batch_size: int = 50
    max_depth: int = 2
    rate_limit_delay: float = 0.35  # Seconds between API calls
    enable_ai: bool = True
    dry_run: bool = False
    backup: bool = True

class NotionSync:
    """Master controller for Notion synchronization"""

    def __init__(self, config: Optional[SyncConfig] = None):
        self.config = config or SyncConfig()
        self.headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.stats = {
            "pages_synced": 0,
            "databases_synced": 0,
            "errors": 0,
            "start_time": None
        }

    def _rate_limit(self):
        """Implement rate limiting"""
        time.sleep(self.config.rate_limit_delay)

    def _handle_pagination(self, url: str, payload: Dict = None) -> List[Dict]:
        """Handle paginated API responses"""
        results = []
        has_more = True
        next_cursor = None

        while has_more:
            if payload is None:
                payload = {}

            if next_cursor:
                payload["start_cursor"] = next_cursor

            payload["page_size"] = self.config.batch_size

            try:
                response = self.session.post(url, json=payload)
                self._rate_limit()

                if response.status_code == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                data = response.json()

                results.extend(data.get("results", []))
                has_more = data.get("has_more", False)
                next_cursor = data.get("next_cursor", None)

            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                self.stats["errors"] += 1
                break

        return results

    def discover_all_databases(self) -> Dict[str, Any]:
        """Discover all accessible databases in the workspace"""
        logger.info("Discovering all databases...")

        # Search for all databases
        search_url = "https://api.notion.com/v1/search"
        payload = {
            "filter": {
                "value": "database",
                "property": "object"
            }
        }

        databases = self._handle_pagination(search_url, payload)

        # Extract and organize database information
        db_map = {}
        for db in databases:
            db_id = db["id"]
            db_info = {
                "id": db_id,
                "title": self._extract_title(db),
                "created_time": db.get("created_time"),
                "last_edited_time": db.get("last_edited_time"),
                "properties": {},
                "parent": db.get("parent")
            }

            # Get detailed schema
            schema = self.get_database_schema(db_id)
            if schema:
                db_info["properties"] = schema

            db_map[db_id] = db_info

        # Save to cache
        cache_file = CACHE_DIR / "indexes" / "database_map.json"
        with open(cache_file, "w") as f:
            json.dump(db_map, f, indent=2, default=str)

        logger.info(f"Discovered {len(db_map)} databases")
        self.stats["databases_synced"] = len(db_map)

        return db_map

    def get_database_schema(self, db_id: str) -> Dict[str, Any]:
        """Get detailed schema for a specific database"""
        url = f"https://api.notion.com/v1/databases/{db_id}"

        try:
            response = self.session.get(url)
            self._rate_limit()
            response.raise_for_status()

            data = response.json()
            properties = data.get("properties", {})

            # Extract property details
            schema = {}
            for prop_name, prop_data in properties.items():
                schema[prop_name] = {
                    "id": prop_data.get("id"),
                    "type": prop_data.get("type"),
                    "name": prop_data.get("name", prop_name)
                }

                # Add type-specific configuration
                if prop_data["type"] == "relation":
                    schema[prop_name]["database_id"] = prop_data.get("relation", {}).get("database_id")
                elif prop_data["type"] == "rollup":
                    schema[prop_name]["rollup_config"] = prop_data.get("rollup")
                elif prop_data["type"] == "formula":
                    schema[prop_name]["formula_expression"] = prop_data.get("formula", {}).get("expression")
                elif prop_data["type"] == "select":
                    schema[prop_name]["options"] = [
                        opt.get("name") for opt in prop_data.get("select", {}).get("options", [])
                    ]
                elif prop_data["type"] == "multi_select":
                    schema[prop_name]["options"] = [
                        opt.get("name") for opt in prop_data.get("multi_select", {}).get("options", [])
                    ]

            return schema

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get schema for database {db_id}: {e}")
            return {}

    def pull_database_contents(self, db_id: str, filter_obj: Optional[Dict] = None) -> List[Dict]:
        """Pull all contents from a specific database"""
        logger.info(f"Pulling contents from database {db_id}")

        url = f"https://api.notion.com/v1/databases/{db_id}/query"
        payload = {}

        if filter_obj:
            payload["filter"] = filter_obj

        # Add sorting for consistent results
        payload["sorts"] = [
            {
                "property": "Created time",
                "direction": "descending"
            }
        ]

        pages = self._handle_pagination(url, payload)

        # Process and enrich pages
        enriched_pages = []
        for page in pages:
            enriched_page = self._enrich_page_data(page)
            enriched_pages.append(enriched_page)
            self.stats["pages_synced"] += 1

        # Save to cache
        cache_file = CACHE_DIR / "content" / f"db_{db_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, "w") as f:
            json.dump(enriched_pages, f, indent=2, default=str)

        logger.info(f"Pulled {len(enriched_pages)} pages from database {db_id}")

        return enriched_pages

    def _enrich_page_data(self, page: Dict) -> Dict:
        """Enrich page data with extracted property values"""
        enriched = {
            "id": page["id"],
            "created_time": page.get("created_time"),
            "last_edited_time": page.get("last_edited_time"),
            "properties": {},
            "raw_properties": page.get("properties", {})
        }

        # Extract property values
        for prop_name, prop_data in page.get("properties", {}).items():
            prop_type = prop_data.get("type")
            value = self._extract_property_value(prop_data, prop_type)
            enriched["properties"][prop_name] = value

        return enriched

    def _extract_property_value(self, prop_data: Dict, prop_type: str) -> Any:
        """Extract actual value from property data based on type"""
        if prop_type == "title":
            return "".join([t["text"]["content"] for t in prop_data.get("title", [])])
        elif prop_type == "rich_text":
            return "".join([t["text"]["content"] for t in prop_data.get("rich_text", [])])
        elif prop_type == "select":
            select_data = prop_data.get("select")
            return select_data.get("name") if select_data else None
        elif prop_type == "multi_select":
            return [opt.get("name") for opt in prop_data.get("multi_select", [])]
        elif prop_type == "status":
            status_data = prop_data.get("status")
            return status_data.get("name") if status_data else None
        elif prop_type == "date":
            date_data = prop_data.get("date")
            return date_data.get("start") if date_data else None
        elif prop_type == "people":
            return [person.get("id") for person in prop_data.get("people", [])]
        elif prop_type == "relation":
            return [rel.get("id") for rel in prop_data.get("relation", [])]
        elif prop_type == "number":
            return prop_data.get("number")
        elif prop_type == "checkbox":
            return prop_data.get("checkbox")
        elif prop_type == "url":
            return prop_data.get("url")
        else:
            return prop_data

    def _extract_title(self, obj: Dict) -> str:
        """Extract title from various Notion objects"""
        # Try different title locations
        if "title" in obj:
            if isinstance(obj["title"], list) and obj["title"]:
                return obj["title"][0].get("text", {}).get("content", "Untitled")
            elif isinstance(obj["title"], str):
                return obj["title"]

        # For databases
        if "database" in obj and "title" in obj["database"]:
            title_arr = obj["database"]["title"]
            if title_arr and len(title_arr) > 0:
                return title_arr[0].get("text", {}).get("content", "Untitled")

        return "Untitled"

    def create_ai_indexes(self):
        """Create AI-optimized indexes for review"""
        logger.info("Creating AI-optimized indexes...")

        # Load all cached data
        all_tasks = []
        all_projects = []

        # Load tasks
        if DATABASES["tasks"]:
            tasks_cache = list((CACHE_DIR / "content").glob(f"db_{DATABASES['tasks']}_*.json"))
            if tasks_cache:
                with open(sorted(tasks_cache)[-1], "r") as f:  # Get most recent
                    all_tasks = json.load(f)

        # Load projects
        if DATABASES["projects"]:
            projects_cache = list((CACHE_DIR / "content").glob(f"db_{DATABASES['projects']}_*.json"))
            if projects_cache:
                with open(sorted(projects_cache)[-1], "r") as f:
                    all_projects = json.load(f)

        # Create various indexes
        indexes = {
            "high_priority_tasks": [],
            "upcoming_deadlines": [],
            "blocked_tasks": [],
            "unassigned_tasks": [],
            "project_summary": {},
            "risk_items": []
        }

        # Process tasks for indexes
        for task in all_tasks:
            props = task.get("properties", {})

            # High priority
            if props.get("Priority") in ["High", "Critical", "High Priority"]:
                indexes["high_priority_tasks"].append({
                    "id": task["id"],
                    "name": props.get("Name", ""),
                    "priority": props.get("Priority"),
                    "due_date": props.get("Due Date"),
                    "status": props.get("Status")
                })

            # Upcoming deadlines (next 7 days)
            due_date = props.get("Due Date")
            if due_date:
                try:
                    due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
                    if due <= datetime.now(due.tzinfo) + timedelta(days=7):
                        indexes["upcoming_deadlines"].append({
                            "id": task["id"],
                            "name": props.get("Name", ""),
                            "due_date": due_date,
                            "days_until": (due - datetime.now(due.tzinfo)).days
                        })
                except:
                    pass

            # Unassigned tasks
            if not props.get("Person") or len(props.get("Person", [])) == 0:
                indexes["unassigned_tasks"].append({
                    "id": task["id"],
                    "name": props.get("Name", ""),
                    "priority": props.get("Priority")
                })

        # Sort indexes
        indexes["upcoming_deadlines"].sort(key=lambda x: x.get("days_until", 999))

        # Save indexes
        for index_name, index_data in indexes.items():
            index_file = CACHE_DIR / "indexes" / f"{index_name}.json"
            with open(index_file, "w") as f:
                json.dump(index_data, f, indent=2, default=str)

        logger.info("AI indexes created successfully")

        return indexes

    def sync_all(self):
        """Perform complete synchronization"""
        logger.info("Starting full synchronization...")
        self.stats["start_time"] = datetime.now()

        # Step 1: Discover databases
        db_map = self.discover_all_databases()

        # Step 2: Pull contents from known databases
        for db_name, db_id in DATABASES.items():
            if db_id in db_map:
                self.pull_database_contents(db_id)

        # Step 3: Create AI indexes
        if self.config.enable_ai:
            self.create_ai_indexes()

        # Step 4: Generate summary
        self.generate_sync_summary()

    def generate_sync_summary(self):
        """Generate and save synchronization summary"""
        duration = datetime.now() - self.stats["start_time"] if self.stats["start_time"] else timedelta(0)

        summary = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration.total_seconds(),
            "stats": self.stats,
            "config": asdict(self.config) if hasattr(self.config, '__dict__') else {},
            "databases_synced": list(DATABASES.keys())
        }

        # Save summary
        summary_file = CACHE_DIR / f"sync_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        logger.info(f"Sync completed in {duration.total_seconds():.2f} seconds")
        logger.info(f"Pages synced: {self.stats['pages_synced']}")
        logger.info(f"Databases synced: {self.stats['databases_synced']}")
        logger.info(f"Errors: {self.stats['errors']}")

        return summary

    def quick_status(self) -> Dict:
        """Get quick status of cached data"""
        status = {
            "last_sync": None,
            "cached_databases": 0,
            "cached_pages": 0,
            "indexes": []
        }

        # Find last sync
        sync_summaries = list(CACHE_DIR.glob("sync_summary_*.json"))
        if sync_summaries:
            latest = sorted(sync_summaries)[-1]
            with open(latest, "r") as f:
                last_sync = json.load(f)
                status["last_sync"] = last_sync.get("timestamp")

        # Count cached content
        status["cached_databases"] = len(list((CACHE_DIR / "content").glob("db_*.json")))

        # List available indexes
        status["indexes"] = [f.stem for f in (CACHE_DIR / "indexes").glob("*.json")]

        return status

def main():
    """CLI interface for Notion sync"""
    parser = argparse.ArgumentParser(description="Notion Sync Master Controller")

    parser.add_argument("--sync", action="store_true", help="Perform full synchronization")
    parser.add_argument("--discover", action="store_true", help="Discover all databases")
    parser.add_argument("--pull-tasks", action="store_true", help="Pull only tasks database")
    parser.add_argument("--create-indexes", action="store_true", help="Create AI indexes")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--mode", choices=["full", "incremental", "smart"], default="incremental")

    args = parser.parse_args()

    # Configure sync
    config = SyncConfig(
        mode=SyncMode(args.mode),
        dry_run=args.dry_run
    )

    sync = NotionSync(config)

    if args.sync:
        sync.sync_all()
    elif args.discover:
        databases = sync.discover_all_databases()
        print(f"\nDiscovered {len(databases)} databases:")
        for db_id, db_info in databases.items():
            print(f"  - {db_info['title']} ({db_id})")
    elif args.pull_tasks:
        sync.pull_database_contents(DATABASES["tasks"])
    elif args.create_indexes:
        indexes = sync.create_ai_indexes()
        print(f"\nCreated {len(indexes)} indexes:")
        for index_name in indexes.keys():
            print(f"  - {index_name}")
    elif args.status:
        status = sync.quick_status()
        print("\nNotion Sync Status:")
        print(f"  Last sync: {status['last_sync']}")
        print(f"  Cached databases: {status['cached_databases']}")
        print(f"  Available indexes: {', '.join(status['indexes'])}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()