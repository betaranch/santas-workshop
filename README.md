# 🎅 Santa's Workshop - Elf Speakeasy Pop-Up Project

## Quick Start

```bash
# Before work: Pull from Notion
python scripts/start_work.py

# After work: Push to Notion
python scripts/end_work.py
```

**For complete sync instructions → See [`SYNC_WORKFLOW.md`](SYNC_WORKFLOW.md)**

## About

Immersive holiday experience in Bend, Oregon (Nov 1, 2025 - Jan 1, 2026). This repository syncs with Notion for team collaboration.

## Documentation Structure

| Document | Purpose | When to Read |
|----------|---------|--------------|
| **[`SYNC_WORKFLOW.md`](SYNC_WORKFLOW.md)** | 📋 Complete sync instructions | Setting up or troubleshooting |
| **[`TASK_WORKFLOW.md`](TASK_WORKFLOW.md)** | ✅ Task management guide | Managing project tasks |
| **[`Docs/PROJECT_MAP.md`](Docs/PROJECT_MAP.md)** | 🗺️ Full project navigation | Finding specific content |
| **[`CLAUDE.md`](CLAUDE.md)** | 🤖 AI context & workflow | Working with Claude |
| **[`Docs/Technical/`](Docs/Technical/)** | 🔧 Implementation details | Understanding the system |


## Project Folders

- **`Docs/01_Permits_Legal/`** → 🔴 Permits & compliance (CRITICAL PATH)
- **`Docs/02_Space_Ops/`** → Venue operations & layout
- **`Docs/03_Theme_Design_Story/`** → Creative & narrative
- **`Docs/04_Marketing_Sales/`** → Marketing & revenue
- **`Docs/05_Team/`** → 🔴 Staffing & training (CRITICAL)
- **`Docs/06_Budget_Finance/`** → Financial tracking
- **`Docs/07_Vendors_Suppliers/`** → Procurement
- **`Docs/08_Evaluation_Scaling/`** → Growth planning

Each contains: `README.md` (documentation) + `tasks.md` (current tasks)


## Current Status

- **Timeline**: 7 weeks to launch (Nov 1, 2025)
- **Budget**: $53.5K costs → $105K revenue target
- **Tasks**: 15 active (14 high priority)
- **Critical Path**: Permits by Oct 31, Staff recruited

## Documentation Doctrine

### Principles
1. **Single Source of Truth**: Each piece of information lives in ONE place
2. **Progressive Disclosure**: Start simple → link to details → deep dive available
3. **Working Files First**: Project READMEs are primary, meta-docs are secondary
4. **Sync Over Copy**: Content syncs with Notion, never duplicated

### Hierarchy
```
1. Project Docs (Source of Truth)
   └── Docs/[01-08]_*/README.md - Project-specific content

2. Navigation & Workflow (Meta-docs)
   ├── README.md (this file) - Entry point only
   ├── SYNC_WORKFLOW.md - Canonical sync instructions
   ├── TASK_WORKFLOW.md - Task management guide
   └── PROJECT_MAP.md - Navigation and structure

3. Context & Details (Reference)
   ├── CLAUDE.md - AI working context
   ├── Technical/NOTION.md - Sync implementation
   └── Technical/TASKS.md - Task system details
```

### Rules
- **Don't duplicate**: If it's in SYNC_WORKFLOW, don't repeat in README
- **Link liberally**: Point to the source rather than summarizing
- **Project content stays in project folders**: Not in root docs
- **Commands in one place**: SYNC_WORKFLOW.md is the source

## First Time Setup

1. Clone repo → 2. `pip install python-dotenv requests` → 3. Copy `.env.example` to `.env` → 4. Add Notion API key → 5. Run `python scripts/setup_synced_blocks.py`

**Full setup guide → [`SYNC_WORKFLOW.md`](SYNC_WORKFLOW.md)**

---

*Last Updated: September 25, 2025*
*Version: 2.0 - Full bi-directional sync implemented*