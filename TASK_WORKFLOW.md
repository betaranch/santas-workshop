# Task Management Workflow Guide

## Quick Start

### View Current Tasks
```bash
# Pull latest tasks from Notion
python scripts/notion_task_manager.py read

# Tasks appear in each project folder as tasks.md
cat Docs/06_Budget_Finance/tasks.md
```

### Create New Task
```bash
# Use test script as template
python scripts/test_create_task.py

# Or create via Notion UI directly
```

## Complete Task Flow

### 1. Pull Tasks (Notion → Local)
```bash
# Pull all tasks from Notion
python scripts/notion_task_manager.py read

# Generate project task files
python scripts/generate_tasks_md.py

# Both are run automatically by start_work.py
```

### 2. Review Tasks (Local)
```bash
# Check specific project tasks
cat Docs/01_Permits_Legal/tasks.md
cat Docs/06_Budget_Finance/tasks.md

# View summary indexes
cat cache/indexes/high_priority.json
cat cache/indexes/upcoming_deadlines.json
```

### 3. Manage Tasks (Notion)
Tasks are primarily managed in Notion. The local system provides:
- Read-only task views organized by project
- Deduplication capabilities
- AI-friendly structured data for analysis

## How It Works

### Architecture
```
Notion Tasks Database
    ↓ (read via API)
notion_task_manager.py
    ↓ (saves to cache)
all_tasks_YYYYMMDD_HHMMSS.json
    ↓ (filtered by project)
generate_tasks_md.py
    ↓ (creates markdown)
Docs/*/tasks.md files
```

### What Syncs Where

| Content Type | Direction | Script | Output |
|-------------|-----------|---------|---------|
| Tasks | Notion → Local | `notion_task_manager.py read` | cache/tasks/*.json |
| Task Views | Cache → Markdown | `generate_tasks_md.py` | Docs/*/tasks.md |
| New Tasks | Local → Notion | `test_create_task.py` | Creates in Notion |
| Duplicates | Local → Notion | `notion_task_manager.py dedupe` | Archives in Notion |

### Task Categorization

Tasks are automatically filtered into projects based on:
1. **Project Assignment** - Direct relation in Notion
2. **Keyword Matching** - Fallback for uncategorized tasks

## Individual Commands

### Discovery & Setup
```bash
# Discover task databases
python scripts/notion_task_manager.py discover

# Discover project relations
python scripts/discover_projects.py
```

### Daily Operations
```bash
# Read all tasks
python scripts/notion_task_manager.py read

# Find duplicates
python scripts/notion_task_manager.py duplicates

# Remove duplicates (dry run)
python scripts/notion_task_manager.py dedupe

# Remove duplicates (actual)
python scripts/notion_task_manager.py dedupe --run
```

### Task Creation
```bash
# Create test task
python scripts/test_create_task.py

# Update task project
python scripts/update_task_project.py
```

### Task Generation
```bash
# Generate all project task files
python scripts/generate_tasks_md.py
```

## Project Task Files

Each project folder contains a `tasks.md` with:
- Task count and priority breakdown
- Tasks grouped by priority (High/Medium/Low)
- Task details: name, status, due date, assignee

### File Locations
```
Docs/01_Permits_Legal/tasks.md
Docs/02_Space_Ops/tasks.md
Docs/03_Theme_Design_Story/tasks.md
Docs/04_Marketing_Sales/tasks.md
Docs/05_Team/tasks.md
Docs/06_Budget_Finance/tasks.md
Docs/07_Vendors_Suppliers/tasks.md
Docs/08_Evaluation_Scaling/tasks.md
Docs/00_Uncategorized/tasks.md
```

## Cache Structure

```
cache/
├── tasks/
│   ├── all_tasks_*.json         # Raw task data from Notion
│   ├── dedup_report_*.json      # Deduplication reports
│   ├── operations_*.json        # Operation logs
│   └── created_task_*.json      # New task creation logs
├── indexes/
│   ├── high_priority.json       # High priority task index
│   ├── upcoming_deadlines.json  # Tasks by deadline
│   ├── no_status.json          # Tasks missing status
│   └── summary.json            # Overall statistics
├── task_config.json            # Database configuration
└── project_mapping.json        # Project ID mappings
```

## Deduplication Process

### Identify Duplicates
```bash
python scripts/notion_task_manager.py duplicates
```

### Review & Remove
```bash
# Dry run (preview)
python scripts/notion_task_manager.py dedupe

# Actual removal
python scripts/notion_task_manager.py dedupe --run
```

### How It Works
- Duplicates identified by: task name + project combination
- Keeps the oldest task (by creation date)
- Archives duplicates (soft delete) rather than hard delete
- Creates audit trail in cache/tasks/operations_*.json

## Creating Tasks

### Via Script
```python
# Example from test_create_task.py
task_data = {
    "parent": {"database_id": db_id},
    "properties": {
        "Name": {"title": [{"text": {"content": "Task name"}}]},
        "Status": {"status": {"name": "Not started"}},
        "Priority": {"select": {"name": "High Priority"}},
        "Due Date": {"date": {"start": "2025-10-07"}},
        "Projects": {"relation": [{"id": project_id}]}
    }
}
```

### Project IDs
```
Budget & Finance: 278bc994-24ab-80e9-8caa-f3ebf3b71cc9
Space & Ops: 278bc994-24ab-8084-9709-f2c58e4f1665
Evaluation & Scaling: 278bc994-24ab-810d-8442-c5489c07642b
Team: 278bc994-24ab-8169-9f0c-cd764ec3a646
Story, Theme & Design: 278bc994-24ab-818c-acaa-c5f9bfa5a10f
Marketing & Sales: 278bc994-24ab-819e-a7ed-d2d9b36722b1
Permits & Legal: 278bc994-24ab-81b1-9fcc-d252f2d2aef9
Vendors & Suppliers: 278bc994-24ab-81c6-881f-ff284e6fe7c7
```

## Best Practices

1. **Always pull before reviewing** - `notion_task_manager.py read` gets latest
2. **Manage tasks in Notion** - Local files are read-only views
3. **Check for duplicates weekly** - Run deduplication regularly
4. **Use project assignments** - Ensures tasks appear in correct folder
5. **Archive, don't delete** - Maintains audit trail

## Troubleshooting

### "No task databases found"
Run: `python scripts/notion_task_manager.py discover`

### Tasks not appearing in project folder
1. Check if task has Projects field set in Notion
2. Run `python scripts/discover_projects.py` to verify mapping
3. Update task with correct project relation

### Duplicate tasks keep appearing
1. Run deduplication: `python scripts/notion_task_manager.py dedupe --run`
2. Check if automation is creating duplicates
3. Review cache/tasks/operations_*.json for patterns

### Unicode/encoding errors
Scripts handle Windows encoding automatically. Check console output for [ERROR] markers.

## Integration with Daily Workflow

Task management is integrated into the daily sync:

```bash
# Morning (start_work.py includes):
- notion_task_manager.py read
- generate_tasks_md.py

# During work:
- Review tasks.md files
- Update in Notion as needed

# Evening (tasks auto-sync next morning)
```

## Advanced Usage

### Custom Task Filtering
Edit `generate_tasks_md.py` keyword mappings to adjust categorization.

### Bulk Operations
Use Notion's database views for bulk updates, then sync locally.

### Task Analytics
Use cache/indexes/*.json files for custom reporting and analysis.

---

*Remember: Tasks are the heartbeat of the project. Keep them current, clear, and actionable!*