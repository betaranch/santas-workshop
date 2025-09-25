#!/usr/bin/env python3
"""
Page-Level Sync Between READMEs and Notion
Maps entire README files to Notion page content blocks
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

# Page mapping configuration
PAGE_MAP = {
    "01_Permits_Legal": {
        "notion_page_id": None,  # To be discovered or configured
        "title": "Permits & Legal"
    },
    "02_Space_Ops": {
        "notion_page_id": None,
        "title": "Space & Operations"
    },
    "03_Theme_Design_Story": {
        "notion_page_id": None,
        "title": "Theme, Design & Story"
    },
    "04_Marketing_Sales": {
        "notion_page_id": None,
        "title": "Marketing & Sales"
    },
    "05_Team": {
        "notion_page_id": None,
        "title": "Team"
    },
    "06_Budget_Finance": {
        "notion_page_id": None,
        "title": "Budget & Finance"
    },
    "07_Vendors_Suppliers": {
        "notion_page_id": None,
        "title": "Vendors & Suppliers"
    },
    "08_Evaluation_Scaling": {
        "notion_page_id": None,
        "title": "Evaluation & Scaling"
    }
}

class NotionPageSync:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API")
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / "Docs"
        self.cache_dir = self.base_dir / "cache"
        self.sync_state_file = self.cache_dir / "page_sync_state.json"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Load or initialize page mappings
        self.load_page_mappings()

    def load_page_mappings(self):
        """Load saved page ID mappings or discover them"""
        mapping_file = self.cache_dir / "page_mappings.json"

        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                saved_mappings = json.load(f)
                for folder, data in saved_mappings.items():
                    if folder in PAGE_MAP:
                        PAGE_MAP[folder]["notion_page_id"] = data.get("notion_page_id")

    def save_page_mappings(self):
        """Save page ID mappings for future use"""
        mapping_file = self.cache_dir / "page_mappings.json"
        with open(mapping_file, 'w') as f:
            json.dump(PAGE_MAP, f, indent=2)

    def markdown_to_notion_blocks(self, markdown: str) -> List[Dict]:
        """Convert markdown content to Notion block format"""
        blocks = []
        lines = markdown.split('\n')

        for line in lines:
            if not line.strip():
                continue

            # Headers
            if line.startswith('# '):
                blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            elif line.startswith('### '):
                blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })
            # Bullets
            elif line.startswith('- '):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })
            # Checkboxes
            elif line.startswith('- [ ] ') or line.startswith('- [x] '):
                checked = line.startswith('- [x] ')
                blocks.append({
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": line[6:]}}],
                        "checked": checked
                    }
                })
            # Code blocks
            elif line.startswith('```'):
                # Handle code blocks (simplified)
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": "Code block"}}],
                        "language": "plain text"
                    }
                })
            # Regular paragraphs
            elif line.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": line}}]
                    }
                })

        return blocks

    def notion_blocks_to_markdown(self, blocks: List[Dict]) -> str:
        """Convert Notion blocks to markdown format"""
        markdown_lines = []

        for block in blocks:
            block_type = block.get("type")

            if block_type == "heading_1":
                text = self._extract_text(block["heading_1"]["rich_text"])
                markdown_lines.append(f"# {text}")

            elif block_type == "heading_2":
                text = self._extract_text(block["heading_2"]["rich_text"])
                markdown_lines.append(f"## {text}")

            elif block_type == "heading_3":
                text = self._extract_text(block["heading_3"]["rich_text"])
                markdown_lines.append(f"### {text}")

            elif block_type == "paragraph":
                text = self._extract_text(block["paragraph"]["rich_text"])
                markdown_lines.append(text)

            elif block_type == "bulleted_list_item":
                text = self._extract_text(block["bulleted_list_item"]["rich_text"])
                markdown_lines.append(f"- {text}")

            elif block_type == "to_do":
                text = self._extract_text(block["to_do"]["rich_text"])
                checked = block["to_do"].get("checked", False)
                checkbox = "[x]" if checked else "[ ]"
                markdown_lines.append(f"- {checkbox} {text}")

            elif block_type == "code":
                text = self._extract_text(block["code"]["rich_text"])
                language = block["code"].get("language", "")
                markdown_lines.append(f"```{language}")
                markdown_lines.append(text)
                markdown_lines.append("```")

            # Add spacing
            markdown_lines.append("")

        return '\n'.join(markdown_lines)

    def _extract_text(self, rich_text: List[Dict]) -> str:
        """Extract plain text from Notion rich text format"""
        return ''.join([t.get("text", {}).get("content", "") for t in rich_text])

    def pull_page_to_readme(self, folder_name: str, page_id: str):
        """Pull Notion page content to README file"""
        # Get page content
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print(f"Error fetching page: {response.status_code}")
            return

        blocks = response.json().get("results", [])

        # Convert to markdown
        markdown = self.notion_blocks_to_markdown(blocks)

        # Add sync metadata
        metadata = f"\n\n<!-- SYNCED_WITH_NOTION -->\n"
        metadata += f"<!-- Page ID: {page_id} -->\n"
        metadata += f"<!-- Last Sync: {datetime.now().isoformat()} -->\n"
        metadata += f"<!-- Hash: {hashlib.md5(markdown.encode()).hexdigest()} -->\n"

        # Write to README
        readme_path = self.docs_dir / folder_name / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
            f.write(metadata)

        print(f"Pulled {folder_name} from Notion")

    def push_readme_to_page(self, folder_name: str, page_id: str):
        """Push README content to Notion page"""
        # Read README
        readme_path = self.docs_dir / folder_name / "README.md"
        if not readme_path.exists():
            print(f"No README found for {folder_name}")
            return

        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove sync metadata
        if "<!-- SYNCED_WITH_NOTION -->" in content:
            content = content.split("<!-- SYNCED_WITH_NOTION -->")[0]

        # Convert to Notion blocks
        blocks = self.markdown_to_notion_blocks(content)

        # Clear existing page content
        self._clear_page(page_id)

        # Add new blocks
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        data = {"children": blocks[:100]}  # Notion has a limit of 100 blocks per request

        response = requests.patch(url, headers=self.headers, json=data)

        if response.status_code == 200:
            print(f"Pushed {folder_name} to Notion")
        else:
            print(f"Error pushing {folder_name}: {response.status_code}")

    def _clear_page(self, page_id: str):
        """Clear all blocks from a Notion page"""
        # Get existing blocks
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            return

        blocks = response.json().get("results", [])

        # Delete each block
        for block in blocks:
            delete_url = f"https://api.notion.com/v1/blocks/{block['id']}"
            requests.delete(delete_url, headers=self.headers)

    def sync_all(self, direction: str = "pull"):
        """Sync all README files with Notion pages"""
        for folder_name, config in PAGE_MAP.items():
            page_id = config.get("notion_page_id")

            if not page_id:
                print(f"No page ID configured for {folder_name}")
                continue

            if direction == "pull":
                self.pull_page_to_readme(folder_name, page_id)
            elif direction == "push":
                self.push_readme_to_page(folder_name, page_id)

        self.save_page_mappings()

    def setup_page_mappings(self):
        """Interactive setup to map folders to Notion pages"""
        print("\nSetting up Notion page mappings...")
        print("Enter the Notion page ID for each project folder.")
        print("(You can find this in the page URL after the last dash)\n")

        for folder_name, config in PAGE_MAP.items():
            current = config.get("notion_page_id", "Not set")
            print(f"{folder_name} ({config['title']})")
            print(f"  Current: {current}")

            new_id = input("  Enter page ID (or press Enter to skip): ").strip()
            if new_id:
                PAGE_MAP[folder_name]["notion_page_id"] = new_id
                print(f"  Set to: {new_id}")
            print()

        self.save_page_mappings()
        print("Page mappings saved!")

def main():
    """CLI for page-level sync"""
    import sys

    if len(sys.argv) < 2:
        print("""
Notion Page Sync - Sync entire READMEs with Notion pages

Usage:
  python notion_page_sync.py setup    # Configure page mappings
  python notion_page_sync.py pull     # Pull from Notion to READMEs
  python notion_page_sync.py push     # Push READMEs to Notion
  python notion_page_sync.py status   # Show sync status

This syncs entire README files as page content in Notion.
        """)
        return

    command = sys.argv[1]
    sync = NotionPageSync()

    if command == "setup":
        sync.setup_page_mappings()

    elif command == "pull":
        sync.sync_all(direction="pull")
        print("\nPull complete!")

    elif command == "push":
        confirm = input("This will overwrite Notion pages. Continue? (y/n): ")
        if confirm.lower() == 'y':
            sync.sync_all(direction="push")
            print("\nPush complete!")

    elif command == "status":
        print("\nPage Mappings:")
        for folder, config in PAGE_MAP.items():
            page_id = config.get("notion_page_id", "Not configured")
            status = "Ready" if page_id else "Not configured"
            print(f"  {folder}: {status}")

if __name__ == "__main__":
    main()