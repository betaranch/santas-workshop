#!/usr/bin/env python3
"""
Pre-work sync script - Run this before starting your work session
Pulls latest content from Notion and prepares your workspace
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Run a command and show status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"[ERROR] Command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("""
    ============================================================
                    ELF SPEAKEASY PROJECT
                      Pre-Work Sync Script
    ============================================================
    """)

    print(f"\nStarting sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check if user wants full sync or quick sync
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_mode = True
        print("[QUICK MODE] Skipping README pull, only syncing tasks\n")
    else:
        quick_mode = False
        print("[FULL MODE] Syncing everything from Notion\n")

    success = True

    # Step 1: Pull latest database content (Tasks, Notes, etc.)
    if run_command(
        "python scripts/notion.py sync",
        "STEP 1: Pulling latest Tasks, Notes, and Projects from Notion"
    ):
        print("[OK] Database sync complete")
    else:
        print("[WARN] Database sync failed - continuing anyway")
        success = False

    time.sleep(1)

    # Step 2: Generate task files for each project
    if run_command(
        "python scripts/generate_tasks_md.py",
        "STEP 2: Generating tasks.md files for each project"
    ):
        print("[OK] Task files generated")
    else:
        print("[WARN] Task generation failed - continuing anyway")
        success = False

    time.sleep(1)

    # Step 3: Pull latest README content from Notion (unless quick mode)
    if not quick_mode:
        print("\n" + "="*60)
        print("STEP 3: Pulling README content from Notion pages")
        print("="*60)
        print("\n[INFO] This will check for conflicts and create backups")
        print("[INFO] You'll be prompted if there are recent local changes\n")

        response = input("Pull all README files from Notion? (y/n/skip): ").lower()

        if response == 'y':
            if run_command(
                "python scripts/pull_from_notion.py",
                "Pulling README content from Notion"
            ):
                print("[OK] README files synced from Notion")
            else:
                print("[WARN] Some README files may not have synced")
                success = False
        else:
            print("[SKIP] Skipping README pull")

    # Step 4: Show current status
    print("\n" + "="*60)
    print("WORKSPACE STATUS")
    print("="*60)

    # Count tasks
    try:
        from generate_tasks_md import TaskGenerator
        generator = TaskGenerator()
        high_priority = sum(1 for t in generator.tasks
                          if generator.extract_property_text(
                              t.get("properties", {}), "Priority"
                          ) and "High" in generator.extract_property_text(
                              t.get("properties", {}), "Priority"
                          ))

        print(f"\nTasks Summary:")
        print(f"  Total Tasks: {len(generator.tasks)}")
        print(f"  High Priority: {high_priority}")
    except:
        print("\n[INFO] Could not load task summary")

    # Show recent backups
    backup_dir = Path(__file__).parent.parent / "backups"
    if backup_dir.exists():
        recent_backups = []
        for project_dir in backup_dir.iterdir():
            if project_dir.is_dir():
                backups = list(project_dir.glob("README_*.md"))
                if backups:
                    latest = max(backups, key=lambda x: x.stat().st_mtime)
                    recent_backups.append((project_dir.name, latest))

        if recent_backups:
            print(f"\nRecent Backups:")
            for project, backup in recent_backups[:5]:
                mod_time = datetime.fromtimestamp(backup.stat().st_mtime)
                print(f"  {project}: {mod_time.strftime('%Y-%m-%d %H:%M')}")

    # Final status
    print("\n" + "="*60)
    if success:
        print("[OK] SYNC COMPLETE - Ready to work!")
    else:
        print("[WARN] SYNC COMPLETED WITH WARNINGS - Check output above")
    print("="*60)

    print("\nUseful commands for your work session:")
    print("  python scripts/quick_sync.py          # Sync individual project to Notion")
    print("  python scripts/sync_readme_to_notion.py  # Push all READMEs to Notion")
    print("  python scripts/notion.py analyze      # Search tasks and notes")

    print("\nHappy coding!\n")


if __name__ == "__main__":
    main()