#!/usr/bin/env python3
"""
End-of-work sync script - Run this after your work session
Pushes your changes to Notion
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

def check_git_status():
    """Check if there are uncommitted changes"""
    try:
        result = subprocess.run(
            "git status --porcelain",
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.stdout.strip():
            return True
        return False
    except:
        return None

def main():
    print("""
    ============================================================
                    ELF SPEAKEASY PROJECT
                     End-of-Work Sync Script
    ============================================================
    """)

    print(f"\nEnding work session at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    success = True

    # Step 1: Check what's changed
    print("\n" + "="*60)
    print("STEP 1: Checking for local changes")
    print("="*60)

    # List modified README files
    docs_dir = Path(__file__).parent.parent / "Docs"
    modified_readmes = []

    for readme in docs_dir.glob("*/README.md"):
        # Check if modified in last 8 hours
        mod_time = datetime.fromtimestamp(readme.stat().st_mtime)
        if (datetime.now() - mod_time).total_seconds() < 28800:  # 8 hours
            project = readme.parent.name
            modified_readmes.append(project)

    if modified_readmes:
        print(f"\nModified README files (last 8 hours):")
        for project in modified_readmes:
            print(f"  - {project}")
    else:
        print("\nNo README files modified recently")

    # Step 2: Push README changes to Notion
    if modified_readmes:
        print("\n" + "="*60)
        print("STEP 2: Push README changes to Notion")
        print("="*60)

        response = input("\nPush all modified READMEs to Notion? (y/n/select): ").lower()

        if response == 'y':
            # Push all READMEs
            if run_command(
                "python scripts/sync_readme_to_notion.py",
                "Pushing all README files to Notion"
            ):
                print("[OK] All READMEs pushed to Notion")
            else:
                print("[ERROR] Failed to push some READMEs")
                success = False

        elif response == 'select':
            # Let user select which ones to push
            print("\nSelect projects to sync:")
            for i, project in enumerate(modified_readmes, 1):
                print(f"{i}. {project}")

            selections = input("\nEnter numbers separated by comma (e.g., 1,3,4): ").strip()

            if selections:
                selected_indices = [int(x.strip()) - 1 for x in selections.split(',')]
                for idx in selected_indices:
                    if 0 <= idx < len(modified_readmes):
                        project = modified_readmes[idx]
                        run_command(
                            f"python scripts/sync_readme_to_notion.py {project}",
                            f"Pushing {project} to Notion"
                        )
                        time.sleep(1)
        else:
            print("[SKIP] Not pushing README changes")
    else:
        print("\n[INFO] No README changes to push")

    # Step 3: Git status check (if in a git repo)
    git_changes = check_git_status()
    if git_changes is not None:
        print("\n" + "="*60)
        print("STEP 3: Git Status")
        print("="*60)

        if git_changes:
            print("\n[WARN] You have uncommitted changes")
            print("Consider committing your work:")
            print("  git add -A")
            print("  git commit -m 'End of work session'")
        else:
            print("\n[OK] No uncommitted changes")

    # Step 4: Summary
    print("\n" + "="*60)
    print("SESSION SUMMARY")
    print("="*60)

    # Show work duration if start_work was run today
    cache_dir = Path(__file__).parent.parent / "cache"
    last_sync_file = cache_dir / "last_sync.txt"

    if last_sync_file.exists():
        with open(last_sync_file, 'r') as f:
            last_sync = datetime.fromisoformat(f.read().strip())

        duration = datetime.now() - last_sync
        hours = duration.total_seconds() / 3600
        print(f"\nWork session duration: {hours:.1f} hours")

    # Final status
    print("\n" + "="*60)
    if success:
        print("[OK] END-OF-WORK SYNC COMPLETE")
    else:
        print("[WARN] SYNC COMPLETED WITH WARNINGS")
    print("="*60)

    print("\nYour changes have been pushed to Notion.")
    print("Team members will see your updates immediately.")
    print("\nGreat work today!\n")

    # Save sync time
    last_sync_file.parent.mkdir(exist_ok=True)
    with open(last_sync_file, 'w') as f:
        f.write(datetime.now().isoformat())


if __name__ == "__main__":
    main()