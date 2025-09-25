# Project Navigation Map

## 🗺️ Quick Navigation

### Start Here
1. **Daily Workflow**: Run `python scripts/start_work.py` before working
2. **Project Folders**: Navigate to `Docs/[01-08]_*/` for specific areas
3. **Current Tasks**: Check `tasks.md` in each folder
4. **Push Changes**: Run `python scripts/end_work.py` after working

## 📂 Directory Structure

```
santas-workshop/
├── README.md                 # Main project overview
├── SYNC_WORKFLOW.md         # Complete sync instructions
├── TASK_WORKFLOW.md         # Task management guide
├── CLAUDE.md                # AI assistant context
├── .env                     # API keys (create from .env.example)
│
├── scripts/                 # All sync and utility scripts
│   ├── start_work.py       # ⭐ Run before working
│   ├── end_work.py         # ⭐ Run after working
│   ├── quick_sync.py       # Interactive sync menu
│   ├── notion_task_manager.py # Task operations
│   ├── generate_tasks_md.py # Create task files
│   ├── pull_from_notion.py # Pull content from Notion
│   ├── sync_readme_to_notion.py # Push to Notion
│   └── [other scripts...]
│
├── Docs/                    # All project documentation
│   ├── PROJECT_MAP.md      # This file
│   ├── core.md             # Original project brief
│   │
│   ├── 01_Permits_Legal/   # 🔴 CRITICAL PATH
│   │   ├── README.md       # Permit requirements & status
│   │   └── tasks.md        # Current permit tasks
│   │
│   ├── 02_Space_Ops/       # Venue & Operations
│   │   ├── README.md       # Layout, setup, operations
│   │   └── tasks.md        # Space-related tasks
│   │
│   ├── 03_Theme_Design_Story/  # Creative & Design
│   │   ├── README.md       # Themes, stories, aesthetics
│   │   └── tasks.md        # Design tasks
│   │
│   ├── 04_Marketing_Sales/ # Marketing & Revenue
│   │   ├── README.md       # Marketing strategy, sales
│   │   └── tasks.md        # Marketing tasks
│   │
│   ├── 05_Team/            # 🔴 CRITICAL - Staffing
│   │   ├── README.md       # Recruiting, training
│   │   └── tasks.md        # Team tasks
│   │
│   ├── 06_Budget_Finance/  # Financial Planning
│   │   ├── README.md       # Budget, expenses, revenue
│   │   └── tasks.md        # Finance tasks
│   │
│   ├── 07_Vendors_Suppliers/  # Procurement
│   │   ├── README.md       # Vendor relationships
│   │   └── tasks.md        # Procurement tasks
│   │
│   ├── 08_Evaluation_Scaling/  # Future Growth
│   │   ├── README.md       # Metrics, expansion plans
│   │   └── tasks.md        # Evaluation tasks
│   │
│   ├── Sessions/           # Work session documentation
│   │   ├── S01_*.md       # Session 1: Project structure
│   │   └── S02_*.md       # Session 2: Sync implementation
│   │
│   └── Technical/          # Technical documentation
│       ├── NOTION.md       # Detailed sync architecture
│       └── TASKS.md        # Task system implementation
│
├── cache/                  # Notion sync cache (gitignored)
│   ├── synced_blocks.json # Block ID mappings
│   ├── content/           # Database content
│   ├── tasks/             # Task cache and reports
│   ├── indexes/           # Task indexes (priority, deadlines)
│   ├── task_config.json   # Task database mappings
│   ├── project_mapping.json # Project ID mappings
│   └── notion_config.json # API configuration
│
└── backups/               # Automatic backup files (gitignored)
    └── [project_name]/    # Per-project backups
        └── README_*.md    # Timestamped backups
```

## 🔄 Sync System Overview

### Two Types of Content

1. **README.md files** (Documentation)
   - Lives in each project folder
   - Syncs with Notion page content
   - Edit locally in markdown
   - Push changes with `sync_readme_to_notion.py`
   - Pull changes with `pull_from_notion.py`

2. **tasks.md files** (Task Lists)
   - Auto-generated from Notion Tasks database
   - Read-only (don't edit directly)
   - Updates when you run `start_work.py`
   - Organized by priority and project

### Sync Workflow

```
Morning Routine:
┌──────────────┐
│start_work.py │ ──► Pulls tasks ──► Generates tasks.md
└──────────────┘     ──► Optionally pulls READMEs

During Work:
┌──────────────┐
│Edit README.md│ ──► Work in markdown locally
└──────────────┘

Evening Routine:
┌──────────────┐
│end_work.py   │ ──► Pushes README changes to Notion
└──────────────┘
```

## 📋 How to Use This Project

### First Time Setup
1. Clone repository
2. Copy `.env.example` to `.env` and add Notion API key
3. Run `pip install python-dotenv requests`
4. Run `python scripts/setup_synced_blocks.py` (one time)

### Daily Use
1. **Start**: `python scripts/start_work.py`
2. **Navigate**: Go to relevant project folder
3. **Check**: Read `tasks.md` for priorities
4. **Edit**: Modify `README.md` as needed
5. **End**: `python scripts/end_work.py`

### Finding Information

| Looking for... | Check here... |
|---------------|---------------|
| Current tasks | `Docs/*/tasks.md` |
| Task management | `TASK_WORKFLOW.md` |
| Permit status | `Docs/01_Permits_Legal/` |
| Budget info | `Docs/06_Budget_Finance/` |
| Team needs | `Docs/05_Team/` |
| Design concepts | `Docs/03_Theme_Design_Story/` |
| Sync help | `SYNC_WORKFLOW.md` |
| Technical - Sync | `Docs/Technical/NOTION.md` |
| Technical - Tasks | `Docs/Technical/TASKS.md` |

## 🎯 Current Priorities

### Critical Path Items (🔴)
1. **Permits & Legal** - All permits by Oct 31
2. **Team Recruiting** - 6-8 staff needed
3. **Venue Confirmation** - 345 SW Century Dr decision

### High Priority (🟡)
- Space layout and operations plan
- Theme and design finalization
- Marketing calendar development
- Vendor sourcing and quotes

### Task Distribution
- Total Tasks: 15
- High Priority: 14
- Categorized: 93%
- Uncategorized: 1

## 📝 Key Files Explained

### Configuration Files
- `.env` - Contains Notion API key (never commit!)
- `.env.example` - Template for environment setup
- `.gitignore` - Excludes cache, backups, and .env

### Documentation Files
- `README.md` - Main project overview
- `CLAUDE.md` - Instructions for AI assistant
- `SYNC_WORKFLOW.md` - Detailed sync instructions
- `PROJECT_MAP.md` - This navigation guide

### Working Files
- `*/README.md` - Project documentation (edit these!)
- `*/tasks.md` - Task lists (auto-generated, don't edit)

### Session History
- `Docs/Sessions/S*.md` - Work session summaries
- Tracks decisions, achievements, and learnings

## 🚀 Quick Commands Reference

```bash
# Essential Daily Commands
python scripts/start_work.py      # Before working
python scripts/end_work.py        # After working

# Sync Specific Project
python scripts/pull_from_notion.py 01_Permits_Legal
python scripts/sync_readme_to_notion.py 01_Permits_Legal

# Interactive Menu
python scripts/quick_sync.py

# Force Operations
python scripts/pull_from_notion.py --force  # Skip conflict checks
python scripts/start_work.py --quick        # Skip README pull

# Task Commands
python scripts/notion_task_manager.py read      # Pull latest tasks
python scripts/notion_task_manager.py duplicates # Find duplicates
python scripts/notion_task_manager.py dedupe    # Remove duplicates
python scripts/generate_tasks_md.py             # Regenerate task files

# Utility Commands
python scripts/notion.py sync                   # Sync databases
python scripts/find_all_pages.py               # Discover Notion pages
```

## 🛟 Troubleshooting

| Problem | Solution |
|---------|----------|
| "No synced block mappings" | Run `python scripts/setup_synced_blocks.py` |
| "No cached Notion data" | Run `python scripts/notion.py sync` |
| Sync takes too long | Use project-specific sync or `--quick` mode |
| Conflicting changes | Check `/backups/` folder for your version |
| Unicode errors | Scripts auto-handle, but check output |

## 📊 Project Stats

- **Timeline**: 7 weeks to launch
- **Budget**: $53.5K costs, $105K revenue target
- **Projects**: 8 main areas
- **Tasks**: 15 active (14 high priority)
- **Team Size**: 6-8 needed
- **Sync Scripts**: 12 created
- **Documentation**: Fully bi-directional

---

*Use this map to navigate the project efficiently. Remember: `start_work.py` before, `end_work.py` after!*