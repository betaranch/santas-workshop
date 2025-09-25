#!/usr/bin/env python3
"""
Notion Synced Block Integration
Uses Notion's native synced_block feature instead of HTML markers
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

class NotionSyncedBlockManager:
    """
    Manages synced blocks between README files and Notion pages.
    Uses Notion's native synced_block feature for cleaner integration.
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

        # Load or create synced block mappings
        self.block_map = self.load_block_mappings()

    def load_block_mappings(self) -> Dict:
        """Load saved synced block IDs"""
        mapping_file = self.cache_dir / "synced_blocks.json"

        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                return json.load(f)

        return {
            "01_Permits_Legal": {
                "page_id": None,
                "synced_block_id": None,
                "title": "Permits & Legal"
            },
            "02_Space_Ops": {
                "page_id": None,
                "synced_block_id": None,
                "title": "Space & Operations"
            },
            # ... other projects
        }

    def create_synced_block(self, page_id: str, content_blocks: List[Dict]) -> str:
        """Create a new synced block with content"""

        # Create the synced block container
        synced_block = {
            "object": "block",
            "type": "synced_block",
            "synced_block": {
                "synced_from": None,  # This creates an original synced block
                "children": content_blocks
            }
        }

        # Add to page
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        data = {"children": [synced_block]}

        response = requests.patch(url, headers=self.headers, json=data)

        if response.status_code == 200:
            result = response.json()
            # Get the synced block ID
            synced_block_id = result["results"][0]["id"]
            return synced_block_id

        return None

    def update_synced_block(self, block_id: str, new_content: List[Dict]):
        """Update content within a synced block"""

        # First, get existing children and delete them
        children_url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        response = requests.get(children_url, headers=self.headers)

        if response.status_code == 200:
            children = response.json().get("results", [])

            # Delete existing children
            for child in children:
                delete_url = f"https://api.notion.com/v1/blocks/{child['id']}"
                requests.delete(delete_url, headers=self.headers)
                time.sleep(0.1)

        # Add new content
        data = {"children": new_content}
        response = requests.patch(children_url, headers=self.headers, json=data)

        return response.status_code == 200

    def get_synced_block_content(self, block_id: str) -> List[Dict]:
        """Retrieve content from a synced block"""

        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json().get("results", [])

        return []

    def link_synced_block_to_page(self, source_block_id: str, target_page_id: str):
        """Create a synced copy of a block in another page"""

        # Create a synced reference
        synced_reference = {
            "object": "block",
            "type": "synced_block",
            "synced_block": {
                "synced_from": {
                    "type": "block_id",
                    "block_id": source_block_id
                }
            }
        }

        # Add to target page
        url = f"https://api.notion.com/v1/blocks/{target_page_id}/children"
        data = {"children": [synced_reference]}

        response = requests.patch(url, headers=self.headers, json=data)
        return response.status_code == 200


# Alternative: Use Callout Blocks as Visual Markers

class NotionCalloutSync:
    """
    Uses visually appealing callout blocks instead of HTML comments
    """

    def create_sync_section(self, page_id: str, folder_name: str):
        """Create a nice-looking sync section with callout blocks"""

        sync_section = [
            {
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"📁 Synced Documentation: {folder_name}"}
                    }],
                    "icon": {"type": "emoji", "emoji": "🔄"},
                    "color": "blue_background"
                }
            },
            {
                "type": "divider",
                "divider": {}
            },
            # Content goes here
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Content syncs with local README files"}
                    }]
                }
            },
            {
                "type": "divider",
                "divider": {}
            },
            {
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                    }],
                    "icon": {"type": "emoji", "emoji": "✅"},
                    "color": "green_background"
                }
            }
        ]

        return sync_section


# Alternative: Use Toggle Blocks for Collapsible Sync Areas

class NotionToggleSync:
    """
    Uses toggle blocks to create collapsible sync areas
    """

    def create_toggle_sync_section(self, page_id: str, title: str, content: List[Dict]):
        """Create a toggle block that contains synced content"""

        toggle_block = {
            "type": "toggle",
            "toggle": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"📂 {title} (Synced Content)"},
                    "annotations": {
                        "bold": True,
                        "color": "blue"
                    }
                }],
                "children": content
            }
        }

        return toggle_block


# Alternative: Use Unique Headers as Boundaries

class NotionHeaderSync:
    """
    Uses unique headers to mark sync boundaries - cleanest approach!
    """

    def __init__(self):
        self.api_key = os.getenv("NOTION_API")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def find_sync_section_by_header(self, blocks: List[Dict], header_text: str) -> tuple:
        """Find content between specific headers"""

        start_idx = None
        end_idx = None

        for i, block in enumerate(blocks):
            if block.get("type") == "heading_2":
                text = self._extract_text(block)

                # Look for our sync header
                if header_text in text:
                    start_idx = i
                # Look for next section header to mark end
                elif start_idx is not None and "## " in text:
                    end_idx = i
                    break

        # If no end header found, use end of document
        if start_idx is not None and end_idx is None:
            end_idx = len(blocks)

        return start_idx, end_idx

    def _extract_text(self, block: Dict) -> str:
        """Extract text from any block type"""
        block_type = block.get("type")

        if block_type in ["heading_1", "heading_2", "heading_3"]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
        elif block_type == "paragraph":
            rich_text = block.get("paragraph", {}).get("rich_text", [])
        else:
            return ""

        return ''.join([t.get("text", {}).get("content", "") for t in rich_text])


def main():
    """Demo the different sync approaches"""

    print("""
Notion Sync Options - Choose Your Style:

1. SYNCED BLOCKS (Native Notion)
   - Cleanest solution
   - Auto-syncs across pages
   - No visible markers

2. CALLOUT BLOCKS (Visual)
   - Pretty blue/green callouts
   - Clear visual boundaries
   - Professional appearance

3. TOGGLE BLOCKS (Collapsible)
   - Hide/show synced content
   - Saves space
   - Clear labeling

4. HEADER BOUNDARIES (Simplest)
   - Just use "## 📁 Synced Content" headers
   - No special markers
   - Most natural

Which would you prefer?
    """)

if __name__ == "__main__":
    main()