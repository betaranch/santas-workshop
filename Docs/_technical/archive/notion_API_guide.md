# Notion API Guide for Elf Speakeasy Pop-Up Project

This document provides a baseline for interacting with the Notion setup for the Elf Speakeasy pop-up project. It covers authentication, database structure, available fields/properties, and how to read/write data using the Notion API (v1). This is designed for agents, scripts, or platforms to query/update project info (e.g., tasks, projects) without assumptions.

**Current Date**: September 25, 2025  
**Workspace/Page**: "Santa's Workshop" (Page ID: `278bc99424ab8127a7dec0ec844f3a7b`)  
**API Version**: 2022-06-28 (recommended for stability)  
**Integration Token**: `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` (internal use only; rotate periodically)  
**Base URL**: `https://api.notion.com/v1`

## Overview
The setup uses three linked databases on the "Santa's Workshop" page:
- **Projects DB**: Stores project categories (e.g., "Permits & Legal") as pages. Used for relation linking in Tasks.
- **Tasks DB**: Main task tracker with relations to Projects.
- **Notes/Resources DB**: For docs, quotes, etc. (less structured; query as needed).

Data flow: Tasks link to Projects via relation (two-way if set up). Use `/databases/{id}/query` to pull, `/pages` to create/update pages in DBs.

**Rate Limits**: 3 requests/sec; use `time.sleep(0.5)` between calls. Timeouts: 60s default.

**Error Handling**:
- 404 (object_not_found): Check sharing (DB must be shared with integration).
- 400 (invalid_request): Property type mismatch (e.g., relation ID format).
- 429 (rate_limit): Backoff and retry.
- Always log `response.text` for details.

## Authentication
Use Bearer token in headers:
```json
{
  "Authorization": "Bearer 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",
  "Notion-Version": "2022-06-28",
  "Content-Type": "application/json"
}
```
Ensure the integration has read/write access to the workspace/DBs (Notion: Share > Connections > Add integration).

## Database Structure & Fields

### 1. Projects DB (ID: `278bc994-24ab-817e-81bc-db906cd5ced1`)
Stores category pages (e.g., "Permits & Legal"). Query for pages, use IDs for relations.

| Property Name | Type | Description | Interaction Notes |
|---------------|------|-------------|-------------------|
| Name | title | Page title (e.g., "Permits & Legal") | Read: `page['properties']['Name']['title'][0]['text']['content']`<br>Write: `{"title": [{"text": {"content": "New Project"}}]}` |
| Tasks | relation | Links back to Tasks DB (two-way if set) | Read: Array of task IDs<br>Write: `{"relation": [{"id": "task_id"}]}` (array for multi) |

- **Pull Pages**: `/databases/{id}/query` → results as pages.
- **Example Pages** (from recent query): Budget & Finance, Space & Ops, Evaluation & Scaling, Team, Story, Theme & Design, Marketing & Sales, Permits & Legal, Vendors & Suppliers.

### 2. Tasks DB (ID: `278bc994-24ab-8136-b84a-c02ba029cd33`)
Main task tracker. Create pages as tasks.

| Property Name | Type | Description | Interaction Notes |
|---------------|------|-------------|-------------------|
| Name | title | Task title (e.g., "Research permits") | Read: `page['properties']['Name']['title'][0]['text']['content']`<br>Write: `{"title": [{"text": {"content": "New Task"}}]}` |
| Projects | relation | Links to Projects DB page (e.g., ID for "Permits & Legal") | Read: Array of project IDs<br>Write: `{"relation": [{"id": "project_id"}]}` (single for now; array for multi) |
| Status | status | Task status (options: To Do, In Progress, Done—add if empty) | Read: `page['properties']['Status']['status']['name']`<br>Write: `{"select": {"name": "To Do"}}` |
| Created time | created_time | Auto-timestamp | Read: `page['created_time']`<br>Write: Auto |
| Person | people | Assignee (user IDs) | Read: Array of user objects<br>Write: `{"people": [{"id": "user_id"}]}` |
| Priority | select | Priority level (options: High Priority—add Low/Med/Critical) | Read: `page['properties']['Priority']['select']['name']`<br>Write: `{"select": {"name": "High Priority"}}` |
| Due Date | date | Due date | Read: `page['properties']['Due Date']['date']['start']`<br>Write: `{"date": {"start": "2025-10-15"}}` |

- **Pull Tasks**: `/databases/{id}/query` → results as pages (filter by relation to project ID).
- **Push Task**: `/pages` POST with parent = database_id, properties as above.

### 3. Notes/Resources DB (ID: `278bc994-24ab-81f5-97a3-d7c35c5dcb4d`)
For files/quotes. Less used for tasks.

| Property Name | Type | Description | Interaction Notes |
|---------------|------|-------------|-------------------|
| Projects | relation | Links to Projects | As above |
| Photo URL | url | Image links | Read: `page['properties']['Photo URL']['url']`<br>Write: `{"url": "https://example.com/img.jpg"}` |
| Tags | multi_select | Tags (options: add as needed, e.g., "Vendor") | Read: Array of tag names<br>Write: `{"multi_select": [{"name": "Vendor"}]}` |

## Interacting with Fields
- **Relations**: Always array of {"id": "page_id"}. For two-way, update both sides.
- **Select/Multi-Select**: Exact name match; case-sensitive. List options via `/databases/{id}`.
- **Pull (Query)**: POST `/databases/{id}/query` with filter (e.g., {"property": "Projects", "relation": {"contains": "project_id"}}).
- **Push (Create)**: POST `/pages` with "parent": {"database_id": "db_id"}, "properties": { ... }.
- **Update**: PATCH `/pages/{task_id}` with "properties": { updated fields }.

## Examples (Python with requests)
### Pull Tasks Linked to "Permits & Legal"
```python
import requests

url = f'{BASE_URL}/databases/{TASKS_DB_ID}/query'
payload = {
    "filter": {
        "property": "Projects",
        "relation": {
            "contains": "278bc994-24ab-81b1-9fcc-d252f2d2aef9"  # Permits ID
        }
    }
}
response = requests.post(url, headers=headers, json=payload)
tasks = response.json().get('results', [])
for task in tasks:
    print(task['properties']['Name']['title'][0]['text']['content'])
```

### Create Task with Relation
```python
payload = {
    "parent": {"database_id": TASKS_DB_ID},
    "properties": {
        "Name": {"title": [{"text": {"content": "New Permit Task"}}]},
        "Projects": {"relation": [{"id": "278bc994-24ab-81b1-9fcc-d252f2d2aef9"}]},  # Permits ID
        "Priority": {"select": {"name": "High Priority"}},
        "Due Date": {"date": {"start": "2025-10-15"}}
    }
}
response = requests.post(f'{BASE_URL}/pages', headers=headers, json=payload)
if response.status_code == 200:
    print("Task created:", response.json().get('id'))
```

### Update Task Status
```python
task_id = "task_id_here"
payload = {
    "properties": {
        "Status": {"select": {"name": "In Progress"}}
    }
}
response = requests.patch(f'{BASE_URL}/pages/{task_id}', headers=headers, json=payload)
```

## Troubleshooting
- **No Options in Select**: Add in Notion UI; API write fails with 400.
- **Relation Errors**: Ensure two-way relation; IDs must be exact.
- **Timeout**: Add retries/backoff in code.
- **Access Denied**: Share DBs with integration in Notion.

Refine as needed (e.g., add Tags options). For scripts, use the indexed IDs above to avoid fuzzy. Update this doc with new fields/DBs.