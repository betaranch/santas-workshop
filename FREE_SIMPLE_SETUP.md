# FREE & Simple Setup - No GitHub Upgrade Needed!

## The Simplest Solution (5 minutes)

Your snapshot will live at a raw GitHub URL that anyone can access. No Pages, no upgrade, totally free!

## Quick Setup

### 1. Push the Workflow (2 minutes)
```bash
git add .
git commit -m "Add simple auto-snapshot"
git push
```

### 2. Test It (2 minutes)
1. Go to: https://github.com/betaranch/santas-workshop/actions
2. Click **"Simple Auto Snapshot"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Wait for green checkmark

### 3. Your Team's Link (1 minute)

After the workflow runs, your snapshot will be at:
```
https://raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md
```

## For Your Team in Notion

### Option A: Direct Link with Instructions
Add this to Notion:

```markdown
## 📸 AI Project Snapshot

**[Click here to view snapshot](https://raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md)**

*Auto-updates every 6 hours*

**How to use:**
1. Click the link above
2. Select all text (Ctrl+A or Cmd+A)
3. Copy (Ctrl+C or Cmd+C)
4. Paste into Claude or ChatGPT
5. Ask questions based on your role
```

### Option B: Embed in Notion (Better UX)
Create a Code block in Notion:
1. Type `/code`
2. Click "Sync from GitHub URL"
3. Paste: `https://raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md`
4. Toggle on "Auto-sync"

Now the snapshot appears directly in Notion!

### Option C: Use a Simple Viewer

Add this link to Notion:
```
https://htmlpreview.github.io/?https://github.com/betaranch/santas-workshop/blob/main/LATEST_SNAPSHOT.md
```

Or use GitHub's interface:
```
https://github.com/betaranch/santas-workshop/blob/main/LATEST_SNAPSHOT.md
```

## Alternative: Free Web Hosting with Vercel (10 minutes)

If you want a nicer interface with a copy button:

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Create a Simple Viewer
```bash
mkdir snapshot-viewer
cd snapshot-viewer
```

Create `index.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Project Snapshot</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        button {
            background: #0070f3;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #0051cc; }
        #content {
            display: none;
            white-space: pre-wrap;
            background: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .message {
            padding: 10px;
            background: #d4edda;
            color: #155724;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>🎅 Santa's Workshop - Project Snapshot</h1>
    <p>Auto-updates every 6 hours</p>

    <button onclick="copySnapshot()">📋 Copy to Clipboard</button>
    <a href="https://raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md" target="_blank">
        <button>📄 View Raw</button>
    </a>

    <div id="message"></div>
    <pre id="content"></pre>

    <script>
        // Fetch snapshot from GitHub
        fetch('https://raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md')
            .then(r => r.text())
            .then(text => {
                document.getElementById('content').textContent = text;
            })
            .catch(err => {
                document.getElementById('message').textContent = 'Error loading snapshot';
            });

        function copySnapshot() {
            const content = document.getElementById('content').textContent;
            navigator.clipboard.writeText(content).then(() => {
                const msg = document.getElementById('message');
                msg.textContent = '✅ Copied! Now paste into any AI assistant.';
                msg.className = 'message';
                setTimeout(() => msg.textContent = '', 5000);
            });
        }
    </script>
</body>
</html>
```

### 3. Deploy to Vercel (Free)
```bash
vercel
# Follow prompts, accept defaults
# Get your URL like: https://snapshot-viewer.vercel.app
```

### 4. Share Vercel Link
Give your team the Vercel URL - it has a nice copy button!

## Comparison of Free Options

| Method | Setup Time | User Experience | URL Type |
|--------|------------|-----------------|----------|
| Raw GitHub URL | 2 min | Copy manually | Long but works |
| GitHub Blob View | 2 min | Nicer view, copy button | GitHub interface |
| Notion Code Sync | 3 min | Shows IN Notion | Embedded |
| Vercel Viewer | 10 min | Best UX, copy button | Custom domain |

## Recommended: Start Simple

1. Use the **raw GitHub URL** first
2. It works immediately
3. Upgrade to Vercel later if team wants better UX

Your team's link (after you run the workflow):
```
https://raw.githubusercontent.com/betaranch/santas-workshop/main/LATEST_SNAPSHOT.md
```

## That's It!

No payment needed, totally free, works forever!

Just:
1. `git push`
2. Run the workflow
3. Share the link

Your team gets updated snapshots every 6 hours without any GitHub knowledge!