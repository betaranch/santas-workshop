# Notion Integration Technical Documentation

## Overview

This project uses a bi-directional sync system between local markdown files and Notion pages. Team members can work in either environment with changes synchronized automatically.

## Architecture

### Sync Flow Diagram

```
┌─────────────┐          ┌─────────────┐          ┌─────────────┐
│   NOTION    │◄────────►│    LOCAL    │◄────────►│     GIT     │
│   PAGES     │          │  MARKDOWN   │          │    REPO     │
└─────────────┘          └─────────────┘          └─────────────┘
      ▲                        ▲
      │                        │
      ▼                        ▼
┌─────────────┐          ┌─────────────┐
│   NOTION    │          │   tasks.md  │
│  DATABASES  │─────────►│    FILES    │
└─────────────┘          └─────────────┘
```

### Components

1. **Synced Blocks** - Native Notion feature for embedding synchronized content
2. **API Integration** - Python scripts using Notion API v2022-06-28
3. **Conflict Detection** - Timestamp-based conflict checking
4. **Backup System** - Automatic versioned backups

## Implementation Details

### Synced Block Configuration

Each project page has a dedicated synced block:

```json
{
  "01_Permits_Legal": {
    "page_id": "278bc994-24ab-81b1-9fcc-d252f2d2aef9",
    "synced_block_id": "279bc994-24ab-804f-8570-d77ded7e495f"
  },
  // ... 7 more projects
}
```

Stored in: `/cache/synced_blocks.json`

### Scripts Architecture

#### Core Sync Scripts

| Script | Purpose | Direction | Trigger |
|--------|---------|-----------|---------|
| `pull_from_notion.py` | Pull page content to markdown | Notion → Local | Manual/Pre-work |
| `sync_readme_to_notion.py` | Push markdown to Notion | Local → Notion | Manual/Post-work |
| `notion.py sync` | Sync databases to cache | Notion → Cache | Daily |
| `generate_tasks_md.py` | Create task files | Cache → Local | After DB sync |

#### Workflow Scripts

| Script | Purpose | Components Used |
|--------|---------|-----------------|
| `start_work.py` | Pre-work sync | notion.py, generate_tasks_md, pull_from_notion |
| `end_work.py` | Post-work sync | sync_readme_to_notion, git status |
| `quick_sync.py` | Interactive menu | sync_readme_to_notion |

#### Setup Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `setup_synced_blocks.py` | Create synced blocks | Initial setup only |
| `find_all_pages.py` | Discover Notion pages | Debugging/Discovery |

### Markdown ↔ Notion Block Conversion

#### Markdown to Notion

| Markdown | Notion Block Type |
|----------|------------------|
| `# Header` | heading_1 |
| `## Header` | heading_2 |
| `### Header` | heading_3 |
| `- Item` | bulleted_list_item |
| `1. Item` | numbered_list_item |
| `` `code` `` | code (inline) |
| ` ```lang ` | code (block) |
| `> Quote` | quote |
| `---` | divider |
| `**bold**` | rich_text with bold |
| `*italic*` | rich_text with italic |

#### Notion to Markdown

| Notion Block | Markdown Output |
|--------------|-----------------|
| heading_1-3 | `#`, `##`, `###` |
| paragraph | Plain text |
| bulleted_list | `- Item` |
| numbered_list | `1. Item` |
| code | ` ```language` block |
| quote | `> Text` |
| callout | `> 📌 Text` |
| toggle | `<details>` tag |
| divider | `---` |

### Conflict Resolution

1. **Detection**: File modification time < 30 minutes triggers warning
2. **Backup**: Automatic backup to `/backups/[project]/README_[timestamp].md`
3. **Options**:
   - Skip the file
   - View diff
   - Force overwrite
4. **Retention**: Keeps last 10 backups per project

### API Limits & Optimization

- **Rate Limiting**: 0.35s delay between requests
- **Batch Size**: 100 blocks maximum per request
- **Retry Logic**: Not implemented (fails fast)
- **Caching**: Timestamped cache files in `/cache/content/`

## Configuration

### Environment Variables (.env)

```bash
NOTION_API=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_WORKSPACE_URL=https://www.notion.so/workspace/...
```

### Cache Structure

```
cache/
├── synced_blocks.json      # Block ID mappings
├── notion_config.json       # Discovered databases
├── all_pages.json          # Page discovery results
├── content/                # Database content cache
│   └── db_[id]_[timestamp].json
└── last_sync.txt           # Sync timestamp
```

### Backup Structure

```
backups/
├── 01_Permits_Legal/
│   ├── README_20250925_120000.md
│   └── README_20250925_140000.md
├── 02_Space_Ops/
│   └── README_20250925_120000.md
└── ...
```

## Task Categorization

Tasks are automatically categorized using keyword matching:

```python
project_keywords = {
    "01_Permits_Legal": ["permit", "legal", "license", "TCO", "zoning"],
    "02_Space_Ops": ["space", "operation", "layout", "furniture"],
    "03_Theme_Design_Story": ["theme", "design", "story", "vignette"],
    // ... more mappings
}
```

Success rate: 93% (14 of 15 tasks categorized correctly)

## Error Handling

### Common Issues & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| "No synced block mappings" | Initial setup not done | Run `setup_synced_blocks.py` |
| "No cached Notion data" | Database not synced | Run `notion.py sync` |
| Unicode/Emoji errors | Windows encoding | Fixed with ASCII fallbacks |
| 400 Bad Request | Invalid emoji in API | Use supported emoji only |
| Timeout | Large content | Use individual project sync |

### Debugging Commands

```bash
# Check current configuration
python scripts/notion.py

# Discover all pages
python scripts/find_all_pages.py

# Test specific sync
python scripts/pull_from_notion.py 01_Permits_Legal

# Force sync without conflicts
python scripts/pull_from_notion.py --force
```

## Best Practices

1. **Always backup before major syncs** - Automatic but verify
2. **Use project-specific sync for speed** - Don't sync all if only one changed
3. **Run start_work.py religiously** - Prevents conflicts
4. **Check git status before committing** - Ensure sync complete
5. **Use --quick mode for minor updates** - Skips README pull

## Performance Metrics

- **Full sync time**: ~2-3 minutes (all 8 projects)
- **Single project sync**: ~15 seconds
- **Task generation**: ~5 seconds
- **Database sync**: ~10 seconds
- **Markdown conversion**: ~90 blocks/second

## Security Considerations

1. **API Key**: Stored in `.env`, never committed
2. **Backups**: Local only, not synced to git
3. **Cache**: Contains full content, gitignored
4. **Rate Limiting**: Prevents API abuse
5. **Permissions**: Read/write to workspace pages only

## Future Enhancements

### Planned
- [ ] Two-way task status sync
- [ ] Attachment/image support
- [ ] Change detection (sync only modified)
- [ ] Automated scheduling (cron/Task Scheduler)

### Considered
- [ ] Conflict merge UI
- [ ] Rollback functionality
- [ ] Sync status dashboard
- [ ] Team permissions management

## Maintenance

### Regular Tasks
- Clean old backups: Automatic (keeps last 10)
- Update cache: Daily via `start_work.py`
- Check API version: Quarterly

### Monitoring
- Check `/cache/` size periodically
- Review backup retention policy
- Monitor API rate limits

---

*Last Updated: September 25, 2025*
*API Version: Notion 2022-06-28*
*Python Version: 3.11+*