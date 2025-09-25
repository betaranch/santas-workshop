# Notion Button Quick Start - 5 Minutes to Working Button

## What You Get
A button in Notion that generates a comprehensive markdown file of your entire project - perfect for AI analysis and team reviews.

## Immediate Local Setup (5 minutes)

### 1. Install Flask (One Time)
```bash
pip install flask flask-cors
```

### 2. Start the Web Service
```bash
python scripts/web_service.py
```

You'll see:
```
Starting server on http://0.0.0.0:5000
```

### 3. Find Your Computer's IP Address
```bash
# Windows
ipconfig
# Look for IPv4 Address (like 192.168.1.100)

# Mac/Linux
ifconfig
# Look for inet address
```

### 4. Test in Browser
Open: `http://YOUR_IP:5000` (e.g., `http://192.168.1.100:5000`)

You should see a web interface where you can:
- Click "Generate New Snapshot"
- Download previous snapshots
- See the generation status

### 5. Create Notion Button

In your Notion page:

1. Type `/button` to create a button
2. Name it: "📸 Generate AI Snapshot"
3. Click the button to edit
4. Click "Add action" → "Send webhook"
5. Configure:
   - **URL**: `http://YOUR_IP:5000/generate-snapshot`
   - **Headers**: Leave empty
   - **Body**: `{}`

### 6. Test Your Button!
Click the button in Notion. A file will download with your complete project snapshot.

## Using the Snapshot with AI

1. **Open the downloaded markdown file**
2. **Copy all content** (Ctrl+A, Ctrl+C)
3. **Paste into any AI** (Claude, ChatGPT, etc.)
4. **Ask strategic questions**:
   - "What are the biggest risks in this project?"
   - "What opportunities are we missing?"
   - "What should we prioritize this week?"
   - "Find any blind spots or contradictions"

## For Team Use

### Option A: Same Network
If team members are on the same network (office WiFi):
- They can use the same button
- URL stays the same: `http://YOUR_IP:5000/generate-snapshot`

### Option B: Different Locations
For remote team members, choose one:

1. **GitHub Actions** (Recommended for teams)
   - Push repo to GitHub
   - Follow setup in `Docs/Technical/NOTION_BUTTON_INTEGRATION.md`
   - Button works for everyone, anywhere

2. **Vercel/Netlify** (Simplest cloud option)
   - Deploy with one command
   - Get public URL
   - Update button URL

## Features Available

Your local web service (`http://YOUR_IP:5000`) provides:

- **Web Interface**: `/` - Visual interface with buttons
- **Generate Snapshot**: `/generate-snapshot` - For Notion button
- **List Snapshots**: `/list-snapshots` - See all generated files
- **Download Specific**: `/download/filename.md` - Get any snapshot
- **Health Check**: `/health` - Verify service is running

## Troubleshooting

### "Connection refused" in Notion
- Check web service is running (`python scripts/web_service.py`)
- Verify IP address is correct
- Check firewall isn't blocking port 5000

### "No snapshot generated"
- Check console output of web service
- Try running manually: `python scripts/compile_project_snapshot.py`
- Check `snapshots/` folder exists

### Button shows success but no download
- Try the JSON endpoint instead: `/generate-snapshot-json`
- Check browser downloads folder
- Try different browser

## Advanced: Auto-Start on Windows

Create `start_snapshot_service.bat`:
```batch
@echo off
cd /d D:\betaranch\santas-workshop
python scripts\web_service.py
pause
```

Double-click to start the service anytime!

## Next Steps

Once you're comfortable with local setup:
1. **Test with your team** - Share the button
2. **Gather feedback** - What additional data would help?
3. **Consider cloud deployment** - For always-available access
4. **Customize the snapshot** - Add project-specific sections

## The Power of This Approach

With one button click, you get:
- **Complete project context** in one file
- **All tasks and priorities** organized by area
- **Risk analysis** and blind spots
- **Perfect AI prompt** for strategic analysis
- **Team alignment** - everyone sees same data

No more copy-pasting from multiple Notion pages!

---

*Start local now, upgrade to cloud later. The important thing is to start using it!*