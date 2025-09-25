#!/usr/bin/env python3
"""
Setup Synced Blocks for all 8 Project Pages
Discovers pages, creates synced blocks, and saves mappings
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

class SyncedBlockSetup:
    def __init__(self):
        self.api_key = os.getenv("NOTION_API")
        self.base_dir = Path(__file__).parent.parent
        self.cache_dir = self.base_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        # Project mapping
        self.projects = {
            "01_Permits_Legal": "Permits & Legal",
            "02_Space_Ops": "Space & Operations",
            "03_Theme_Design_Story": "Theme, Design, & Story",
            "04_Marketing_Sales": "Marketing & Sales",
            "05_Team": "Team",
            "06_Budget_Finance": "Budget & Finance",
            "07_Vendors_Suppliers": "Vendors & Suppliers",
            "08_Evaluation_Scaling": "Evaluation & Scaling"
        }

        # Known synced block from session doc
        self.known_block = {
            "01_Permits_Legal": "279bc994-24ab-804f-8570-d77ded7e495f"
        }

        # Direct page mappings found from discovery
        self.page_ids = {
            "01_Permits_Legal": "278bc994-24ab-81b1-9fcc-d252f2d2aef9",
            "02_Space_Ops": "278bc994-24ab-8084-9709-f2c58e4f1665",
            "03_Theme_Design_Story": "278bc994-24ab-818c-acaa-c5f9bfa5a10f",
            "04_Marketing_Sales": "278bc994-24ab-819e-a7ed-d2d9b36722b1",
            "05_Team": "278bc994-24ab-8169-9f0c-cd764ec3a646",
            "06_Budget_Finance": "278bc994-24ab-80e9-8caa-f3ebf3b71cc9",
            "07_Vendors_Suppliers": "278bc994-24ab-81c6-881f-ff284e6fe7c7",
            "08_Evaluation_Scaling": "278bc994-24ab-810d-8442-c5489c07642b"
        }

    def search_pages(self):
        """Search for all project pages in Notion"""
        url = "https://api.notion.com/v1/search"
        results = {}

        for folder, title in self.projects.items():
            data = {
                "query": title,
                "filter": {
                    "property": "object",
                    "value": "page"
                },
                "page_size": 5
            }

            response = requests.post(url, headers=self.headers, json=data)
            time.sleep(0.35)  # Rate limiting

            if response.status_code == 200:
                pages = response.json().get("results", [])
                for page in pages:
                    page_title = self._get_page_title(page)
                    if title.lower() in page_title.lower():
                        results[folder] = {
                            "page_id": page["id"],
                            "title": page_title,
                            "url": page["url"],
                            "synced_block_id": self.known_block.get(folder, None)
                        }
                        print(f"[OK] Found: {title} -> {page['id'][:8]}...")
                        break
            else:
                print(f"[X] Not found: {title}")

        return results

    def _get_page_title(self, page):
        """Extract title from page object"""
        props = page.get("properties", {})

        # Try different title property names
        for prop_name in ["Name", "Title", "title"]:
            if prop_name in props:
                title_prop = props[prop_name]
                if title_prop.get("type") == "title":
                    texts = title_prop.get("title", [])
                    if texts:
                        return texts[0].get("text", {}).get("content", "")

        # Fallback to parent type
        parent = page.get("parent", {})
        if parent.get("type") == "page_id":
            return "Child Page"
        elif parent.get("type") == "workspace":
            return "Top Level Page"

        return "Untitled"

    def find_synced_blocks_in_page(self, page_id):
        """Check if page already has synced blocks"""
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        params = {"page_size": 100}

        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            blocks = response.json().get("results", [])

            for block in blocks:
                if block.get("type") == "synced_block":
                    # Check if it's an original (not a reference)
                    synced_from = block.get("synced_block", {}).get("synced_from")
                    if synced_from is None:
                        return block["id"]

        return None

    def create_synced_block(self, page_id, project_name):
        """Create a new synced block in the page"""

        # Initial content for the synced block
        initial_content = [
            {
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"[SYNC] {project_name} Documentation"}
                    }]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "This section syncs with the project's README.md file."}
                    }]
                }
            },
            {
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
                    }],
                    "icon": {"type": "emoji", "emoji": "🔄"},
                    "color": "gray_background"
                }
            }
        ]

        # Create the synced block
        synced_block = {
            "object": "block",
            "type": "synced_block",
            "synced_block": {
                "synced_from": None,  # Original block
                "children": initial_content
            }
        }

        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        data = {"children": [synced_block]}

        response = requests.patch(url, headers=self.headers, json=data)

        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                return results[0]["id"]
        else:
            print(f"    Error creating block: {response.status_code}")
            try:
                error_detail = response.json() if response.text else {}
                if error_detail:
                    # Handle unicode in error messages
                    msg = error_detail.get('message', 'Unknown error')
                    # Replace problematic unicode characters
                    msg = msg.encode('ascii', 'replace').decode('ascii')
                    print(f"    Details: {msg}")
            except:
                print(f"    Raw response: {response.text[:200]}")

        return None

    def setup_all_projects(self):
        """Main setup function"""
        print("\n[SETUP] Using direct page IDs for all 8 projects...\n")

        # Use direct mapping instead of search
        pages = {}
        for folder, title in self.projects.items():
            if folder in self.page_ids:
                pages[folder] = {
                    "page_id": self.page_ids[folder],
                    "title": title,
                    "url": f"https://www.notion.so/{self.page_ids[folder].replace('-', '')}",
                    "synced_block_id": self.known_block.get(folder, None)
                }
                print(f"[OK] Mapped: {title}")

        print(f"\n[OK] Configured {len(pages)} project pages")

        # Check and create synced blocks
        print("\n[SYNC] Setting up synced blocks...\n")

        for folder, page_info in pages.items():
            page_id = page_info["page_id"]
            title = page_info["title"]

            # Check if synced block already exists
            if page_info["synced_block_id"]:
                print(f"[OK] {folder}: Using existing block {page_info['synced_block_id'][:8]}...")
            else:
                existing_block = self.find_synced_blocks_in_page(page_id)

                if existing_block:
                    page_info["synced_block_id"] = existing_block
                    print(f"[OK] {folder}: Found existing block {existing_block[:8]}...")
                else:
                    # Create new synced block
                    new_block = self.create_synced_block(page_id, self.projects[folder])
                    time.sleep(0.5)  # Rate limiting

                    if new_block:
                        page_info["synced_block_id"] = new_block
                        print(f"[OK] {folder}: Created new block {new_block[:8]}...")
                    else:
                        print(f"[X] {folder}: Failed to create synced block")

        # Save the mapping
        mapping_file = self.cache_dir / "synced_blocks.json"
        with open(mapping_file, 'w') as f:
            json.dump(pages, f, indent=2)

        print(f"\n[SAVE] Saved mappings to {mapping_file}")

        # Display summary
        print("\n" + "="*60)
        print("SYNCED BLOCK CONFIGURATION")
        print("="*60)

        for folder, info in pages.items():
            print(f"\n{folder}:")
            print(f"  Page: {info['title']}")
            print(f"  Page ID: {info['page_id']}")
            print(f"  Block ID: {info.get('synced_block_id', 'Not created')}")

        return pages

    def test_sync(self, folder_name):
        """Test syncing content to a specific project"""
        mapping_file = self.cache_dir / "synced_blocks.json"

        if not mapping_file.exists():
            print("No mapping file found. Run setup first.")
            return

        with open(mapping_file, 'r') as f:
            mappings = json.load(f)

        if folder_name not in mappings:
            print(f"Project {folder_name} not found in mappings")
            return

        block_id = mappings[folder_name].get("synced_block_id")
        if not block_id:
            print(f"No synced block ID for {folder_name}")
            return

        # Test content
        test_content = [
            {
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "[OK] Sync Test Successful!"}
                    }]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Synced at: {datetime.now().strftime('%H:%M:%S')}"}
                    }]
                }
            }
        ]

        # Update the synced block
        url = f"https://api.notion.com/v1/blocks/{block_id}/children"
        data = {"children": test_content}

        response = requests.patch(url, headers=self.headers, json=data)

        if response.status_code == 200:
            print(f"[OK] Successfully synced test content to {folder_name}")
        else:
            print(f"[X] Failed to sync: {response.status_code}")
            print(response.text)


def main():
    """Run the setup"""
    setup = SyncedBlockSetup()

    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "test" and len(sys.argv) > 2:
            # Test sync for specific project
            setup.test_sync(sys.argv[2])
        elif sys.argv[1] == "discover":
            # Just discover pages
            pages = setup.search_pages()
            print(f"\nFound {len(pages)} pages")
    else:
        # Full setup
        setup.setup_all_projects()

        print("\n\n[NEXT] Next steps:")
        print("1. Verify the synced blocks appear in Notion")
        print("2. Test sync with: python scripts/setup_synced_blocks.py test 01_Permits_Legal")
        print("3. Implement README to Block conversion")
        print("4. Set up automated sync schedule")


if __name__ == "__main__":
    main()