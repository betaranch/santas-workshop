#!/usr/bin/env python3
"""
Notion Segment Sync - Sync marked segments between README and Notion
Uses special markers to define sync boundaries in Notion pages
"""

import os
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from dotenv import load_dotenv

load_dotenv()

class NotionSegmentSync:
    """
    Syncs marked segments between README files and Notion pages.

    In Notion, create a segment with:
    <!-- SYNC_START:folder_name -->
    Content to sync...
    <!-- SYNC_END:folder_name -->

    In README, the entire file syncs to that segment.
    """

    def __init__(self):
        self.api_key = os.getenv("NOTION_API")
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / "Docs"
        self.cache_dir = self.base_dir / "cache"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Map folders to their parent Notion pages
        self.segment_map = self.load_segment_map()

    def load_segment_map(self) -> Dict:
        """Load or create segment mapping configuration"""
        config_file = self.cache_dir / "segment_map.json"

        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)

        # Default structure - user needs to add page IDs
        default_map = {
            "01_Permits_Legal": {
                "page_id": None,
                "segment_marker": "permits_content",
                "title": "Permits & Legal"
            },
            "02_Space_Ops": {
                "page_id": None,
                "segment_marker": "space_ops_content",
                "title": "Space & Operations"
            },
            "03_Theme_Design_Story": {
                "page_id": None,
                "segment_marker": "theme_content",
                "title": "Theme, Design & Story"
            },
            "04_Marketing_Sales": {
                "page_id": None,
                "segment_marker": "marketing_content",
                "title": "Marketing & Sales"
            },
            "05_Team": {
                "page_id": None,
                "segment_marker": "team_content",
                "title": "Team"
            },
            "06_Budget_Finance": {
                "page_id": None,
                "segment_marker": "budget_content",
                "title": "Budget & Finance"
            },
            "07_Vendors_Suppliers": {
                "page_id": None,
                "segment_marker": "vendors_content",
                "title": "Vendors & Suppliers"
            },
            "08_Evaluation_Scaling": {
                "page_id": None,
                "segment_marker": "evaluation_content",
                "title": "Evaluation & Scaling"
            }
        }

        return default_map

    def save_segment_map(self):
        """Save segment mapping configuration"""
        config_file = self.cache_dir / "segment_map.json"
        with open(config_file, 'w') as f:
            json.dump(self.segment_map, f, indent=2)

    def find_sync_segment(self, blocks: List[Dict], marker: str) -> Tuple[int, int]:
        """
        Find the start and end indices of a sync segment in Notion blocks.
        Looks for comments like: <!-- SYNC_START:marker --> and <!-- SYNC_END:marker -->
        """
        start_idx = None
        end_idx = None

        for i, block in enumerate(blocks):
            if block.get("type") == "paragraph":
                text = self._extract_text_from_block(block)

                if f"<!-- SYNC_START:{marker} -->" in text:
                    start_idx = i
                elif f"<!-- SYNC_END:{marker} -->" in text:
                    end_idx = i

                if start_idx is not None and end_idx is not None:
                    break

        return start_idx, end_idx

    def _extract_text_from_block(self, block: Dict) -> str:
        """Extract plain text from a Notion block"""
        block_type = block.get("type")

        if block_type == "paragraph":
            rich_text = block.get("paragraph", {}).get("rich_text", [])
        elif block_type == "heading_1":
            rich_text = block.get("heading_1", {}).get("rich_text", [])
        elif block_type == "heading_2":
            rich_text = block.get("heading_2", {}).get("rich_text", [])
        elif block_type == "heading_3":
            rich_text = block.get("heading_3", {}).get("rich_text", [])
        elif block_type == "bulleted_list_item":
            rich_text = block.get("bulleted_list_item", {}).get("rich_text", [])
        else:
            return ""

        return ''.join([t.get("text", {}).get("content", "") for t in rich_text])

    def pull_segment(self, folder_name: str) -> bool:
        """Pull a segment from Notion to README"""
        config = self.segment_map.get(folder_name)
        if not config or not config.get("page_id"):
            print(f"No page configured for {folder_name}")
            return False

        page_id = config["page_id"]
        marker = config["segment_marker"]

        # Get all blocks from the page
        blocks = self._get_all_blocks(page_id)
        if not blocks:
            print(f"No blocks found in page {page_id}")
            return False

        # Find sync segment
        start_idx, end_idx = self.find_sync_segment(blocks, marker)

        if start_idx is None or end_idx is None:
            print(f"Sync markers not found for {marker} in page")
            print(f"Add these to your Notion page:")
            print(f"  <!-- SYNC_START:{marker} -->")
            print(f"  (Your content here)")
            print(f"  <!-- SYNC_END:{marker} -->")
            return False

        # Extract segment blocks (excluding marker blocks)
        segment_blocks = blocks[start_idx + 1:end_idx]

        # Convert to markdown
        markdown = self._blocks_to_markdown(segment_blocks)

        # Write to README
        readme_path = self.docs_dir / folder_name / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        metadata = [
            f"<!-- SYNCED FROM NOTION -->",
            f"<!-- Page ID: {page_id} -->",
            f"<!-- Marker: {marker} -->",
            f"<!-- Last Pull: {datetime.now().isoformat()} -->",
            f"<!-- Hash: {hashlib.md5(markdown.encode()).hexdigest()} -->\n"
        ]

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
            f.write('\n\n')
            f.write('\n'.join(metadata))

        print(f"Pulled {folder_name} segment from Notion")
        return True

    def push_segment(self, folder_name: str) -> bool:
        """Push README content to a Notion segment"""
        config = self.segment_map.get(folder_name)
        if not config or not config.get("page_id"):
            print(f"No page configured for {folder_name}")
            return False

        page_id = config["page_id"]
        marker = config["segment_marker"]

        # Read README
        readme_path = self.docs_dir / folder_name / "README.md"
        if not readme_path.exists():
            print(f"No README found at {readme_path}")
            return False

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove metadata section if present
        if "<!-- SYNCED FROM NOTION -->" in content:
            content = content.split("<!-- SYNCED FROM NOTION -->")[0].strip()

        # Convert to Notion blocks
        new_blocks = self._markdown_to_blocks(content)

        # Get current page blocks
        current_blocks = self._get_all_blocks(page_id)

        # Find segment boundaries
        start_idx, end_idx = self.find_sync_segment(current_blocks, marker)

        if start_idx is None or end_idx is None:
            print(f"Creating new sync segment for {marker}")
            # Append new segment at end
            self._append_segment(page_id, marker, new_blocks)
        else:
            print(f"Updating existing segment for {marker}")
            # Replace segment content
            self._replace_segment(page_id, current_blocks, start_idx, end_idx, new_blocks)

        print(f"Pushed {folder_name} to Notion segment")
        return True

    def _get_all_blocks(self, page_id: str) -> List[Dict]:
        """Get all blocks from a Notion page"""
        blocks = []
        has_more = True
        start_cursor = None

        while has_more:
            url = f"https://api.notion.com/v1/blocks/{page_id}/children"
            params = {"page_size": 100}

            if start_cursor:
                params["start_cursor"] = start_cursor

            response = requests.get(url, headers=self.headers, params=params)
            time.sleep(0.35)  # Rate limiting

            if response.status_code != 200:
                print(f"Error fetching blocks: {response.status_code}")
                return blocks

            data = response.json()
            blocks.extend(data.get("results", []))
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")

        return blocks

    def _blocks_to_markdown(self, blocks: List[Dict]) -> str:
        """Convert Notion blocks to markdown"""
        lines = []

        for block in blocks:
            block_type = block.get("type")

            if block_type == "heading_1":
                text = self._extract_text_from_block(block)
                lines.append(f"# {text}")

            elif block_type == "heading_2":
                text = self._extract_text_from_block(block)
                lines.append(f"## {text}")

            elif block_type == "heading_3":
                text = self._extract_text_from_block(block)
                lines.append(f"### {text}")

            elif block_type == "paragraph":
                text = self._extract_text_from_block(block)
                if text:
                    lines.append(text)

            elif block_type == "bulleted_list_item":
                text = self._extract_text_from_block(block)
                lines.append(f"- {text}")

            elif block_type == "numbered_list_item":
                text = self._extract_text_from_block(block)
                lines.append(f"1. {text}")

            elif block_type == "to_do":
                text = self._extract_text_from_block(block)
                checked = block.get("to_do", {}).get("checked", False)
                checkbox = "[x]" if checked else "[ ]"
                lines.append(f"- {checkbox} {text}")

            elif block_type == "code":
                code_text = self._extract_text_from_block(block)
                language = block.get("code", {}).get("language", "")
                lines.append(f"```{language}")
                lines.append(code_text)
                lines.append("```")

            elif block_type == "divider":
                lines.append("---")

            # Add spacing
            if block_type in ["heading_1", "heading_2", "heading_3", "paragraph", "divider"]:
                lines.append("")

        return '\n'.join(lines).strip()

    def _markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """Convert markdown to Notion blocks (simplified)"""
        blocks = []
        lines = markdown.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Headers
            if line.startswith('# '):
                blocks.append({
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:].strip()}}]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:].strip()}}]
                    }
                })
            # Lists
            elif line.startswith('- '):
                # Check for checkbox
                if line.startswith('- [ ] ') or line.startswith('- [x] '):
                    checked = line.startswith('- [x] ')
                    text = line[6:].strip()
                    blocks.append({
                        "type": "to_do",
                        "to_do": {
                            "rich_text": [{"type": "text", "text": {"content": text}}],
                            "checked": checked
                        }
                    })
                else:
                    blocks.append({
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": line[2:].strip()}}]
                        }
                    })
            # Code blocks
            elif line.startswith('```'):
                # Find end of code block
                language = line[3:].strip() or "plain text"
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1

                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": '\n'.join(code_lines)}}],
                        "language": language
                    }
                })
            # Dividers
            elif line.strip() == '---':
                blocks.append({
                    "type": "divider",
                    "divider": {}
                })
            # Regular paragraphs
            else:
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line.strip()}}]
                    }
                })

            i += 1

        return blocks

    def _append_segment(self, page_id: str, marker: str, blocks: List[Dict]):
        """Append a new sync segment to a page"""
        # Create segment with markers
        segment_blocks = [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"<!-- SYNC_START:{marker} -->"}}]
                }
            }
        ] + blocks + [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": f"<!-- SYNC_END:{marker} -->"}}]
                }
            }
        ]

        # Append to page
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"

        # Notion limits to 100 blocks per request
        for i in range(0, len(segment_blocks), 100):
            batch = segment_blocks[i:i+100]
            data = {"children": batch}
            response = requests.patch(url, headers=self.headers, json=data)
            time.sleep(0.35)

            if response.status_code != 200:
                print(f"Error appending blocks: {response.status_code}")

    def _replace_segment(self, page_id: str, current_blocks: List[Dict],
                        start_idx: int, end_idx: int, new_blocks: List[Dict]):
        """Replace content between segment markers"""
        # Delete existing blocks between markers
        blocks_to_delete = current_blocks[start_idx + 1:end_idx]

        for block in blocks_to_delete:
            delete_url = f"https://api.notion.com/v1/blocks/{block['id']}"
            requests.delete(delete_url, headers=self.headers)
            time.sleep(0.35)

        # Insert new blocks after start marker
        if new_blocks:
            # We need to add blocks after the start marker block
            after_block_id = current_blocks[start_idx]['id']

            # Add blocks one by one to maintain order
            for block in reversed(new_blocks):
                url = f"https://api.notion.com/v1/blocks/{after_block_id}/children"
                data = {"children": [block]}
                response = requests.patch(url, headers=self.headers, json=data)
                time.sleep(0.35)

                if response.status_code != 200:
                    print(f"Error inserting block: {response.status_code}")

    def setup_pages(self):
        """Interactive setup to configure page mappings"""
        print("\nSetting up Notion page mappings for segment sync...")
        print("For each project folder, provide:")
        print("1. The Notion page ID where the content lives")
        print("2. The segment will be marked with HTML comments\n")

        for folder_name, config in self.segment_map.items():
            print(f"\n{folder_name} ({config['title']})")
            print(f"  Current page ID: {config.get('page_id', 'Not set')}")
            print(f"  Segment marker: {config['segment_marker']}")

            page_id = input("  Enter Notion page ID (or Enter to skip): ").strip()
            if page_id:
                self.segment_map[folder_name]["page_id"] = page_id
                print(f"  Configured! Add these markers to your Notion page:")
                print(f"    <!-- SYNC_START:{config['segment_marker']} -->")
                print(f"    (Your content here)")
                print(f"    <!-- SYNC_END:{config['segment_marker']} -->")

        self.save_segment_map()
        print("\nConfiguration saved!")

    def sync_all(self, direction: str = "pull"):
        """Sync all configured segments"""
        success_count = 0

        for folder_name in self.segment_map.keys():
            if direction == "pull":
                if self.pull_segment(folder_name):
                    success_count += 1
            elif direction == "push":
                if self.push_segment(folder_name):
                    success_count += 1

        print(f"\n{direction.title()} complete: {success_count} segments synced")

def main():
    """CLI interface"""
    import sys

    if len(sys.argv) < 2:
        print("""
Notion Segment Sync - Sync marked segments between READMEs and Notion

Usage:
  python notion_segment_sync.py setup     # Configure page mappings
  python notion_segment_sync.py pull      # Pull segments from Notion
  python notion_segment_sync.py push      # Push READMEs to Notion segments
  python notion_segment_sync.py pull-one [folder]  # Pull specific folder
  python notion_segment_sync.py push-one [folder]  # Push specific folder

How it works:
1. In Notion, add HTML comments to mark sync boundaries
2. This tool syncs content between those markers with README files
3. Changes can flow both directions

Example Notion markup:
  <!-- SYNC_START:permits_content -->
  ## Permits Documentation
  This content syncs with the README...
  <!-- SYNC_END:permits_content -->
        """)
        return

    command = sys.argv[1]
    sync = NotionSegmentSync()

    if command == "setup":
        sync.setup_pages()

    elif command == "pull":
        sync.sync_all(direction="pull")

    elif command == "push":
        confirm = input("This will update Notion segments. Continue? (y/n): ")
        if confirm.lower() == 'y':
            sync.sync_all(direction="push")

    elif command == "pull-one" and len(sys.argv) > 2:
        folder = sys.argv[2]
        sync.pull_segment(folder)

    elif command == "push-one" and len(sys.argv) > 2:
        folder = sys.argv[2]
        sync.push_segment(folder)

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()