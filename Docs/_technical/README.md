# Technical Documentation

Central hub for all technical documentation and system guides.

## 📚 Active Documentation

### **NOTION.md** - Notion Integration (Primary)
Complete guide for syncing with Notion. Everything you need in one place.

```bash
# Quick commands
python scripts/notion.py discover   # Setup
python scripts/notion.py sync       # Get data
python scripts/notion.py analyze    # Get insights
```

## 📁 Project Structure

```
scripts/
├── notion.py           # Single unified Notion script
└── archive/            # Old deprecated scripts

cache/
├── notion_config.json  # Auto-discovered configuration
├── content/            # Synced Notion data
└── indexes/            # AI-processed insights

Docs/
├── core.md             # Project plan
└── Technical/
    ├── README.md       # This file
    ├── NOTION.md       # Notion integration guide
    └── archive/        # Historical documentation
```

## 🚀 Quick Start

1. **Setup**: Configure `.env` with your Notion credentials
2. **Discover**: `python scripts/notion.py discover`
3. **Sync**: `python scripts/notion.py sync`
4. **Analyze**: `python scripts/notion.py analyze`

## 📊 Current Status

- **System**: Simplified to single `notion.py` script
- **Data**: 26 tasks synced, 25 high priority
- **Cache**: Auto-updating with timestamps
- **Indexes**: AI-ready for analysis

---

*For historical documentation, see the `archive/` folder*