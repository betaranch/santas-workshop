# GitHub Setup Guide - Step by Step

## Overview
Set up your Notion button to generate project snapshots via GitHub Actions. The snapshot will be committed to your repo and available as a GitHub Release.

## Prerequisites
- GitHub account
- Git installed locally
- Notion workspace (paid plan for webhooks)

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website
1. Go to https://github.com/new
2. Repository name: `santas-workshop`
3. Set to **Private** (for your team only)
4. Click "Create repository"

### Option B: Using Command Line
```bash
# In your project directory
git init
git add .
git commit -m "Initial commit"
```

## Step 2: Push Your Code to GitHub

```bash
# Add your GitHub repository as origin
git remote add origin https://github.com/YOUR_USERNAME/santas-workshop.git

# Push your code
git branch -M main
git push -u origin main
```

## Step 3: Add Notion API Key to GitHub

1. Go to your repository on GitHub
2. Click **Settings** (in the repository, not your profile)
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Name: `NOTION_API`
6. Value: Your Notion API key (from .env file)
7. Click **Add secret**

## Step 4: Create GitHub Personal Access Token

This token allows Notion to trigger your GitHub Action.

1. Go to https://github.com/settings/tokens
2. Click **Generate new token** → **Generate new token (classic)**
3. Note: `Notion Webhook Token`
4. Expiration: 90 days (or No expiration)
5. Select scopes:
   - ✅ `repo` (all of it)
   - ✅ `workflow`
6. Click **Generate token**
7. **COPY THE TOKEN NOW** (you won't see it again!)
   - Save it somewhere safe
   - You'll need it for the Notion button

## Step 5: Test GitHub Action Manually

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Click **Generate Project Snapshot**
4. Click **Run workflow** → **Run workflow**
5. Wait for it to complete (green checkmark)
6. Check:
   - **Releases** page for the download
   - **snapshots/** folder for the files

## Step 6: Configure Notion Button

### Create the Button
1. In your Notion page, type `/button`
2. Name it: `📸 Generate AI Snapshot`
3. Click the button to configure

### Add Webhook Action
1. Click **Add action**
2. Select **Send webhook**
3. Configure:

**URL:**
```
https://api.github.com/repos/YOUR_GITHUB_USERNAME/santas-workshop/dispatches
```
(Replace YOUR_GITHUB_USERNAME with your actual username)

**Headers:**
```json
{
  "Accept": "application/vnd.github.v3+json",
  "Authorization": "token YOUR_PERSONAL_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```
(Replace YOUR_PERSONAL_ACCESS_TOKEN with the token from Step 4)

**Body:**
```json
{
  "event_type": "generate-snapshot"
}
```

4. Click **Done**

## Step 7: Test Your Notion Button

1. Click your new button in Notion
2. You should see a success message
3. Go to GitHub → Actions tab
4. You should see a workflow running
5. Once complete (2-3 minutes):
   - Check **Releases** for download
   - Check **snapshots/latest_snapshot.md** in your repo

## Step 8: How Team Members Access Snapshots

### Option 1: GitHub Releases (Easiest)
1. Go to: `https://github.com/YOUR_USERNAME/santas-workshop/releases`
2. Click on the latest release
3. Download the `.md` file

### Option 2: Direct Link
Bookmark this link:
```
https://github.com/YOUR_USERNAME/santas-workshop/blob/main/snapshots/latest_snapshot.md
```

### Option 3: Raw File
For direct copying:
```
https://raw.githubusercontent.com/YOUR_USERNAME/santas-workshop/main/snapshots/latest_snapshot.md
```

## Step 9: Share with Team

### For Team Members to Use the Button

1. **Add them to GitHub repository**:
   - Settings → Manage access → Add people
   - Give them read access

2. **Share Notion page** with the button

3. **They click button** → Snapshot generates → They download from GitHub

### Team Access Links
Share these with your team:
- **Latest Snapshot**: `https://github.com/YOUR_USERNAME/santas-workshop/blob/main/snapshots/latest_snapshot.md`
- **All Releases**: `https://github.com/YOUR_USERNAME/santas-workshop/releases`
- **Repository**: `https://github.com/YOUR_USERNAME/santas-workshop`

## Verification Checklist

- [ ] Repository created and code pushed
- [ ] NOTION_API secret added to GitHub
- [ ] Personal access token created
- [ ] Manual workflow test successful
- [ ] Notion button configured
- [ ] Button test successful
- [ ] Team members have access

## Troubleshooting

### "Workflow not found"
- Make sure `.github/workflows/generate-snapshot.yml` is pushed to GitHub
- Check the Actions tab is enabled in your repository

### "Bad credentials" in Notion
- Regenerate your personal access token
- Make sure you included `token ` before the token in the Authorization header

### "Not Found" error
- Check your GitHub username is correct in the URL
- Verify repository name is exactly `santas-workshop`

### Snapshot not appearing
- Check GitHub Actions tab for errors
- Verify NOTION_API secret is set correctly
- Look at workflow logs for specific errors

## Success Indicators

When everything is working:
1. **Notion button** shows ✅ when clicked
2. **GitHub Actions** shows green checkmark
3. **New release** appears in Releases tab
4. **snapshots/latest_snapshot.md** updates
5. **Team can download** from releases page

## Daily Use

1. **Any team member** clicks the Notion button
2. **Wait 2-3 minutes** for generation
3. **Go to releases page** or direct link
4. **Download/copy** the markdown
5. **Paste into AI** for analysis

## Security Notes

- Keep your personal access token secret
- Don't commit tokens to the repository
- Rotate tokens periodically
- Only give team members the access they need

---

*Once set up, this will work reliably for your team with just one click!*