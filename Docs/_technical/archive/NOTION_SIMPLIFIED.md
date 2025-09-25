# Notion Integration - Simplified & Clear

## 🎯 The Big Picture

**ONE SCRIPT** does everything: `notion.py`

No more confusion. No more redundancy. Just simple, clear commands.

## ⚡ Quick Start

### First Time Setup (30 seconds)
```bash
python scripts/notion.py discover
```
This finds all your Notion databases and saves them. You only do this once.

### Daily Workflow
```bash
python scripts/notion.py sync      # Pull latest data (morning)
python scripts/notion.py analyze   # See what needs attention
python scripts/notion.py status    # Quick check anytime
```

## 📁 How It Works

### 1. Configuration (.env file)
```
NOTION_API=your_api_key_here
NOTION_WORKSPACE_URL=https://www.notion.so/Your-Page-URL
```
The script automatically extracts the page ID from your URL. No manual ID needed!

### 2. Data Flow
```
Notion Cloud
     ↓ (sync)
Local Cache (cache/ folder)
     ↓ (analyze)
AI Indexes (pre-processed insights)
     ↓
You see what matters
```

### 3. What Gets Stored Where

```
cache/
├── notion_config.json         # Your database IDs (auto-discovered)
├── content/                   # Raw data from Notion
│   ├── tasks_*.json           # All your tasks
│   ├── projects_*.json        # All your projects
│   └── notes_*.json           # All your notes
└── indexes/                   # Smart views of your data
    ├── high_priority.json     # Tasks needing attention
    ├── upcoming_deadlines.json # Sorted by due date
    ├── no_status.json         # Tasks that need triage
    └── summary.json           # Overall statistics
```

## 🔧 Commands Explained

### `discover` - Find Your Databases
- **When**: First time only (or use --force to refresh)
- **What**: Searches your entire Notion workspace
- **Result**: Saves all database IDs to `cache/notion_config.json`
- **Why**: So the script knows where to pull data from

### `sync` - Get Latest Data
- **When**: Daily, or whenever you want fresh data
- **What**: Pulls all tasks, projects, notes from Notion
- **Result**: Updates cache with latest data, creates AI indexes
- **Why**: Keeps your local copy current

### `analyze` - AI Insights
- **When**: When you need to know what to focus on
- **What**: Analyzes patterns in your data
- **Result**: Shows priorities, deadlines, recommendations
- **Why**: Helps you make decisions

### `status` - Quick Check
- **When**: Anytime you want to see the state
- **What**: Shows configuration, cache status, summary
- **Result**: One-page overview
- **Why**: Quick sanity check

## 🚀 Real Examples

### Morning Routine
```bash
# Start your day
python scripts/notion.py sync
python scripts/notion.py analyze

# Output shows:
# WARNING: 14 HIGH PRIORITY items need attention
# 6 items due this week
# Recommendation: Too many high-priority items, re-prioritize
```

### Quick Status Check
```bash
python scripts/notion.py status

# Shows:
# Configuration: ✓
# Databases: 3 (Tasks, Projects, Notes)
# Last sync: 10 minutes ago
# Total tasks: 26
```

### Force Refresh (if needed)
```bash
python scripts/notion.py discover --force  # Re-discover databases
python scripts/notion.py sync              # Pull fresh data
```

## ❓ FAQ

### Q: Why is this better than the old scripts?
**A:**
- One script instead of 4 confusing ones
- Auto-discovers your workspace (no hardcoded IDs)
- Clear commands that make sense
- Actually works reliably

### Q: What happened to the old scripts?
**A:** Archived in `scripts/archive/`. They were:
- `notion_fetch.py` - Partial functionality, now in `sync`
- `notion_tasks.py` - Broken, couldn't find databases
- `script.py` - Limited task creation
- `notion_sync.py` - Good but complex, now simplified

### Q: Do I need to edit the script?
**A:** No! Everything is configured via:
- `.env` file for credentials
- Auto-discovery for database IDs
- Cached configuration that persists

### Q: How often should I sync?
**A:**
- Daily minimum for active projects
- After making changes in Notion
- Before important meetings/reviews

### Q: Can it create tasks in Notion?
**A:** Not yet. Current version is read-only. This is intentional for safety.
Future version will add:
```bash
python scripts/notion.py create --task "New task name"
python scripts/notion.py update --status "In Progress"
```

## 🔍 Troubleshooting

### "ERROR: No NOTION_API key found"
→ Check your `.env` file has `NOTION_API=your_key_here`

### "ERROR: No page ID found"
→ Check your `.env` file has `NOTION_WORKSPACE_URL=your_url_here`

### Sync shows 0 items
→ Run `discover --force` to refresh database list

### Old data showing
→ Run `sync` to pull latest from Notion

## 📊 Understanding Your Data

After sync, check these files for insights:

1. **cache/indexes/high_priority.json**
   - Your urgent tasks in one place
   - Sorted by importance

2. **cache/indexes/upcoming_deadlines.json**
   - Everything with a due date
   - Sorted chronologically

3. **cache/indexes/summary.json**
   - Big picture statistics
   - Status distribution

## 🎯 The Philosophy

**Extreme Clarity**: Every command has one clear purpose
**No Surprises**: Data goes to predictable places
**Safety First**: Read-only for now, no accidental changes
**Progressive**: Start simple (sync), add complexity (analyze) only if needed

---

## Next Steps

1. Run `python scripts/notion.py discover` if you haven't already
2. Run `python scripts/notion.py sync` to get your data
3. Run `python scripts/notion.py analyze` to see insights
4. Check `cache/indexes/` for detailed JSON data

That's it. Simple, clear, powerful.