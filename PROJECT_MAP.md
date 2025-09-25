# Project Structure Map - Elf Speakeasy

## 🗂️ Folder Architecture for AI Navigation

This map helps AI agents (Claude, Codex, etc.) understand the project structure and find relevant information quickly.

## Project Folders

```
Docs/
├── 01_Permits_Legal/       → Compliance, licenses, regulatory
├── 02_Space_Ops/          → Venue, operations, logistics
├── 03_Theme_Design_Story/  → Creative, narrative, experience design
├── 04_Marketing_Sales/     → Promotion, revenue, partnerships
├── 05_Team/               → Staffing, training, characters
├── 06_Budget_Finance/      → Money, costs, profitability
├── 07_Vendors_Suppliers/   → External services, procurement
├── 08_Evaluation_Scaling/  → Metrics, growth, future planning
├── Technical/              → System documentation, APIs
└── core.md                → Master project overview
```

## Quick Navigation Guide

### By Topic:
- **Legal/Compliance** → Check `01_Permits_Legal`
- **Physical Space** → Check `02_Space_Ops`
- **Creative/Story** → Check `03_Theme_Design_Story`
- **Revenue/Sales** → Check `04_Marketing_Sales`
- **People/HR** → Check `05_Team`
- **Money/Budget** → Check `06_Budget_Finance`
- **Suppliers** → Check `07_Vendors_Suppliers`
- **Growth/Metrics** → Check `08_Evaluation_Scaling`

### By Urgency (October Deadlines):
1. **Oct 1**: Marketing launch → `04_Marketing_Sales`
2. **Oct 3**: Furniture quotes → `07_Vendors_Suppliers`
3. **Oct 5**: Corporate pipeline → `04_Marketing_Sales`
4. **Oct 15**: Permits complete → `01_Permits_Legal`
5. **Oct 15**: Design finalized → `03_Theme_Design_Story`
6. **Oct 20**: Staff hired → `05_Team`

### By System:
- **Notion Integration** → `Technical/NOTION.md`
- **Task Management** → `cache/indexes/` (via notion.py)
- **Project Planning** → `core.md`
- **AI Context** → `CLAUDE.md`

## Cross-References

### Dependencies:
- **Permits** impact → Space setup timeline
- **Design** drives → Marketing materials
- **Budget** constrains → All vendor decisions
- **Team** size affects → Operations planning
- **Marketing** success determines → Revenue/scaling

### Information Flow:
```
Notion (source) → notion.py → cache/ → Docs/[folders] → AI analysis
```

## For AI Agents

### When asked about:
- "What permits do we need?" → `01_Permits_Legal/README.md`
- "Show me the budget" → `06_Budget_Finance/README.md`
- "What's our marketing plan?" → `04_Marketing_Sales/README.md`
- "Explain the elf story" → `03_Theme_Design_Story/README.md`
- "How many staff needed?" → `05_Team/README.md`
- "Venue layout?" → `02_Space_Ops/README.md`
- "Vendor contacts?" → `07_Vendors_Suppliers/README.md`
- "Success metrics?" → `08_Evaluation_Scaling/README.md`

### Context Commands:
```
"Look in folder 03 for theme details"
"Check all folders for October deadlines"
"Compare budget in 06 with costs in 07"
"Find high-priority items across all projects"
```

## Data Locations

### Live Data:
- **Tasks**: `cache/content/tasks_*.json`
- **Projects**: `cache/content/projects_*.json`
- **Indexes**: `cache/indexes/*.json`

### Documentation:
- **Project Docs**: `Docs/[01-08]_*/README.md`
- **Technical**: `Docs/Technical/`
- **Archives**: `scripts/archive/` and `Docs/Technical/archive/`

### Configuration:
- **Environment**: `.env`
- **Notion Config**: `cache/notion_config.json`
- **AI Context**: `CLAUDE.md`

## Update Frequency

- **Daily**: Run `python scripts/notion.py sync`
- **Weekly**: Review project folders for updates
- **As Needed**: Update README.md files in each folder

## Quick Status Check

```bash
# Get latest from Notion
python scripts/notion.py sync

# See what needs attention
python scripts/notion.py analyze

# Check specific project
cat Docs/04_Marketing_Sales/README.md
```

---

*This map helps AI agents navigate the project efficiently. Each folder contains focused information for its domain.*