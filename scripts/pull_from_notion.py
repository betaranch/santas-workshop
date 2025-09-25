#!/usr/bin/env python3
"""
Pull content from Notion synced blocks back to README.md files
Creates backups before overwriting to prevent data loss
"""

import os
import json
import time
import re
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv
import shutil

load_dotenv()

class NotionToReadmeSync:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API")
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / "Docs"
        self.cache_dir = self.base_dir / "cache"
        self.backup_dir = self.base_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Load synced block mappings
        self.load_mappings()

    def load_mappings(self):
        """Load synced block mappings"""
        mapping_file = self.cache_dir / "synced_blocks.json"

        if not mapping_file.exists():
            print("[ERROR] No synced block mappings found. Run setup_synced_blocks.py first.")
            exit(1)

        with open(mapping_file, 'r') as f:
            self.mappings = json.load(f)

    def get_block_children(self, block_id, cursor=None):
        """Recursively get all children of a block"""
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        params = {"page_size": 100}

        if cursor:
            params["start_cursor"] = cursor

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            print(f"[ERROR] Failed to get block children: {response.status_code}")
            return []

        data = response.json()
        blocks = data.get("results", [])

        # If there are more pages, get them
        if data.get("has_more"):
            time.sleep(0.35)  # Rate limiting
            blocks.extend(self.get_block_children(block_id, data.get("next_cursor")))

        return blocks

    def notion_blocks_to_markdown(self, blocks):
        """Convert Notion blocks to markdown format"""
        markdown = []
        in_list = False
        list_counter = 0

        for block in blocks:
            block_type = block.get("type")

            # Skip callouts that are sync markers
            if block_type == "callout":
                text = self.extract_text_from_block(block)
                if "Last synced:" in text or "synced at:" in text:
                    continue

            # Skip dividers after sync markers
            if block_type == "divider" and len(markdown) == 0:
                continue

            # Convert block to markdown
            md_line = self.convert_block_to_markdown(block)

            # Handle list continuity
            if block_type in ["bulleted_list_item", "numbered_list_item"]:
                if block_type == "numbered_list_item":
                    if not in_list or in_list != "numbered":
                        list_counter = 1
                        in_list = "numbered"
                    else:
                        list_counter += 1
                    md_line = f"{list_counter}. {md_line.lstrip('- ')}"
                else:
                    in_list = "bulleted"
            else:
                if in_list:
                    in_list = False
                    list_counter = 0
                    if md_line and not md_line.startswith("#"):
                        markdown.append("")  # Add blank line after lists

            if md_line is not None:
                markdown.append(md_line)

        return "\n".join(markdown)

    def convert_block_to_markdown(self, block):
        """Convert a single Notion block to markdown"""
        block_type = block.get("type")

        if block_type == "paragraph":
            text = self.extract_rich_text(block.get("paragraph", {}).get("rich_text", []))
            return text if text else ""

        elif block_type == "heading_1":
            text = self.extract_rich_text(block.get("heading_1", {}).get("rich_text", []))
            return f"# {text}" if text else ""

        elif block_type == "heading_2":
            text = self.extract_rich_text(block.get("heading_2", {}).get("rich_text", []))
            # Skip sync markers
            if "[SYNC]" in text or "Documentation" in text and "📁" in text:
                return None
            return f"## {text}" if text else ""

        elif block_type == "heading_3":
            text = self.extract_rich_text(block.get("heading_3", {}).get("rich_text", []))
            return f"### {text}" if text else ""

        elif block_type == "bulleted_list_item":
            text = self.extract_rich_text(block.get("bulleted_list_item", {}).get("rich_text", []))
            return f"- {text}" if text else ""

        elif block_type == "numbered_list_item":
            text = self.extract_rich_text(block.get("numbered_list_item", {}).get("rich_text", []))
            return f"- {text}" if text else ""  # Will be fixed by list counter

        elif block_type == "code":
            code_block = block.get("code", {})
            text = self.extract_rich_text(code_block.get("rich_text", []))
            language = code_block.get("language", "")
            if language == "plain text":
                language = ""
            return f"```{language}\n{text}\n```"

        elif block_type == "quote":
            text = self.extract_rich_text(block.get("quote", {}).get("rich_text", []))
            return f"> {text}" if text else ""

        elif block_type == "divider":
            return "---"

        elif block_type == "callout":
            callout = block.get("callout", {})
            text = self.extract_rich_text(callout.get("rich_text", []))
            # Convert callouts to blockquotes with emoji
            icon = callout.get("icon", {})
            if icon.get("type") == "emoji":
                emoji = icon.get("emoji", "📌")
                return f"> {emoji} {text}"
            return f"> {text}"

        elif block_type == "toggle":
            toggle = block.get("toggle", {})
            text = self.extract_rich_text(toggle.get("rich_text", []))
            # Convert toggle to details/summary (GitHub markdown)
            children = self.get_block_children(block.get("id"))
            if children:
                child_md = self.notion_blocks_to_markdown(children)
                return f"<details>\n<summary>{text}</summary>\n\n{child_md}\n</details>"
            return f"**{text}**"

        elif block_type == "synced_block":
            # Skip synced block containers
            return None

        else:
            # Unknown block type - try to extract text
            return f"[{block_type}]"

    def extract_rich_text(self, rich_text_array):
        """Extract and format text from Notion rich text array"""
        if not rich_text_array:
            return ""

        result = []
        for text_obj in rich_text_array:
            text = text_obj.get("text", {}).get("content", "")
            annotations = text_obj.get("annotations", {})

            # Apply formatting
            if annotations.get("code"):
                text = f"`{text}`"
            else:
                if annotations.get("bold"):
                    text = f"**{text}**"
                if annotations.get("italic"):
                    text = f"*{text}*"
                if annotations.get("strikethrough"):
                    text = f"~~{text}~~"

            # Handle links
            if text_obj.get("text", {}).get("link"):
                url = text_obj["text"]["link"].get("url", "")
                text = f"[{text}]({url})"

            result.append(text)

        return "".join(result)

    def extract_text_from_block(self, block):
        """Extract plain text from any block type"""
        block_type = block.get("type")

        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
        elif block_type == "callout":
            rich_text = block.get("callout", {}).get("rich_text", [])
        elif block_type == "quote":
            rich_text = block.get("quote", {}).get("rich_text", [])
        elif block_type == "bulleted_list_item":
            rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        elif block_type == "numbered_list_item":
            rich_text = block.get("numbered_list_item", {}).get("rich_text", [])
        else:
            return ""

        return "".join([t.get("text", {}).get("content", "") for t in rich_text])

    def backup_file(self, file_path):
        """Create a backup of the file before overwriting"""
        if not file_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"

        # Create project-specific backup directory
        project_name = file_path.parent.name
        project_backup_dir = self.backup_dir / project_name
        project_backup_dir.mkdir(exist_ok=True)

        backup_path = project_backup_dir / backup_name
        shutil.copy2(file_path, backup_path)

        return backup_path

    def check_for_conflicts(self, file_path, new_content):
        """Check if there are potential conflicts"""
        if not file_path.exists():
            return False, "File doesn't exist yet"

        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()

        # Simple conflict detection
        if current_content == new_content:
            return False, "Content identical"

        # Check if file was modified recently (last 30 minutes)
        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        time_diff = datetime.now() - mod_time

        if time_diff.total_seconds() < 1800:  # 30 minutes
            return True, f"File modified {int(time_diff.total_seconds() / 60)} minutes ago"

        return False, "No recent modifications"

    def pull_project(self, folder_name, force=False):
        """Pull content from Notion for a specific project"""
        if folder_name not in self.mappings:
            print(f"[ERROR] Project {folder_name} not found in mappings")
            return False

        block_id = self.mappings[folder_name].get("synced_block_id")
        if not block_id:
            print(f"[ERROR] No synced block ID for {folder_name}")
            return False

        print(f"\n[PULL] {folder_name}")
        print(f"  Block ID: {block_id[:8]}...")

        # Get content from Notion
        blocks = self.get_block_children(block_id)

        if not blocks:
            print(f"  [WARN] No content found in Notion")
            return False

        print(f"  Retrieved {len(blocks)} blocks from Notion")

        # Convert to markdown
        markdown_content = self.notion_blocks_to_markdown(blocks)

        # Target README file
        readme_path = self.docs_dir / folder_name / "README.md"

        # Check for conflicts
        has_conflict, conflict_reason = self.check_for_conflicts(readme_path, markdown_content)

        if has_conflict and not force:
            print(f"  [WARN] Potential conflict: {conflict_reason}")
            response = input("  Overwrite anyway? (y/n/d for diff): ").lower()

            if response == 'd':
                # Show diff
                if readme_path.exists():
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        current = f.read()
                    print("\n  --- Current (first 500 chars) ---")
                    print(current[:500])
                    print("\n  --- From Notion (first 500 chars) ---")
                    print(markdown_content[:500])
                    response = input("\n  Overwrite? (y/n): ").lower()

            if response != 'y':
                print("  [SKIP] Skipping due to conflict")
                return False

        # Create backup
        if readme_path.exists():
            backup_path = self.backup_file(readme_path)
            print(f"  Backup saved: {backup_path.name}")

        # Write new content
        readme_path.parent.mkdir(exist_ok=True)
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"  [OK] Successfully pulled to {readme_path}")
        return True

    def pull_all(self, force=False):
        """Pull content for all projects"""
        print("\n" + "="*60)
        print("PULL FROM NOTION TO README FILES")
        print("="*60)

        success_count = 0
        skip_count = 0

        for folder_name in self.mappings.keys():
            result = self.pull_project(folder_name, force)
            if result:
                success_count += 1
            else:
                skip_count += 1
            time.sleep(0.5)  # Rate limiting

        print("\n" + "="*60)
        print(f"PULL COMPLETE: {success_count} pulled, {skip_count} skipped")
        print("="*60)

        # Clean old backups (keep last 10 per project)
        self.cleanup_old_backups()

    def cleanup_old_backups(self, keep_count=10):
        """Remove old backups, keeping only the most recent ones"""
        for project_dir in self.backup_dir.iterdir():
            if project_dir.is_dir():
                backups = sorted(project_dir.glob("README_*.md"),
                               key=lambda x: x.stat().st_mtime,
                               reverse=True)

                # Delete old backups
                for old_backup in backups[keep_count:]:
                    old_backup.unlink()
                    print(f"  Cleaned old backup: {old_backup.name}")


def main():
    """Run the pull sync"""
    sync = NotionToReadmeSync()

    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--force":
            # Force pull all without conflict checking
            sync.pull_all(force=True)
        elif sys.argv[1] == "--help":
            print("""
Usage: python pull_from_notion.py [options] [project]

Options:
  --force          Pull all projects without conflict checking
  --help           Show this help message
  [project]        Pull specific project (e.g., 01_Permits_Legal)

Examples:
  python pull_from_notion.py                    # Pull all with conflict checking
  python pull_from_notion.py --force            # Force pull all
  python pull_from_notion.py 01_Permits_Legal   # Pull specific project
            """)
        else:
            # Pull specific project
            folder = sys.argv[1]
            sync.pull_project(folder)
    else:
        # Pull all projects with conflict checking
        sync.pull_all()


if __name__ == "__main__":
    main()