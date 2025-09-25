import requests
import json

# Your page ID from URL
page_id = "278bc994-24ab-81b1-9fcc-d252f2d2aef9"
api_key = "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"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Notion-Version": "2022-06-28"
}

# Get page blocks
url = f"https://api.notion.com/v1/blocks/{page_id}/children"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    blocks = response.json()["results"]
    print(f"Found {len(blocks)} blocks")
    
    # Look for synced blocks or code blocks with markers
    for i, block in enumerate(blocks):
        block_type = block.get("type")
        print(f"Block {i}: {block_type}")
        
        if block_type == "synced_block":
            print("  -> Found synced block!")
            print(f"  -> ID: {block['id']}")
        elif block_type == "code":
            text = block.get("code", {}).get("rich_text", [])
            if text:
                content = text[0].get("text", {}).get("content", "")
                if "SYNC_START" in content:
                    print("  -> Found markers in code block!")
else:
    print(f"Error: {response.status_code}")
