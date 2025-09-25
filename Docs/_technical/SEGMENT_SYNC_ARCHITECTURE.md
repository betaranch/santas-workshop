# Segment Sync Architecture - The Complete Solution

## The Vision

Your team works in Notion. You work with AI in the repo. Specific segments sync bi-directionally.

```
Team's Notion Page                    Your Local Repo
┌─────────────────────┐               ┌──────────────────┐
│ Project Overview    │               │                  │
│ (not synced)        │               │  README.md       │
├─────────────────────┤               │  (entire file)   │
│ <!-- SYNC_START --> │ <-----------> │                  │
│ Documentation       │     SYNCS      │                  │
│ Plans, Details      │               │                  │
│ <!-- SYNC_END -->   │               │                  │
├─────────────────────┤               └──────────────────┘
│ Other Notion stuff  │
│ (not synced)        │               tasks.md (Phase 2)
└─────────────────────┘               (filtered tasks)
```

## Implementation Phases

### Phase 1: Segment Sync (NOW)
✅ Sync marked segments in Notion pages with README files
✅ Bi-directional flow
✅ Preserves other Notion content

### Phase 2: Task Aggregation (NEXT)
- Add `tasks.md` files to each folder
- Pull filtered tasks from Tasks database
- Show only tasks assigned to that project
- Read-only initially

### Phase 3: Full Integration (FUTURE)
- Task status updates from tasks.md
- New task creation from markdown
- Cross-references between README and tasks

## How Segment Sync Works

### 1. Setup in Notion

In each project page, add markers:

```html
Other content stays untouched...

<!-- SYNC_START:permits_content -->

## Everything between these markers syncs

Your documentation, plans, details go here.
This entire section syncs with the README.md file.

- Checkboxes work
- Lists work
- Headers work
- Everything converts properly

<!-- SYNC_END:permits_content -->

Other Notion content continues...
```

### 2. Setup Locally

Configure which pages to sync:
```bash
python scripts/notion_segment_sync.py setup
```

Enter the Notion page ID for each project when prompted.

### 3. Daily Workflow

#### Morning: Get Team Updates
```bash
# Pull segments from Notion to READMEs
python scripts/notion_segment_sync.py pull
```

#### Work with AI
- Edit README files
- AI agents read/modify READMEs
- All changes tracked in git

#### Evening: Push Updates
```bash
# Push README changes back to Notion segments
python scripts/notion_segment_sync.py push
```

## The Complete File Structure

```
Docs/
├── 01_Permits_Legal/
│   ├── README.md        # Syncs with Notion segment
│   └── tasks.md         # (Phase 2) Filtered task view
├── 02_Space_Ops/
│   ├── README.md        # Syncs with Notion segment
│   └── tasks.md         # (Phase 2) Filtered task view
...
```

## Why This Architecture Works

### 1. **Clean Separation**
- Documentation (README) vs Tasks (database) stay separate
- Each serves its purpose without confusion

### 2. **Team Friendly**
- Team never leaves Notion
- They see your updates in their normal workflow
- No new tools to learn

### 3. **AI Optimized**
- Each folder is focused context
- README has narrative/planning
- tasks.md has execution items
- AI can see both together

### 4. **Conflict Minimal**
- Only synced segments change
- Other Notion content untouched
- Clear boundaries reduce conflicts

### 5. **Audit Trail**
- Git tracks all README changes
- Notion tracks edit history
- You can always see who changed what

## Configuration Example

`cache/segment_map.json`:
```json
{
  "01_Permits_Legal": {
    "page_id": "abc-123-notion-page-id",
    "segment_marker": "permits_content",
    "title": "Permits & Legal"
  },
  "02_Space_Ops": {
    "page_id": "def-456-notion-page-id",
    "segment_marker": "space_ops_content",
    "title": "Space & Operations"
  }
}
```

## Notion Page Setup

Each project page in Notion needs:

1. **A dedicated documentation section** marked with HTML comments
2. **The segment marker** matching your configuration
3. **Team agreement** that content between markers is "yours"

Example Notion page structure:
```
# Permits & Legal (Project Page)

## Quick Links
[Dashboard] [Tasks] [Calendar]

## Team Updates
Latest from the team...

<!-- SYNC_START:permits_content -->

# Permits & Legal Documentation

This entire section syncs with Docs/01_Permits_Legal/README.md

## Current Status
- [ ] Zoning permit submitted
- [ ] Fire marshal meeting scheduled
...

<!-- SYNC_END:permits_content -->

## Meeting Notes
Team meeting notes stay here...

## Resources
Links and files...
```

## Advanced Usage

### Sync Single Folder
```bash
python scripts/notion_segment_sync.py pull-one 01_Permits_Legal
python scripts/notion_segment_sync.py push-one 01_Permits_Legal
```

### Check What Changed
```bash
# See local changes before pushing
git diff Docs/01_Permits_Legal/README.md

# See what would be pushed
python scripts/notion_segment_sync.py check
```

## Phase 2 Preview: Task Sync

Coming next - `tasks.md` files that aggregate:

```markdown
# Tasks for Permits & Legal

## High Priority
- [ ] Submit zoning application (Due: Oct 15)
  - ID: task-id-123
  - Assigned: John
  - Status: In Progress

## Medium Priority
- [ ] Schedule fire marshal meeting (Due: Oct 20)
  - ID: task-id-456
  - Assigned: Unassigned
  - Status: Not Started
```

These task files will:
- Auto-generate from Tasks database
- Filter by project relation
- Update on sync
- Eventually allow status updates back to Notion

## Best Practices

1. **Sync Frequency**
   - Pull in morning
   - Push in evening
   - Pull after team mentions changes

2. **Conflict Resolution**
   - Always pull before push
   - Review changes with `git diff`
   - Communicate major changes to team

3. **Marker Placement**
   - Put markers around complete sections
   - Don't split mid-list or mid-paragraph
   - Keep markers visible to team

4. **Content Organization**
   - Keep README focused on planning/documentation
   - Save tasks for tasks.md (coming soon)
   - Use clear headers for navigation

## Troubleshooting

**"Sync markers not found"**
- Add the HTML comments to your Notion page
- Ensure marker name matches configuration

**"No page configured"**
- Run `python scripts/notion_segment_sync.py setup`
- Get page ID from Notion URL (after last dash)

**"Push overwrites my changes"**
- Always pull first
- Use git to track changes
- Consider smaller, more frequent syncs

## Summary

This architecture gives you:
- ✅ Team stays in Notion
- ✅ You work with AI in markdown
- ✅ Selective bi-directional sync
- ✅ Clear separation of concerns
- ✅ Minimal conflicts
- ✅ Full audit trail

The segment sync solves the core problem: keeping documentation synchronized while maintaining separate workflows for you and your team.