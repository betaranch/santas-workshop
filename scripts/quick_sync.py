#!/usr/bin/env python3
"""
Quick sync script - syncs one project at a time with status updates
"""

import os
import sys
import json
from pathlib import Path
from sync_readme_to_notion import ReadmeToNotionSync

def main():
    sync = ReadmeToNotionSync()

    # Get list of projects
    projects = list(sync.mappings.keys())

    if len(sys.argv) > 1:
        # Sync specific project
        project = sys.argv[1]
        if project in projects:
            print(f"Syncing {project}...")
            sync.sync_project(project)
        else:
            print(f"Project {project} not found. Available projects:")
            for p in projects:
                print(f"  - {p}")
    else:
        # Show menu
        print("\nAvailable projects to sync:")
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project}")
        print(f"{len(projects)+1}. Sync ALL (one by one)")
        print("0. Exit")

        choice = input("\nEnter number: ").strip()

        if choice == "0":
            return
        elif choice == str(len(projects)+1):
            # Sync all one by one
            for project in projects:
                print(f"\nSyncing {project}...")
                sync.sync_project(project)
                print("Done. Moving to next...")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(projects):
                    project = projects[idx]
                    print(f"\nSyncing {project}...")
                    sync.sync_project(project)
                else:
                    print("Invalid choice")
            except:
                print("Invalid input")

if __name__ == "__main__":
    main()