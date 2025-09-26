# Accessing Snapshot from Private Repo

## The Issue
Your repo is private, so `raw.githubusercontent.com` URLs return 404 for unauthenticated users.

## Solution 1: Personal Access Token in URL (Quick but Less Secure)

### Create a Token
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select only `repo` scope (read access)
4. Set expiration (90 days recommended)
5. Copy the token

### Use This URL Format
```
https://YOUR_TOKEN@raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md
```

Replace `YOUR_TOKEN` with your actual token.

**⚠️ Warning**: Anyone with this URL can access the file. Don't share publicly.

## Solution 2: GitHub's Web Interface (Easiest for Team)

Your team members who have access to the private repo can use:
```
https://github.com/betaranch/santas-workshop/blob/main/LATEST_SNAPSHOT.md
```

Then click "Raw" button to get the text.

## Solution 3: Add Team Members to Repo

1. Go to: https://github.com/betaranch/santas-workshop/settings/access
2. Click "Add people"
3. Add your 2 team members
4. They can then access the file directly

## Solution 4: Use GitHub CLI (For Technical Users)

Team members can install GitHub CLI and run:
```bash
gh api repos/betaranch/santas-workshop/contents/LATEST_SNAPSHOT.md --jq '.content' | base64 -d
```

## Solution 5: Create Public Gist (Recommended)

This keeps your code private but makes the snapshot public:

### Setup
1. Create a public Gist at https://gist.github.com
2. Update your workflow to push to the Gist:

```yaml
- name: Update Gist
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Get content
    CONTENT=$(cat LATEST_SNAPSHOT.md | jq -Rs .)

    # Update gist
    curl -X PATCH \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      https://api.github.com/gists/YOUR_GIST_ID \
      -d "{\"files\":{\"snapshot.md\":{\"content\":$CONTENT}}}"
```

Then share the Gist URL with your team.

## For Your Notion Setup

Since you have 3 team members who all use Notion:

### Best Approach:
1. Add them to the GitHub repo (they need GitHub accounts)
2. They bookmark: https://github.com/betaranch/santas-workshop/blob/main/LATEST_SNAPSHOT.md
3. They click "Raw" when they need to copy

### Or Use Notion's GitHub Integration:
1. In Notion, type `/github`
2. Connect to your repo
3. Embed the file directly
4. It will show in Notion for authenticated users

## What About Your Secret?

Your `NOTION_API` secret is working perfectly! It's used by GitHub Actions to:
- Pull tasks from Notion
- Generate the snapshot
- Save it to the repo

The secret is secure and only accessible to the Actions workflow, not to users viewing files.