# Notion Integration Guide

## Quick Start (30 seconds)

```bash
# First time only - discover your databases
python scripts/notion.py discover

# Daily use - sync and analyze
python scripts/notion.py sync
python scripts/notion.py analyze
```

That's it. You're done.

## Setup

### 1. Environment Variables (.env)
```
NOTION_API=your_api_key_here
NOTION_WORKSPACE_URL=https://www.notion.so/Your-Page-URL
```

### 2. Available Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `discover` | Find all databases | First time setup |
| `sync` | Pull latest data | Daily, or after Notion changes |
| `analyze` | Get AI insights | When planning your day |
| `status` | Quick overview | Anytime |

## Data Structure

```
cache/
├── notion_config.json      # Auto-discovered database IDs
├── content/                # Raw Notion data (timestamped)
└── indexes/                # AI-processed insights
    ├── high_priority.json  # Urgent tasks
    ├── upcoming_deadlines.json
    └── summary.json        # Statistics
```

## Common Workflows

### Morning Review
```bash
python scripts/notion.py sync      # Get latest
python scripts/notion.py analyze   # See priorities
```

### Check Project Health
```bash
python scripts/notion.py status    # Quick stats
cat cache/indexes/summary.json     # Detailed breakdown
```

### Troubleshooting
```bash
# If databases change in Notion
python scripts/notion.py discover --force

# If you see old data
python scripts/notion.py sync
```

## Current Project Status

As of last sync:
- **26 tasks** total (100% not started)
- **25 high priority** items (needs reprioritization)
- **First deadline**: October 1 (Marketing & Finance)
- **Most urgent**: Source furniture quotes (Oct 3)

## Technical Details

### API Configuration
- Uses Notion API v2022-06-28
- Rate limited to ~3 requests/second
- Handles pagination automatically
- Caches results locally for speed

### Database Mapping
The system auto-discovers and categorizes:
- Tasks → `tasks`
- Projects → `projects`
- Notes/Resources → `notes`

### File Formats
- All data stored as JSON
- Timestamps in ISO 8601 format
- UTF-8 encoding throughout

## FAQ

**Q: How often should I sync?**
A: Daily minimum, or after making changes in Notion

**Q: Can it push changes back to Notion?**
A: Not yet - current version is read-only for safety

**Q: Where's the detailed API documentation?**
A: Archived. The new system auto-discovers everything.

**Q: What if I get errors?**
A: Check your .env file, then run `discover --force`

---

*Single source of truth for Notion integration*
*Last updated: September 25, 2025*