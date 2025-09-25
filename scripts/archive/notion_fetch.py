import requests
import json
import os

# Your Credentials
NOTION_TOKEN = "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"
PAGE_ID = "278bc99424ab8163b358f18243e9ca9c"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def fetch_page_children(page_id, depth=0, max_depth=3):
    if depth > max_depth:
        return {"error": "Max depth reached"}
    
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    response = requests.get(url, headers=headers)  # Fixed: GET for block children
    print(f"Fetching children for {page_id} (depth {depth}): Status {response.status_code}")
    
    if response.status_code == 200:
        blocks = response.json().get("results", [])
        children = []
        for block in blocks:
            block_type = block.get("type", "unknown")
            content = {}
            if block_type == "heading_1":
                content = {"text": [t["text"]["content"] for t in block["heading_1"]["rich_text"]]}
            elif block_type == "toggle":
                content = {"text": [t["text"]["content"] for t in block["toggle"]["rich_text"]]}
            elif block_type == "bulleted_list_item":
                content = {"text": [t["text"]["content"] for t in block["bulleted_list_item"]["rich_text"]]}
            elif block_type == "database":
                content = {"db_id": block["id"], "title": block.get("database", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled")}
            # Add more block types if needed (e.g., paragraph: block["paragraph"]["rich_text"])
            
            child_data = {"type": block_type, "content": content}
            if block.get("has_children", False):
                child_data["nested"] = fetch_page_children(block["id"], depth + 1, max_depth)
            children.append(child_data)
        return children
    else:
        print(f"Error details: {response.text}")
        return {"error": f"API Error {response.status_code}: {response.text}"}

def fetch_database_records(db_id, limit=5):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    payload = {"page_size": limit}
    response = requests.post(url, headers=headers, json=payload)  # POST for DB query (correct)
    print(f"Fetching DB {db_id}: Status {response.status_code}")
    if response.status_code == 200:
        results = response.json().get("results", [])
        records = []
        for record in results:
            props = {}
            for k, v in record["properties"].items():
                if v.get("type") == "title":
                    props[k] = v["title"][0]["text"]["content"] if v["title"] else "N/A"
                elif v.get("type") == "rich_text":
                    props[k] = [t["text"]["content"] for t in v["rich_text"]]
                else:
                    props[k] = str(v)  # Simplified for other types
            records.append(props)
        return records
    print(f"DB Error: {response.text}")
    return {"error": response.text}

# Main Fetch
print("Starting fetch for page:", PAGE_ID)
hierarchy = fetch_page_children(PAGE_ID)

# Auto-fetch any detected DBs (from hierarchy)
db_records = {}
if isinstance(hierarchy, list):
    for child in hierarchy:
        if isinstance(child, dict) and "content" in child and "db_id" in child["content"]:
            db_id = child["content"]["db_id"]
            db_records[db_id] = fetch_database_records(db_id, limit=3)  # Sample 3 records

output = {
    "page_id": PAGE_ID,
    "hierarchy": hierarchy,
    "database_samples": db_records
}

# Save JSON (always in current dir)
json_path = os.path.join(os.getcwd(), "notion_export.json")
with open(json_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\n✅ JSON saved to: {json_path}")
print("\nFull Output (Console Summary):")
print(json.dumps(output, indent=2))