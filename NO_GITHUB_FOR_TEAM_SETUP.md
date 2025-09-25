# Zero GitHub Knowledge Required - Setup Guide

## What This Does
- Automatically generates a project snapshot every 6 hours
- Creates a simple webpage your team can access
- No GitHub account needed for team members
- Just a link they can bookmark

## Your One-Time Setup (15 minutes)

### Step 1: Enable GitHub Pages (2 minutes)
1. Go to your repo: `https://github.com/YOUR_USERNAME/santas-workshop`
2. Click **Settings** (in the repo, not your profile)
3. Scroll down to **Pages** section (left sidebar)
4. Under **Source**, select:
   - **Deploy from a branch**
   - **Branch:** `main`
   - **Folder:** `/docs`
5. Click **Save**
6. Wait 2-3 minutes for it to activate

Your snapshot will be available at:
```
https://YOUR_USERNAME.github.io/santas-workshop/
```

### Step 2: Update the Workflow File (2 minutes)
Edit `.github/workflows/auto-snapshot.yml` and replace `YOUR_USERNAME` with your actual GitHub username in the last line.

### Step 3: Create docs Folder (1 minute)
```bash
mkdir docs
echo "# Project Snapshot" > docs/snapshot.md
git add docs/
git commit -m "Add docs folder for GitHub Pages"
git push
```

### Step 4: Add Notion API Secret (2 minutes)
1. Go to Settings → Secrets and variables → Actions
2. Add `NOTION_API` with your Notion API key
3. Save

### Step 5: Test the Workflow (3 minutes)
1. Go to **Actions** tab in your repo
2. Click **Auto-Generate Project Snapshot**
3. Click **Run workflow** → **Run workflow**
4. Wait for green checkmark
5. Check `https://YOUR_USERNAME.github.io/santas-workshop/`

### Step 6: Create Notion Embed (5 minutes)

In your Notion page, add this:

#### Option A: Simple Link
```
📸 **Latest Project Snapshot**
[Click here for AI-ready snapshot](https://YOUR_USERNAME.github.io/santas-workshop/)
*Auto-updates every 6 hours*
```

#### Option B: Embed the Page
1. Type `/embed` in Notion
2. Paste: `https://YOUR_USERNAME.github.io/santas-workshop/`
3. The snapshot page appears right in Notion!

#### Option C: Quick Links Card
Create a callout box in Notion:
```
💡 Project Snapshot for AI Analysis

🔄 Auto-updates every 6 hours
📋 [Copy Snapshot](https://YOUR_USERNAME.github.io/santas-workshop/)
⬇️ [Download](https://YOUR_USERNAME.github.io/santas-workshop/snapshot.md)
📖 [View Raw](https://raw.githubusercontent.com/YOUR_USERNAME/santas-workshop/main/docs/snapshot.md)

How to use:
1. Click "Copy Snapshot"
2. Click the "Copy to Clipboard" button
3. Paste into Claude/ChatGPT
4. Ask role-specific questions
```

## What Your Team Sees

### In Notion
They see a link or embedded page - that's it!

### When They Click
A simple webpage with:
- **Copy to Clipboard** button (one click)
- **Download** button (if they prefer)
- Instructions for using with AI
- Current stats (character count, tasks, etc.)

### No GitHub Required
- No accounts needed
- No navigation required
- No technical knowledge required
- Just click and copy!

## How Team Members Use It

### Daily Workflow
1. Open Notion
2. Click the snapshot link (bookmarked)
3. Click "Copy to Clipboard"
4. Paste into Claude/ChatGPT
5. Ask their role-specific questions

That's it! No GitHub, no releases, no navigation.

## Schedule

The snapshot automatically updates:
- **Every 6 hours** (00:00, 06:00, 12:00, 18:00 UTC)
- **On every push** to main branch
- **Manual trigger** available (only you need this)

For Pacific Time:
- 5:00 PM, 11:00 PM, 5:00 AM, 11:00 AM

## If You Want Manual Updates

You can trigger updates two ways:

### From GitHub (for you)
1. Actions → Auto-Generate Project Snapshot
2. Run workflow → Run workflow

### From Command Line (for you)
```bash
gh workflow run auto-snapshot.yml
```

But your team never needs to do this!

## Monitoring

Check if it's working:
- Visit `https://YOUR_USERNAME.github.io/santas-workshop/`
- Look for "Last updated" timestamp
- Should update every 6 hours

## What to Tell Your Team

Send them this message:

```
Hey team!

I've set up an automated project snapshot for AI analysis.

🔗 Bookmark this link: https://YOUR_USERNAME.github.io/santas-workshop/

How to use:
1. Click the link
2. Click "Copy to Clipboard"
3. Paste into Claude or ChatGPT
4. Ask questions based on your area (design, operations, marketing)

It updates automatically every 6 hours with the latest project data.

No login required - just click and use!
```

## Troubleshooting

### "404 Page not found"
- Check GitHub Pages is enabled
- Wait 5-10 minutes after first setup
- Verify docs folder exists

### "Snapshot is outdated"
- Check Actions tab for errors
- Verify NOTION_API secret is set
- Manual trigger to test

### "Copy button doesn't work"
- Try different browser
- Use Download button instead
- Copy from "View Raw" link

## The Magic

Your team gets:
- ✅ Always-current project data
- ✅ One-click access
- ✅ No accounts needed
- ✅ No training required
- ✅ Works on any device

You maintain:
- ✅ Automatic updates
- ✅ Version control
- ✅ No manual work
- ✅ Set and forget

---

*Once this is set up, it just works. Forever. No maintenance needed!*