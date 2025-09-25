#!/usr/bin/env python3
"""
README Sync Extension for Notion Integration
Bridges the gap between cached Notion data and project README files
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Project mapping between Notion and folders
PROJECT_MAP = {
    "Permits & Legal": "01_Permits_Legal",
    "Space & Ops": "02_Space_Ops",
    "Story, Theme & Design": "03_Theme_Design_Story",
    "Marketing & Sales": "04_Marketing_Sales",
    "Team": "05_Team",
    "Budget & Finance": "06_Budget_Finance",
    "Vendors & Suppliers": "07_Vendors_Suppliers",
    "Evaluation & Scaling": "08_Evaluation_Scaling"
}

class ReadmeSync:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.cache_dir = self.base_dir / "cache"
        self.docs_dir = self.base_dir / "Docs"
        self.readme_state_file = self.cache_dir / "readme_state.json"

    def load_latest_cache(self, data_type: str) -> List[Dict]:
        """Load the most recent cache file for a given type"""
        pattern = f"{data_type}_*.json"
        files = list((self.cache_dir / "content").glob(pattern))

        if not files:
            return []

        latest = sorted(files)[-1]
        with open(latest, 'r') as f:
            return json.load(f)

    def extract_tasks_by_project(self) -> Dict[str, List[Dict]]:
        """Group tasks by their project assignment"""
        tasks = self.load_latest_cache("tasks")
        projects = self.load_latest_cache("projects")

        # Create project ID to name mapping
        project_id_map = {}
        for proj in projects:
            project_id_map[proj['id']] = proj['properties'].get('Name', 'Unknown')

        # Group tasks by project
        tasks_by_project = {name: [] for name in PROJECT_MAP.keys()}

        for task in tasks:
            # Get project relations
            project_ids = task['properties'].get('Projects', [])
            if project_ids and isinstance(project_ids, list):
                for proj_id in project_ids:
                    project_name = project_id_map.get(proj_id, 'Unknown')
                    if project_name in tasks_by_project:
                        tasks_by_project[project_name].append(task)

        return tasks_by_project

    def update_readme_section(self, readme_path: Path, section: str, content: str):
        """Update a specific section in a README file"""
        if not readme_path.exists():
            print(f"README not found: {readme_path}")
            return

        with open(readme_path, 'r') as f:
            lines = f.readlines()

        # Find section boundaries
        start_marker = f"<!-- {section}_START -->\n"
        end_marker = f"<!-- {section}_END -->\n"

        # If markers don't exist, append at end
        if start_marker not in ''.join(lines):
            lines.append(f"\n{start_marker}")
            lines.append(content)
            lines.append(f"{end_marker}\n")
        else:
            # Replace content between markers
            start_idx = lines.index(start_marker)
            try:
                end_idx = lines.index(end_marker)
                # Replace content
                lines = lines[:start_idx+1] + [content] + lines[end_idx:]
            except ValueError:
                # End marker missing, just append it
                lines = lines[:start_idx+1] + [content, end_marker]

        with open(readme_path, 'w') as f:
            f.writelines(lines)

    def generate_task_section(self, tasks: List[Dict]) -> str:
        """Generate markdown for task section"""
        if not tasks:
            return "\n*No active tasks from Notion*\n\n"

        content = "\n## Active Tasks from Notion\n\n"

        # Group by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        no_priority = []

        for task in tasks:
            priority = task['properties'].get('Priority', 'None')
            task_data = {
                'name': task['properties'].get('Name', 'Unnamed'),
                'due': task['properties'].get('Due Date', 'No date'),
                'status': task['properties'].get('Status', 'Not started'),
                'id': task['id']
            }

            if 'high' in str(priority).lower():
                high_priority.append(task_data)
            elif 'med' in str(priority).lower():
                medium_priority.append(task_data)
            elif 'low' in str(priority).lower():
                low_priority.append(task_data)
            else:
                no_priority.append(task_data)

        # Write high priority
        if high_priority:
            content += "### High Priority\n"
            for t in high_priority:
                status_emoji = "✅" if "done" in t['status'].lower() else "⏳"
                content += f"- {status_emoji} {t['name']}\n"
                content += f"  - Due: {t['due']}\n"
                content += f"  - Status: {t['status']}\n"
                content += f"  - ID: `{t['id']}`\n"

        # Write medium priority
        if medium_priority:
            content += "\n### 🟡 Medium Priority\n"
            for t in medium_priority:
                status_emoji = "✅" if "done" in t['status'].lower() else "⏳"
                content += f"- {status_emoji} {t['name']}\n"
                content += f"  - Due: {t['due']}\n"

        # Write low priority
        if low_priority:
            content += "\n### 🟢 Low Priority\n"
            for t in low_priority:
                content += f"- {t['name']}\n"

        content += f"\n*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
        return content

    def update_all_readmes(self):
        """Update all project READMEs with latest Notion data"""
        print("Updating READMEs from Notion cache...")

        tasks_by_project = self.extract_tasks_by_project()

        for notion_name, folder_name in PROJECT_MAP.items():
            readme_path = self.docs_dir / folder_name / "README.md"

            if readme_path.exists():
                tasks = tasks_by_project.get(notion_name, [])
                content = self.generate_task_section(tasks)

                self.update_readme_section(readme_path, "NOTION_TASKS", content)
                print(f"✓ Updated {folder_name} ({len(tasks)} tasks)")
            else:
                print(f"⚠ Skipped {folder_name} (no README)")

        # Save state for tracking changes
        self.save_state()

    def save_state(self):
        """Save current state for change detection"""
        state = {
            "last_sync": datetime.now().isoformat(),
            "readmes_updated": list(PROJECT_MAP.values())
        }
        with open(self.readme_state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def extract_changes_from_readme(self, readme_path: Path) -> Dict:
        """Extract any manual changes made to README for pushing back"""
        # This would parse README for special markers like:
        # <!-- PUSH_TO_NOTION: task: "New task name" -->
        # <!-- UPDATE_NOTION: task_id: status: "In Progress" -->

        changes = {
            "new_tasks": [],
            "updates": [],
            "notes": []
        }

        if not readme_path.exists():
            return changes

        with open(readme_path, 'r') as f:
            content = f.read()

        # Find push directives
        new_task_pattern = r'<!-- PUSH_TO_NOTION:\s*task:\s*"([^"]+)"\s*-->'
        for match in re.finditer(new_task_pattern, content):
            changes["new_tasks"].append(match.group(1))

        # Find update directives
        update_pattern = r'<!-- UPDATE_NOTION:\s*([a-f0-9-]+):\s*(\w+):\s*"([^"]+)"\s*-->'
        for match in re.finditer(update_pattern, content):
            changes["updates"].append({
                "id": match.group(1),
                "field": match.group(2),
                "value": match.group(3)
            })

        return changes

    def scan_for_pushback(self) -> Dict:
        """Scan all READMEs for changes to push back to Notion"""
        all_changes = {}

        for folder_name in PROJECT_MAP.values():
            readme_path = self.docs_dir / folder_name / "README.md"
            changes = self.extract_changes_from_readme(readme_path)

            if any(changes.values()):
                all_changes[folder_name] = changes

        return all_changes

def main():
    """CLI for README sync operations"""
    import sys

    if len(sys.argv) < 2:
        print("""
README-Notion Sync Tool

Usage:
  python notion_readme_sync.py update    # Update READMEs from cache
  python notion_readme_sync.py check     # Check for pushback changes
  python notion_readme_sync.py status    # Show sync status

This extends notion.py to manage README files in project folders.
        """)
        return

    command = sys.argv[1]
    sync = ReadmeSync()

    if command == "update":
        sync.update_all_readmes()
        print("\n✅ README update complete")

    elif command == "check":
        changes = sync.scan_for_pushback()
        if changes:
            print("\n📤 Changes to push to Notion:")
            for folder, items in changes.items():
                print(f"\n{folder}:")
                for task in items.get("new_tasks", []):
                    print(f"  + New task: {task}")
                for update in items.get("updates", []):
                    print(f"  ↻ Update {update['id']}: {update['field']} = {update['value']}")
        else:
            print("\n✅ No changes to push")

    elif command == "status":
        if sync.readme_state_file.exists():
            with open(sync.readme_state_file, 'r') as f:
                state = json.load(f)
                print(f"\nLast sync: {state.get('last_sync', 'Never')}")
                print(f"READMEs updated: {len(state.get('readmes_updated', []))}")
        else:
            print("\n⚠ No sync history found")

if __name__ == "__main__":
    main()