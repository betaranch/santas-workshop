#!/usr/bin/env python3
"""
Sync README.md files to Notion synced blocks
Converts markdown to Notion blocks and pushes to configured synced blocks
"""

import os
import json
import time
import re
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

class ReadmeToNotionSync:
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

    def markdown_to_notion_blocks(self, markdown_text, max_blocks=90):
        """Convert markdown to Notion blocks format"""
        blocks = []
        lines = markdown_text.split('\n')

        i = 0
        while i < len(lines) and len(blocks) < max_blocks:
            line = lines[i].rstrip()

            # Skip empty lines at the start
            if not line and len(blocks) == 0:
                i += 1
                continue

            # Headers
            if line.startswith('### '):
                blocks.append({
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                    }
                })
            elif line.startswith('## '):
                blocks.append({
                    "type": "heading_2",
                    "heading_2": {
                        "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                    }
                })
            elif line.startswith('# '):
                blocks.append({
                    "type": "heading_1",
                    "heading_1": {
                        "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                    }
                })

            # Bullet points
            elif line.startswith('- '):
                # Collect all consecutive bullet items
                bullet_items = []
                while i < len(lines) and lines[i].startswith('- '):
                    bullet_items.append(lines[i][2:].strip())
                    i += 1
                i -= 1  # Back up one since we'll increment at the end

                # Create bulleted list items
                for item in bullet_items[:min(10, max_blocks - len(blocks))]:
                    blocks.append({
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })

            # Numbered lists
            elif re.match(r'^\d+\. ', line):
                # Collect all consecutive numbered items
                numbered_items = []
                while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                    content = re.sub(r'^\d+\. ', '', lines[i]).strip()
                    numbered_items.append(content)
                    i += 1
                i -= 1

                # Create numbered list items
                for item in numbered_items[:min(10, max_blocks - len(blocks))]:
                    blocks.append({
                        "type": "numbered_list_item",
                        "numbered_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": item}}]
                        }
                    })

            # Code blocks
            elif line.startswith('```'):
                i += 1
                code_lines = []
                language = line[3:].strip() or "plain text"

                while i < len(lines) and not lines[i].startswith('```'):
                    code_lines.append(lines[i])
                    i += 1

                if code_lines and len(blocks) < max_blocks:
                    code_text = '\n'.join(code_lines[:50])  # Limit code lines
                    blocks.append({
                        "type": "code",
                        "code": {
                            "rich_text": [{"type": "text", "text": {"content": code_text}}],
                            "language": language if language in ["python", "javascript", "bash", "json", "yaml", "html", "css"] else "plain text"
                        }
                    })

            # Blockquotes
            elif line.startswith('> '):
                quote_text = line[2:]
                blocks.append({
                    "type": "quote",
                    "quote": {
                        "rich_text": [{"type": "text", "text": {"content": quote_text}}]
                    }
                })

            # Horizontal rule
            elif line in ['---', '***', '___']:
                blocks.append({"type": "divider", "divider": {}})

            # Regular paragraph
            elif line:
                # Parse for bold and italic
                text_parts = self.parse_markdown_formatting(line)
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": text_parts
                    }
                })

            # Empty line = paragraph break
            else:
                if blocks and blocks[-1]["type"] != "paragraph":
                    blocks.append({
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"type": "text", "text": {"content": " "}}]}
                    })

            i += 1

        return blocks

    def parse_markdown_formatting(self, text):
        """Parse markdown bold and italic formatting"""
        parts = []
        current = ""
        i = 0

        while i < len(text):
            # Bold
            if text[i:i+2] == '**':
                if current:
                    parts.append({"type": "text", "text": {"content": current}})
                    current = ""
                i += 2
                end = text.find('**', i)
                if end != -1:
                    parts.append({
                        "type": "text",
                        "text": {"content": text[i:end]},
                        "annotations": {"bold": True}
                    })
                    i = end + 2
                else:
                    current += '**'
            # Italic
            elif text[i] == '*' and (i == 0 or text[i-1] != '*') and (i+1 < len(text) and text[i+1] != '*'):
                if current:
                    parts.append({"type": "text", "text": {"content": current}})
                    current = ""
                i += 1
                end = text.find('*', i)
                if end != -1:
                    parts.append({
                        "type": "text",
                        "text": {"content": text[i:end]},
                        "annotations": {"italic": True}
                    })
                    i = end + 1
                else:
                    current += '*'
            # Code
            elif text[i] == '`':
                if current:
                    parts.append({"type": "text", "text": {"content": current}})
                    current = ""
                i += 1
                end = text.find('`', i)
                if end != -1:
                    parts.append({
                        "type": "text",
                        "text": {"content": text[i:end]},
                        "annotations": {"code": True}
                    })
                    i = end + 1
                else:
                    current += '`'
            else:
                current += text[i]
                i += 1

        if current:
            parts.append({"type": "text", "text": {"content": current}})

        return parts if parts else [{"type": "text", "text": {"content": text}}]

    def update_synced_block(self, block_id, new_blocks):
        """Update a synced block with new content"""

        # First, get and delete existing children
        children_url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        response = requests.get(children_url, headers=self.headers)

        if response.status_code == 200:
            children = response.json().get("results", [])

            # Delete existing children (except the first heading if it's our sync marker)
            for child in children:
                if child.get("type") == "heading_2":
                    # Check if it's our sync marker
                    text = self.extract_text_from_block(child)
                    if "[SYNC]" in text or "Documentation" in text:
                        continue  # Keep the sync marker

                delete_url = f"https://api.notion.com/v1/blocks/{child['id']}"
                requests.delete(delete_url, headers=self.headers)
                time.sleep(0.1)

        # Add new content with a sync timestamp
        all_blocks = [
            {
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
                    }],
                    "icon": {"type": "emoji", "emoji": "✅"},
                    "color": "green_background"
                }
            },
            {"type": "divider", "divider": {}}
        ] + new_blocks

        # Split into batches if needed (Notion limit is 100 blocks)
        batch_size = 100
        for i in range(0, len(all_blocks), batch_size):
            batch = all_blocks[i:i+batch_size]
            data = {"children": batch}

            response = requests.patch(children_url, headers=self.headers, json=data)

            if response.status_code != 200:
                print(f"    Error updating block: {response.status_code}")
                return False

            time.sleep(0.35)  # Rate limiting

        return True

    def extract_text_from_block(self, block):
        """Extract text content from a Notion block"""
        block_type = block.get("type")
        if block_type in ["heading_1", "heading_2", "heading_3", "paragraph"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            return ''.join([t.get("text", {}).get("content", "") for t in rich_text])
        return ""

    def sync_project(self, folder_name):
        """Sync a specific project's README to Notion"""
        if folder_name not in self.mappings:
            print(f"[ERROR] Project {folder_name} not found in mappings")
            return False

        block_id = self.mappings[folder_name].get("synced_block_id")
        if not block_id:
            print(f"[ERROR] No synced block ID for {folder_name}")
            return False

        # Read the README file
        readme_path = self.docs_dir / folder_name / "README.md"
        if not readme_path.exists():
            print(f"[ERROR] No README.md found at {readme_path}")
            return False

        with open(readme_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        print(f"\n[SYNC] {folder_name}")
        print(f"  Reading: {readme_path}")
        print(f"  Block ID: {block_id[:8]}...")

        # Convert markdown to Notion blocks
        notion_blocks = self.markdown_to_notion_blocks(markdown_content)
        print(f"  Converted to {len(notion_blocks)} blocks")

        # Update the synced block
        if self.update_synced_block(block_id, notion_blocks):
            print(f"  [OK] Successfully synced to Notion")
            return True
        else:
            print(f"  [X] Failed to sync")
            return False

    def sync_all(self):
        """Sync all project READMEs to Notion"""
        print("\n" + "="*60)
        print("README TO NOTION SYNC")
        print("="*60)

        success_count = 0
        for folder_name in self.mappings.keys():
            if self.sync_project(folder_name):
                success_count += 1
            time.sleep(0.5)  # Rate limiting between projects

        print("\n" + "="*60)
        print(f"SYNC COMPLETE: {success_count}/{len(self.mappings)} projects synced")
        print("="*60)


def main():
    """Run the sync"""
    sync = ReadmeToNotionSync()

    import sys
    if len(sys.argv) > 1:
        # Sync specific project
        folder = sys.argv[1]
        sync.sync_project(folder)
    else:
        # Sync all projects
        sync.sync_all()


if __name__ == "__main__":
    main()