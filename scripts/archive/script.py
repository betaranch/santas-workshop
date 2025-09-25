import requests
import json
import time

NOTION_TOKEN = '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'
PROJECTS_DB_ID = '278bc994-24ab-817e-81bc-db906cd5ced1'
TASKS_DB_ID = '278bc994-24ab-8136-b84a-c02ba029cd33'

API_VERSION = '2022-06-28'
BASE_URL = 'https://api.notion.com/v1'
headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': API_VERSION,
    'Content-Type': 'application/json'
}

def query_db(db_id, filter=None):
    url = f'{BASE_URL}/databases/{db_id}/query'
    payload = {'page_size': 100}
    if filter:
        payload['filter'] = filter
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Error querying DB {db_id}: {response.status_code} - {response.text}")
        return []

# Step 1: Query Projects DB for existing category pages and map title to page ID
projects_pages = query_db(PROJECTS_DB_ID)
project_map = {}
for page in projects_pages:
    title_prop = page['properties'].get('Name', {}).get('title', [{}])[0].get('text', {})
    title = title_prop.get('content', '') if title_prop else ''
    if title:
        page_id = page['id']
        project_map[title] = page_id
        print(f"Found existing project: '{title}' -> ID: {page_id}")

# Step 2: Define user items with EXACT project_names from index (no fuzzy, no creation)
user_items = [
    {"title": "Research and submit all planning permits (TCO, zoning variance)", "project_name": "Permits & Legal", "priority": "High Priority", "due": "2025-10-15"},
    {"title": "Develop and test 2 signature cocktails + appetizer pairings", "project_name": "Story, Theme & Design", "priority": "High Priority", "due": "2025-10-10"},
    {"title": "Recruit and schedule 6-8 part-time wait staff/bartenders", "project_name": "Team", "priority": "High Priority", "due": "2025-10-20"},
    {"title": "Build sales pipeline: 10 corp contacts for daytime events", "project_name": "Marketing & Sales", "priority": "High Priority", "due": "2025-10-05"},
    {"title": "Craft 3-5 story vignettes for themes (e.g., Hearth tales)", "project_name": "Story, Theme & Design", "priority": "High Priority", "due": "2025-10-08"},
    {"title": "Finalize Figma floor plan and design mocks", "project_name": "Story, Theme & Design", "priority": "High Priority", "due": "2025-10-12"},
    {"title": "Source and quote rustic furniture/props (Cheerful Redesign, etc.)", "project_name": "Vendors & Suppliers", "priority": "High Priority", "due": "2025-10-03"},
    {"title": "Procure themed plateware/glassware for 75 guests", "project_name": "Space & Ops", "priority": "High Priority", "due": "2025-10-18"},
    {"title": "Refine financing model and track initial expenses", "project_name": "Budget & Finance", "priority": "High Priority", "due": "2025-10-01"},
    {"title": "Develop marketing calendar and assets (Insta/TikTok)", "project_name": "Marketing & Sales", "priority": "High Priority", "due": "2025-10-01"},
    {"title": "Design and source merch (flasks, kits; $3.75K target)", "project_name": "Story, Theme & Design", "priority": "High Priority", "due": "2025-10-15"}
]

# Step 3: For each item, get project page ID (exact match only; skip if missing)
created_tasks = []
for item in user_items:
    project_name = item['project_name']
    project_page_id = project_map.get(project_name)
    if not project_page_id:
        print(f"Missing project '{project_name}' in Projects DB. Skipping task.")
        continue
    
    # Prepare relation array for Projects property
    relation_array = [{"id": project_page_id}]
    
    payload = {
        "parent": {"database_id": TASKS_DB_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": item['title']}}]},
            "Projects": {"relation": relation_array},
            "Priority": {"select": {"name": item['priority']}},
            "Due Date": {"date": {"start": item['due']}}
            # Status omitted—set manually
        }
    }
    
    url = f'{BASE_URL}/pages'
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        task_id = response.json().get('id')
        created_tasks.append({
            'id': task_id,
            'title': item['title'],
            'project': project_name,
            'project_id': project_page_id
        })
        print(f"Created task '{item['title'][:50]}...' (ID: {task_id}, Project: {project_name})")
    else:
        print(f"Error creating task for '{item['title'][:50]}...': {response.status_code} - {response.text}")
    time.sleep(0.5)

print(f"\n=== Summary ===")
print(f"Projects Found: {len(project_map)}")
print(f"Tasks Created: {len(created_tasks)}")

# Export
with open('created_tasks.json', 'w') as f:
    json.dump(created_tasks, f, indent=2)
print("Exported task details to 'created_tasks.json'")