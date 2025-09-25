# Notion Sync Workflow Guide

## Quick Start

### Before Work Session
```bash
python scripts/start_work.py
```
This pulls the latest content from Notion so you have current data.

### After Work Session
```bash
python scripts/end_work.py
```
This pushes your changes back to Notion for the team to see.

## Complete Sync Flow

### 1. Pull (Notion → Markdown)
```bash
# Pull everything
python scripts/pull_from_notion.py

# Pull specific project
python scripts/pull_from_notion.py 01_Permits_Legal

# Force pull (skip conflict checks)
python scripts/pull_from_notion.py --force
```

### 2. Push (Markdown → Notion)
```bash
# Push all READMEs
python scripts/sync_readme_to_notion.py

# Push specific project
python scripts/sync_readme_to_notion.py 01_Permits_Legal

# Interactive menu
python scripts/quick_sync.py
```

## How It Works

### Bi-directional Sync

```
Morning:
  Notion → pull_from_notion.py → README.md files
  Tasks Database → notion.py sync → tasks.md files

During work:
  Edit README.md files locally in markdown

Evening:
  README.md files → sync_readme_to_notion.py → Notion
```

### What Syncs Where

| Content Type | Direction | Script | Output |
|-------------|-----------|---------|---------|
| Page Content | Notion → Local | `pull_from_notion.py` | README.md files |
| Page Content | Local → Notion | `sync_readme_to_notion.py` | Synced blocks |
| Tasks | Notion → Local | `notion_task_manager.py read` | cache/tasks/*.json |
| Task Files | Cache → Markdown | `generate_tasks_md.py` | tasks.md files |

### Conflict Protection

- **Automatic Backups**: Created before overwriting any file
- **Conflict Detection**: Warns if file modified in last 30 minutes
- **Backup Location**: `/backups/[project_name]/README_[timestamp].md`
- **Retention**: Keeps last 10 backups per project

## Individual Scripts

### Setup & Configuration
- `setup_synced_blocks.py` - Initial setup, creates synced blocks
- `find_all_pages.py` - Discovers all Notion pages

### Daily Use
- `start_work.py` - Pre-work sync (pull from Notion)
- `end_work.py` - Post-work sync (push to Notion)
- `quick_sync.py` - Interactive sync menu

### Core Sync
- `pull_from_notion.py` - Pull Notion pages to README files
- `sync_readme_to_notion.py` - Push README files to Notion
- `notion_task_manager.py` - Manage tasks from Notion
- `generate_tasks_md.py` - Create tasks.md from cache
- `notion.py sync` - Sync all databases from Notion

## Project Mappings

All 8 projects have synced blocks configured:

| Project | Folder | Synced Block ID |
|---------|--------|-----------------|
| Permits & Legal | 01_Permits_Legal | 279bc994-24ab-804f... |
| Space & Ops | 02_Space_Ops | 279bc994-24ab-80db... |
| Theme & Design | 03_Theme_Design_Story | 279bc994-24ab-8143... |
| Marketing | 04_Marketing_Sales | 279bc994-24ab-81eb... |
| Team | 05_Team | 279bc994-24ab-813f... |
| Budget | 06_Budget_Finance | 279bc994-24ab-81a4... |
| Vendors | 07_Vendors_Suppliers | 279bc994-24ab-8139... |
| Evaluation | 08_Evaluation_Scaling | 279bc994-24ab-81be... |

## Tips

### Quick Mode
Skip README pull for faster sync:
```bash
python scripts/start_work.py --quick
```

### Check What Changed
View recently modified files:
```bash
python scripts/end_work.py
# Shows files modified in last 8 hours
```

### Manual Task Refresh
```bash
python scripts/notion_task_manager.py read
python scripts/generate_tasks_md.py
```

**For complete task management → See [`TASK_WORKFLOW.md`](TASK_WORKFLOW.md)**

## Troubleshooting

### "No synced block mappings found"
Run: `python scripts/setup_synced_blocks.py`

### "No cached Notion data"
Run: `python scripts/notion.py sync`

### Encoding errors on Windows
The scripts have been fixed for Windows compatibility. If you see unicode errors, the scripts use ASCII alternatives.

### Sync takes too long
Use `--quick` mode or sync individual projects instead of all at once.

## Best Practices

1. **Always run `start_work.py` before beginning work** - This ensures you have the latest content
2. **Run `end_work.py` after making changes** - This pushes your updates to the team
3. **Check backups folder if something goes wrong** - All overwrites are backed up
4. **Use project-specific sync for faster updates** - Don't sync everything if you only changed one project

## Workflow Example

```bash
# Morning
$ python scripts/start_work.py
[OK] Database sync complete
[OK] Task files generated
Pull all README files from Notion? (y/n/skip): y
[OK] README files synced from Notion
[OK] SYNC COMPLETE - Ready to work!

# ... work on project files ...

# Evening
$ python scripts/end_work.py
Modified README files (last 8 hours):
  - 01_Permits_Legal
  - 03_Theme_Design_Story
Push all modified READMEs to Notion? (y/n/select): y
[OK] All READMEs pushed to Notion
[OK] END-OF-WORK SYNC COMPLETE
```

Remember: The goal is to let you work in markdown while the team sees updates in Notion!