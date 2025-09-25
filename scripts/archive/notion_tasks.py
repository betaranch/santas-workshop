from notion_client import Client
import os

# Your credentials
NOTION_TOKEN = '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'
PAGE_ID = '278bc99424ab8163b358f18243e9ca9c'  # From URL

notion = Client(auth=NOTION_TOKEN)

# Step 1: Read page to find Task DB ID (assumes first database block is your Task DB)
def find_task_db_id(page_id):
    blocks = notion.blocks.children.list(block_id=page_id).get('results', [])
    for block in blocks:
        if block['type'] == 'database' and 'Task' in block['database']['title'][0]['text']['content']:  # Adjust filter as needed
            return block['id']
    raise ValueError("Task DB not found—check block types manually.")

DB_ID = find_task_db_id(PAGE_ID)
print(f"Found Task DB ID: {DB_ID}")

# Step 2: Define tasks with properties (match your DB schema)
tasks_data = [
    {
        "Planning and permits": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Research and submit all planning permits (TCO, zoning variance)"}}]},
                "Project": {"select": {"name": "Permits & Legal"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Urgent"}, {"name": "Milestone"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-15"}}
            }
        }
    },
    {
        "Recipes both for cocktails and appetizers": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Develop and test 2 signature cocktails + appetizer pairings"}}]},
                "Project": {"select": {"name": "Theme, Design & Story"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Creative"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-10"}}
            }
        }
    },
    {
        "Personnel and wait staff": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Recruit and schedule 6-8 part-time wait staff/bartenders"}}]},
                "Project": {"select": {"name": "Team"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi-select": [{"name": "Team"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-20"}}
            }
        }
    },
    {
        "Corporate event, sales contacts, and network": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Build sales pipeline: 10 corp contacts for daytime events"}}]},
                "Project": {"select": {"name": "Marketing & Sales"}},
                "Priority": {"select": {"name": "Med"}},
                "Tags": {"multi_select": [{"name": "Vendor"}, {"name": "Milestone"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-05"}}
            }
        }
    },
    {
        "Story and vignettes": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Craft 3-5 story vignettes for themes (e.g., Hearth tales)"}}]},
                "Project": {"select": {"name": "Theme, Design & Story"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Creative"}, {"name": "Story"}]},  # Add "Story" tag if expanding
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-08"}}
            }
        }
    },
    {
        "Layout and design": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Finalize Figma floor plan and design mocks"}}]},
                "Project": {"select": {"name": "Theme, Design & Story"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Creative"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-12"}}
            }
        }
    },
    {
        "Furniture, prop sourcing": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Source and quote rustic furniture/props (Cheerful Redesign, etc.)"}}]},
                "Project": {"select": {"name": "Vendors & Suppliers"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Vendor"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-03"}}
            }
        }
    },
    {
        "Plateware, glassware, barware": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Procure themed plateware/glassware for 75 guests"}}]},
                "Project": {"select": {"name": "Space & Ops"}},
                "Priority": {"select": {"name": "Med"}},
                "Tags": {"multi_select": [{"name": "Vendor"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-18"}}
            }
        }
    },
    {
        "Financing budget": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Refine financing model and track initial expenses"}}]},
                "Project": {"select": {"name": "Budget & Finance"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Budget"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-01"}}
            }
        }
    },
    {
        "Marketing": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Develop marketing calendar and assets (Insta/TikTok)"}}]},
                "Project": {"select": {"name": "Marketing & Sales"}},
                "Priority": {"select": {"name": "High"}},
                "Tags": {"multi_select": [{"name": "Milestone"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-01"}}
            }
        }
    },
    {
        "Merch": {
            "parent": {"database_id": DB_ID},
            "properties": {
                "Name": {"title": [{"text": {"content": "Design and source merch (flasks, kits; $3.75K target)"}}]},
                "Project": {"select": {"name": "Theme, Design & Story"}},
                "Priority": {"select": {"name": "Med"}},
                "Tags": {"multi_select": [{"name": "Creative"}, {"name": "Vendor"}]},
                "Status": {"select": {"name": "To Do"}},
                "Due Date": {"date": {"start": "2025-10-15"}}
            }
        }
    }
]

# Step 3: Write tasks to DB
for item, task_props in tasks_data.items():
    new_page = notion.pages.create(**task_props)
    print(f"Created task for '{item}': {new_page['id']}")

print("All tasks added successfully!")