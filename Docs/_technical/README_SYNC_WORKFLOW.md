# README-Notion Sync Workflow

## The Complete Picture

### Current State
- **READMEs**: Created as one-off from core.md (static snapshots)
- **Notion Data**: Lives in cache/ after sync (dynamic, updated)
- **Gap**: READMEs don't auto-update from Notion changes

### New Workflow

```
Your Team                You                    AI Agents
   ↓                      ↓                         ↓
[Notion] ←→ [Local Repo Cache] ←→ [README Files] ←→ [AI Analysis]
         sync          update             read
         push          extract           suggest
```

## Daily Workflow

### Morning Sync (Get Latest from Team)
```bash
# 1. Pull latest from Notion
python scripts/notion.py sync

# 2. Update READMEs with new tasks
python scripts/notion_readme_sync.py update

# 3. Check what needs attention
python scripts/notion.py analyze
```

### During Day (AI Collaboration)
- Edit README files directly
- Add AI insights and plans
- Mark changes for Notion pushback

### Evening Push (Send Updates to Team)
```bash
# 1. Check what needs pushing
python scripts/notion_readme_sync.py check

# 2. Push updates to Notion (coming soon)
python scripts/notion.py push --from-readmes
```

## How to Mark Changes for Pushback

### Adding New Tasks to Notion
In any README, add:
```markdown
<!-- PUSH_TO_NOTION: task: "Research permit expediting services" -->
<!-- PUSH_TO_NOTION: task: "Call fire marshal for variance" -->
```

### Updating Task Status
```markdown
<!-- UPDATE_NOTION: 279bc994-24ab-8185-8be9-f0fb8c79a71b: status: "In Progress" -->
<!-- UPDATE_NOTION: 279bc994-24ab-8185-8be9-f0fb8c79a71b: priority: "Critical" -->
```

### Adding Notes
```markdown
<!-- NOTE_TO_NOTION: "Fire marshal requires additional documentation" -->
```

## README Structure After Sync

Each README will have:

```markdown
# 01 - Permits & Legal

[Original static content here]

<!-- NOTION_TASKS_START -->
## Active Tasks from Notion

### 🔴 High Priority
- ⏳ Research and submit all planning permits
  - Due: 2025-10-15
  - Status: Not started
  - ID: `279bc994-24ab-8184-94b3-edec4608474d`

### 🟡 Medium Priority
[Tasks auto-populated here]

*Last synced: 2025-09-25 11:45*
<!-- NOTION_TASKS_END -->
```

## The Two-Way Sync Philosophy

### What Syncs FROM Notion → READMEs
- Task lists with status
- Due dates
- Priority levels
- Assignees

### What Pushes FROM READMEs → Notion
- New tasks you create
- Status updates you make
- Priority changes
- Notes and comments

### What Stays Local (AI Workspace)
- Detailed plans
- AI-generated insights
- Extended documentation
- Strategic notes

## Benefits of This Approach

1. **Team Independence**: Team works in Notion without friction
2. **AI Power**: You get full repo for AI collaboration
3. **Selective Sync**: Only push what matters back
4. **Context Preservation**: READMEs maintain rich context
5. **Audit Trail**: See exactly what changed

## Implementation Status

### ✅ Working Now
- Notion → Cache sync (`notion.py sync`)
- Cache → README updates (`notion_readme_sync.py update`)
- Change detection (`notion_readme_sync.py check`)

### 🚧 Coming Next
- README → Notion push (`notion.py push`)
- Conflict resolution
- Batch operations
- Automatic scheduling

## Quick Reference

```bash
# Full workflow
python scripts/notion.py discover          # One time
python scripts/notion.py sync              # Get from Notion
python scripts/notion_readme_sync.py update # Update READMEs
# ... work with AI on READMEs ...
python scripts/notion_readme_sync.py check  # See changes
python scripts/notion.py push              # Send to Notion (soon)
```

## Architecture Decision Record (ADR)

### Why This Design?

1. **Vertical Slices**: Each folder is self-contained context
2. **Cache Layer**: Prevents accidental overwrites
3. **Explicit Push**: You control what goes back to Notion
4. **Markdown Native**: AI agents work best with markdown
5. **Git Friendly**: All changes tracked in version control

### Trade-offs

**Pros**:
- Clear separation of concerns
- No accidental data loss
- Full AI context per project
- Team workflow unchanged

**Cons**:
- Extra sync step
- Potential for drift
- Manual pushback markers
- Two sources to maintain

### Future Enhancements

1. **Auto-sync on schedule** (cron/GitHub Actions)
2. **Conflict UI** for handling divergence
3. **Smart merging** of README changes
4. **Webhook from Notion** for real-time sync
5. **README templates** with sync markers

---

*This workflow enables powerful AI collaboration while keeping your team's Notion workflow intact.*