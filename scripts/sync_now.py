import requests
import json

page_id = "278bc994-24ab-81b1-9fcc-d252f2d2aef9"
synced_block_id = "279bc994-24ab-804f-8570-d77ded7e495f"
api_key = "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"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

# Simple test content
test_blocks = [
    {
        "type": "heading_2",
        "heading_2": {
            "rich_text": [{"type": "text", "text": {"content": "Permits & Legal Status"}}]
        }
    },
    {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"type": "text", "text": {"content": "Synced from local README - It works!"}}]
        }
    },
    {
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": "Zoning permit"}}],
            "checked": False
        }
    }
]

# Update synced block
url = f"https://api.notion.com/v1/blocks/{synced_block_id}/children"
data = {"children": test_blocks}

response = requests.patch(url, headers=headers, json=data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("SUCCESS! Check your Notion page!")
else:
    print(f"Error: {response.text[:200]}")
