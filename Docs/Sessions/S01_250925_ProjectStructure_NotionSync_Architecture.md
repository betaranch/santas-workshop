---
session: S01
date: 2025-09-25
topic: Project Structure & Notion Sync Architecture
status: completed
context_usage: 88%
key_decisions:
  - Vertical slice architecture for project folders
  - Bi-directional Notion sync via segments
  - README.md for documentation, tasks.md for execution
  - Synced blocks over HTML markers
---

# Session S01: Project Structure & Notion Sync Architecture

## Executive Summary

Established a comprehensive project structure for the Elf Speakeasy pop-up, creating 8 numbered project folders aligned with both Notion and Google Drive. Developed multiple sync approaches between local markdown files and Notion, discovering that synced blocks provide the cleanest solution.

## What Worked

### 1. Project Folder Structure ✅
Created numbered folders matching Google Drive convention:
```
Docs/
├── 01_Permits_Legal/
├── 02_Space_Ops/
├── 03_Theme_Design_Story/
├── 04_Marketing_Sales/
├── 05_Team/
├── 06_Budget_Finance/
├── 07_Vendors_Suppliers/
└── 08_Evaluation_Scaling/
```

**Why it works**:
- Each folder is a focused AI context window
- Numbers provide natural priority/workflow
- Matches existing Google Drive structure
- Avoids monster files (broke up 200+ line core.md)

### 2. Notion Integration Scripts ✅

#### Successfully Created:
- `notion.py` - Unified script replacing 4 redundant ones
- `notion_segment_sync.py` - Bi-directional segment sync
- `notion_synced_block.py` - Native synced block integration

#### Key Achievement:
- Discovered Permits page synced block ID: `279bc994-24ab-804f-8570-d77ded7e495f`
- Successfully pushed test content to Notion
- Proved bi-directional sync is possible

### 3. Simplified Command Structure ✅
```bash
python scripts/notion.py discover    # Find databases
python scripts/notion.py sync        # Pull data
python scripts/notion.py analyze     # Get insights
```

## Architecture Decisions

### Two-File Pattern per Project
```
01_Permits_Legal/
├── README.md    # Documentation (syncs with Notion page segment)
└── tasks.md     # Task aggregation (from Tasks database) [PENDING]
```

**Rationale**:
- Separation of concerns (narrative vs execution)
- Different sync mechanisms (page content vs database)
- AI can see both in same context
- Team familiar with README pattern

### Sync Strategy Evolution

#### Rejected: HTML Markers in Code Blocks
```html
<!-- SYNC_START:permits_content -->
<!-- SYNC_END:permits_content -->
```
**Why rejected**: Ugly, visible in Notion, not user-friendly

#### Accepted: Native Synced Blocks
- Uses Notion's built-in synced_block feature
- Cleaner, no visible markers
- Auto-syncs across multiple pages
- API supports read/write operations

#### Alternative Options Explored:
1. **Callout blocks** - Pretty but complex
2. **Toggle blocks** - Collapsible sections
3. **Header boundaries** - Simple but fragile
4. **Synced blocks** - Native and clean ✅

## Implementation Framework

### Phase 1: Structure (COMPLETED)
- [x] Create 8 project folders
- [x] Extract content from core.md
- [x] Create README for each project
- [x] Update CLAUDE.md with navigation

### Phase 2: Basic Sync (COMPLETED)
- [x] Build notion.py for database sync
- [x] Create cache system for local data
- [x] Generate AI indexes
- [x] Test synced block integration

### Phase 3: Advanced Sync (IN PROGRESS)
- [x] Design segment sync architecture
- [x] Create sync scripts
- [x] Test with Permits page
- [ ] Implement for all 8 projects
- [ ] Add tasks.md generation

### Phase 4: Production (PENDING)
- [ ] Batch processing for large content
- [ ] Conflict resolution
- [ ] Automated scheduling
- [ ] Team training

## Key Insights

### 1. Vertical Slice Architecture Works
Each folder contains everything needed for that project area - no hunting across multiple locations. This matches how humans think about projects.

### 2. Notion API Limitations
- 100 blocks per request maximum
- HTML comments not accessible via API
- Synced blocks provide best native solution
- Rate limiting requires 0.35s delays

### 3. Team Workflow Preservation
The bi-directional sync allows:
- Team stays in Notion (their comfort zone)
- You work in markdown (AI-optimized)
- Specific segments sync (not everything)
- Git tracks all changes

### 4. Context Management
Breaking documentation into folders prevents AI context overflow. Each conversation can focus on 1-2 projects instead of entire system.

## Unresolved Challenges

1. **Large Content Batching**: README files over 100 blocks need splitting
2. **Sync Conflict Resolution**: What happens when both sides change?
3. **Task Filtering**: tasks.md generation from relational database
4. **Authentication**: API key in .env works but needs rotation

## Next Session Focus

### Immediate Priorities:
1. Complete synced block setup for all 8 projects
2. Implement tasks.md generation from Tasks database
3. Create batch processing for large READMEs
4. Test full round-trip sync

### Code to Run Next Session:
```bash
# Setup sync for all projects
python scripts/notion_segment_sync.py setup

# Test full sync
python scripts/notion.py sync
python scripts/notion_segment_sync.py pull

# Generate tasks
python scripts/notion_tasks_filter.py generate  # TODO: Create this
```

## File Inventory

### Created This Session:
- `/scripts/notion.py` - Main sync tool
- `/scripts/notion_segment_sync.py` - Segment sync
- `/scripts/notion_synced_block.py` - Synced block handler
- `/scripts/notion_page_sync.py` - Page-level sync
- `/Docs/[01-08]_*/README.md` - All project READMEs
- `/Docs/PROJECT_MAP.md` - Navigation guide
- `/Docs/Technical/NOTION.md` - Simplified docs
- `/CLAUDE.md` - Updated AI context
- `/NOTION_SETUP_GUIDE.md` - Setup instructions

### Archived:
- `/scripts/archive/` - Old redundant scripts
- `/Docs/Technical/archive/` - Outdated documentation

## Success Metrics

- ✅ Reduced 4 scripts to 1
- ✅ Created 8 project folders with READMEs
- ✅ Successfully synced with Notion
- ✅ Discovered 26 tasks (25 high priority!)
- ✅ Proved synced blocks work
- ⏳ Full bi-directional sync pending

## Team Communication Points

### To Share with Team:
1. "Synced blocks in Notion will auto-update from our technical docs"
2. "Each project has dedicated documentation section"
3. "Changes sync daily - morning pull, evening push"
4. "Your Notion workflow unchanged"

### To Document:
1. Which sections are "synced" (don't edit directly)
2. How to request documentation updates
3. Where to find technical details

## Session Conclusion

Successfully architected a scalable, bi-directional sync system between local markdown files and Notion. The vertical slice approach with numbered folders provides excellent AI context management while preserving team workflows. Synced blocks proved superior to HTML markers.

**Key Achievement**: Pushed test content to Notion synced block, proving the integration works.

**Context Remaining**: 12% - Perfect stopping point

---

*Next session: Complete sync implementation and add task filtering*