# Task Management System - Technical Documentation

## Overview

The Notion Task Management System provides a dedicated layer for handling tasks in Notion without interfering with other sync operations (like synced blocks). This system is designed to read, deduplicate, and update tasks across your Notion workspace.

## Architecture

### Separation of Concerns

The task management system operates independently from other Notion sync operations:

- **Task Manager** (`notion_task_manager.py`): Handles all task-specific operations
- **General Sync** (`notion.py`): Manages general content syncing
- **Block Sync** (other scripts): Handle synced blocks and page content

This separation ensures that task operations don't interfere with content synchronization.

## Key Features

### 1. Task Discovery
- Automatically finds all task databases in your Notion workspace
- Caches database IDs for efficient operations
- Filters databases by name (looks for "task" in title)

### 2. Duplicate Detection
- Identifies duplicates based on:
  - Task name
  - Associated projects
- Groups duplicates for review
- Maintains audit trail

### 3. Safe Deduplication
- **Dry Run Mode**: Preview what will be removed before committing
- **Smart Selection**: Keeps the newest task (by creation date)
- **Soft Delete**: Archives duplicates instead of permanent deletion
- **Full Audit Trail**: Logs all operations

### 4. Task Updates
- Update individual task properties
- Batch update capabilities
- Property type handling for all Notion field types

## Usage Workflow

### Initial Setup

1. **Discover Task Databases**
```bash
python scripts/notion_task_manager.py discover
```

2. **Read Current Tasks**
```bash
python scripts/notion_task_manager.py read
```

### Removing Duplicates

1. **Check for Duplicates**
```bash
python scripts/notion_task_manager.py duplicates
```

2. **Preview Deduplication (Dry Run)**
```bash
python scripts/notion_task_manager.py dedupe
```

3. **Execute Deduplication**
```bash
python scripts/notion_task_manager.py dedupe --run
```

## Current Duplicate Analysis

Based on the analysis of your current tasks, we found **7 sets of duplicate tasks**, each appearing 3 times:

| Task | Due Date | Duplicates |
|------|----------|------------|
| Develop marketing calendar and assets | Oct 1 | 3 copies |
| Refine financing model | Oct 1 | 3 copies |
| Procure themed plateware/glassware | Oct 18 | 3 copies |
| Source and quote rustic furniture | Oct 3 | 3 copies |
| Build sales pipeline | Oct 5 | 3 copies |
| Recruit wait staff/bartenders | Oct 20 | 3 copies |
| Research and submit permits | Oct 15 | 3 copies |

These duplicates were created at different times (18:16, 00:40, 00:38) on September 25, 2025.

## API Reference

### NotionTaskManager Class

#### Core Methods

**`discover_task_databases()`**
- Discovers all task databases in the workspace
- Returns: Dict mapping database IDs to metadata
- Side effect: Updates config file

**`read_all_tasks(db_id=None)`**
- Reads all tasks from specified or all databases
- Parameters:
  - `db_id` (optional): Specific database ID
- Returns: List of task dictionaries

**`find_duplicates(tasks)`**
- Identifies duplicate tasks
- Parameters:
  - `tasks`: List of task dictionaries
- Returns: Dict mapping signatures to duplicate task groups

**`deduplicate_tasks(dry_run=True)`**
- Removes duplicate tasks
- Parameters:
  - `dry_run`: If True, only preview changes
- Returns: Deduplication report

**`update_task(task_id, updates)`**
- Updates a single task
- Parameters:
  - `task_id`: Notion page ID
  - `updates`: Dict of property updates
- Returns: Boolean success status

#### Helper Methods

**`_archive_task(task_id)`**
- Archives (soft deletes) a task
- Parameters:
  - `task_id`: Notion page ID
- Returns: Boolean success status

**`save_operations_log()`**
- Saves audit log of all operations
- Side effect: Creates JSON log file

## Data Storage

### Directory Structure
```
cache/
├── tasks/
│   ├── all_tasks_YYYYMMDD_HHMMSS.json
│   ├── dedup_report_YYYYMMDD_HHMMSS.json
│   └── operations_YYYYMMDD_HHMMSS.json
└── task_config.json
```

### File Formats

**task_config.json**
```json
{
  "task_databases": {
    "database_id": {
      "title": "Database Name",
      "id": "database_id",
      "created": "ISO timestamp",
      "updated": "ISO timestamp"
    }
  },
  "discovered_at": "ISO timestamp"
}
```

**dedup_report.json**
```json
{
  "timestamp": "ISO timestamp",
  "dry_run": true/false,
  "duplicates_found": number,
  "tasks_removed": number,
  "kept_tasks": [...],
  "removed_tasks": [...]
}
```

## Safety Features

1. **Dry Run by Default**: Always preview changes before execution
2. **Soft Delete**: Archives tasks instead of permanent deletion
3. **Audit Trail**: All operations are logged
4. **Rate Limiting**: Respects Notion API limits
5. **Error Recovery**: Graceful handling of API failures

## Integration Guidelines

### Coexistence with Other Sync Operations

The task manager is designed to work alongside other Notion sync operations:

1. **Separate Cache**: Uses `cache/tasks/` directory
2. **Separate Config**: Uses `task_config.json`
3. **No Block Modifications**: Only updates page properties
4. **Read-Only by Default**: Write operations require explicit commands

### Best Practices

1. **Regular Deduplication**: Run weekly to prevent duplicate buildup
2. **Always Dry Run First**: Review changes before applying
3. **Monitor Logs**: Check operation logs for any issues
4. **Backup Before Major Operations**: Export tasks before bulk changes

## Troubleshooting

### Common Issues

**"No NOTION_API key found"**
- Solution: Add `NOTION_API=your_key` to `.env` file

**"Rate limited" errors**
- Solution: Script automatically handles rate limits with backoff

**Duplicates keep appearing**
- Check if multiple sync processes are running
- Verify no automation is creating duplicates
- Review creation timestamps to identify source

## Future Enhancements

- [ ] Bulk task creation from templates
- [ ] Smart merge of duplicate task properties
- [ ] Scheduled deduplication runs
- [ ] Webhook integration for real-time updates
- [ ] Advanced filtering and search capabilities
- [ ] Task relationship management

## Support

For issues or questions:
1. Check operation logs in `cache/tasks/`
2. Review deduplication reports
3. Ensure API key has proper permissions
4. Verify database IDs in `task_config.json`