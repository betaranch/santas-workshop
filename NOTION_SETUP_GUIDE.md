# Notion Setup Guide - Add Sync Markers

## Quick Copy-Paste for Each Project Page

Open each project page in Notion and paste the corresponding markers below.
Put them where you want your synced documentation section to be.

---

### 1️⃣ Permits & Legal Page

```
<!-- SYNC_START:permits_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:permits_content -->
```

---

### 2️⃣ Space & Ops Page

```
<!-- SYNC_START:space_ops_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:space_ops_content -->
```

---

### 3️⃣ Story, Theme & Design Page

```
<!-- SYNC_START:theme_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:theme_content -->
```

---

### 4️⃣ Marketing & Sales Page

```
<!-- SYNC_START:marketing_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:marketing_content -->
```

---

### 5️⃣ Team Page

```
<!-- SYNC_START:team_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:team_content -->
```

---

### 6️⃣ Budget & Finance Page

```
<!-- SYNC_START:budget_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:budget_content -->
```

---

### 7️⃣ Vendors & Suppliers Page

```
<!-- SYNC_START:vendors_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:vendors_content -->
```

---

### 8️⃣ Evaluation & Scaling Page

```
<!-- SYNC_START:evaluation_content -->

Paste existing README content here if you want, or leave blank to pull from local README

<!-- SYNC_END:evaluation_content -->
```

---

## How to Add These in Notion

1. **Open the project page**
2. **Click where you want the synced section**
3. **Type or paste** the START marker
4. **Press Enter** a few times
5. **Type or paste** the END marker
6. **Done!**

## Getting the Page IDs

After adding markers, you need the page ID from each URL:

1. Open the project page
2. Look at your browser's address bar
3. Copy everything after the last dash

Example:
```
https://www.notion.so/Permits-Legal-278bc99424ab817e81bcd252f2d2aef9
                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                     This is what you need
```

## Page ID Checklist

Copy these IDs as you go:

- [ ] Permits & Legal: _______________________
- [ ] Space & Ops: _______________________
- [ ] Story, Theme & Design: _______________________
- [ ] Marketing & Sales: _______________________
- [ ] Team: _______________________
- [ ] Budget & Finance: _______________________
- [ ] Vendors & Suppliers: _______________________
- [ ] Evaluation & Scaling: _______________________

## Final Step: Configure the Script

Once all markers are added and you have all IDs:

```bash
cd scripts
python notion_segment_sync.py setup
```

Paste each page ID when prompted.

## Test It!

```bash
# First push your READMEs to Notion
python notion_segment_sync.py push

# Then try pulling to verify it works
python notion_segment_sync.py pull
```

---

**Tip**: Start with just ONE page (like Permits & Legal) to test the whole flow before doing all 8.