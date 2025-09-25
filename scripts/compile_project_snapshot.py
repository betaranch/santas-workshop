#!/usr/bin/env python3
"""
Compile Project Snapshot - Creates a comprehensive markdown file of entire project state
Perfect for AI analysis, team reviews, and strategic planning
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / "Docs"
CACHE_DIR = BASE_DIR / "cache"
OUTPUT_DIR = BASE_DIR / "snapshots"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Load environment
load_dotenv(BASE_DIR / ".env")

class ProjectSnapshot:
    """Compiles entire project state into a single markdown file"""

    def __init__(self):
        self.api_key = os.getenv("NOTION_API")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        } if self.api_key else None

        self.content_sections = []
        self.task_data = {}
        self.project_summaries = {}

    def compile_snapshot(self, pull_latest=True) -> str:
        """Main method to compile everything"""
        print("[COMPILE] Compiling Santa's Workshop Project Snapshot...")

        if pull_latest and self.api_key:
            print("[PULL] Pulling latest data from Notion...")
            self._pull_latest_data()

        # 1. Executive Summary
        print("[1/7] Creating executive summary...")
        self._add_executive_summary()

        # 2. Project Overview
        print("[2/7] Adding project overview...")
        self._add_project_overview()

        # 3. Current Status Dashboard
        print("[3/7] Building status dashboard...")
        self._add_status_dashboard()

        # 4. All Project Sections with Tasks
        print("[4/7] Compiling all project sections...")
        self._compile_all_projects()

        # 5. Analysis Prompts for AI
        print("[5/7] Adding analysis prompts...")
        self._add_analysis_prompts()

        # 6. Team Context
        print("[6/7] Adding team context...")
        self._add_team_context()

        # 7. Metadata
        self._add_metadata()

        # Combine everything
        snapshot = "\n\n".join(self.content_sections)

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"project_snapshot_{timestamp}.md"
        filepath = OUTPUT_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(snapshot)

        print(f"\n[SUCCESS] Snapshot saved to: {filepath}")
        print(f"[INFO] File size: {len(snapshot):,} characters")
        print(f"[INFO] Sections: {len(self.content_sections)}")

        return str(filepath)

    def _pull_latest_data(self):
        """Pull latest data from Notion if API key available"""
        try:
            # Use existing scripts to pull latest
            import subprocess

            # Pull tasks
            result = subprocess.run(
                ["python", "scripts/notion_task_manager.py", "read"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )

            if result.returncode == 0:
                print("  [OK] Tasks updated")

            # Generate task files
            result = subprocess.run(
                ["python", "scripts/generate_tasks_md.py"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )

            if result.returncode == 0:
                print("  [OK] Task files regenerated")

        except Exception as e:
            print(f"  [WARN] Could not pull latest: {e}")

    def _add_executive_summary(self):
        """Add executive summary section"""
        summary = """# 🎅 Santa's Workshop - Project Snapshot

## Executive Summary

**Project**: Elf Speakeasy Pop-Up Experience
**Location**: Bend, Oregon
**Timeline**: November 1, 2025 - January 1, 2026
**Status**: 7 weeks to launch

### Vision
Transform a venue into an immersive North Pole portal where adults escape into a world of craft cocktails, storytelling, and holiday magic. This isn't just a pop-up - it's a fully realized alternate reality that happens to serve exceptional drinks.

### Core Concept
A theatrical speakeasy experience that layers:
- **Narrative immersion** through character interactions and environmental storytelling
- **Craft cocktail program** with themed drinks and food pairings
- **Interactive elements** that reward curiosity and repeat visits
- **Photographic moments** designed for organic social sharing

### Business Model
- **Investment**: $53,500 fixed costs
- **Revenue Target**: $105,000
- **Profit Target**: $38,000
- **Break-even**: 40% capacity
- **Audiences**: Evening adults (primary), Corporate events (secondary), Weekend families (tertiary)

### Critical Success Factors
1. All permits approved by October 31
2. 6-8 trained staff recruited and ready
3. Venue secured and transformed by October 25
4. Marketing campaign live by October 1
5. Opening night November 1"""

        self.content_sections.append(summary)

    def _add_project_overview(self):
        """Add detailed project overview from core.md"""
        core_file = DOCS_DIR / "core.md"
        if core_file.exists():
            with open(core_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract first 1500 chars as overview
                if len(content) > 1500:
                    content = content[:1500] + "\n\n*[Core document continues...]*"

                self.content_sections.append("## Project Foundation\n\n" + content)

    def _add_status_dashboard(self):
        """Add current status dashboard"""
        # Load task indexes
        dashboard = "## 📊 Current Status Dashboard\n"

        # Load summary
        summary_file = CACHE_DIR / "indexes" / "summary.json"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                summary = json.load(f)

                dashboard += f"""
### Task Overview
- **Total Tasks**: {summary.get('total_tasks', 0)}
- **Not Started**: {summary.get('by_status', {}).get('Not started', 0)}
- **In Progress**: {summary.get('by_status', {}).get('In Progress', 0)}
- **Completed**: {summary.get('by_status', {}).get('Done', 0)}
- **High Priority**: {summary.get('by_priority', {}).get('High Priority', 0)}
"""

        # Load upcoming deadlines
        deadlines_file = CACHE_DIR / "indexes" / "upcoming_deadlines.json"
        if deadlines_file.exists():
            with open(deadlines_file, 'r') as f:
                deadlines = json.load(f)[:5]  # First 5

                if deadlines:
                    dashboard += "\n### 🔥 Upcoming Deadlines\n"
                    for task in deadlines:
                        dashboard += f"- **{task['due']}**: {task['name']}\n"

        # Project distribution
        dashboard += """
### Project Areas
1. **Permits & Legal** - 🔴 CRITICAL PATH
2. **Space & Operations** - Venue and layout planning
3. **Theme & Design** - Creative and narrative development
4. **Marketing & Sales** - Customer acquisition
5. **Team** - 🔴 CRITICAL - Staffing and training
6. **Budget & Finance** - Financial tracking
7. **Vendors & Suppliers** - Procurement
8. **Evaluation & Scaling** - Growth planning
"""

        self.content_sections.append(dashboard)

    def _compile_all_projects(self):
        """Compile all project READMEs and tasks"""
        project_folders = [
            ("01_Permits_Legal", "Permits & Legal", "🔴"),
            ("02_Space_Ops", "Space & Operations", "🏠"),
            ("03_Theme_Design_Story", "Theme, Design & Story", "🎨"),
            ("04_Marketing_Sales", "Marketing & Sales", "📢"),
            ("05_Team", "Team", "👥"),
            ("06_Budget_Finance", "Budget & Finance", "💰"),
            ("07_Vendors_Suppliers", "Vendors & Suppliers", "📦"),
            ("08_Evaluation_Scaling", "Evaluation & Scaling", "📈"),
        ]

        for folder, title, icon in project_folders:
            project_dir = DOCS_DIR / folder
            if not project_dir.exists():
                continue

            section = f"## {icon} {title}\n"

            # Add README content
            readme_file = project_dir / "README.md"
            if readme_file.exists():
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Get first 2000 chars or until first major section
                    lines = content.split('\n')
                    excerpt = []
                    char_count = 0

                    for line in lines:
                        if char_count > 2000 and line.startswith('##'):
                            break
                        excerpt.append(line)
                        char_count += len(line)

                    section += '\n'.join(excerpt)

            # Add tasks
            tasks_file = project_dir / "tasks.md"
            if tasks_file.exists():
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    task_content = f.read()
                    # Extract just the task list, not the header
                    lines = task_content.split('\n')
                    task_lines = []
                    in_tasks = False

                    for line in lines:
                        if line.startswith('### '):
                            in_tasks = True
                        if in_tasks:
                            task_lines.append(line)

                    if task_lines:
                        section += "\n\n### Current Tasks\n" + '\n'.join(task_lines)

            section += "\n\n---"
            self.content_sections.append(section)

    def _add_analysis_prompts(self):
        """Add analysis prompts for AI assistance"""
        prompts = """## 🤖 AI Analysis Guide

### How to Use This Document with AI
Copy this entire document into Claude, ChatGPT, or your preferred AI assistant, then explore based on your role and current needs.

### Analysis Perspectives by Role

#### Design & Creative Perspective
- "What themed elements would enhance immersion while staying within our $15K startup budget?"
- "How can we create Instagram-worthy moments that feel authentic to the narrative?"
- "What sensory design elements (lighting, sound, scent) are we missing?"
- "How can we make the space transformation reversible for venue flexibility?"

#### Operations & Logistics Perspective
- "What operational bottlenecks might occur with 75 guests?"
- "How can we optimize staff scheduling across different event types?"
- "What backup plans do we need for weather, supply chain, or venue issues?"
- "Where are the critical dependencies that could delay our Nov 1 opening?"

#### Marketing & Revenue Perspective
- "What partnership opportunities could drive pre-sales?"
- "How can we optimize pricing across our three audience segments?"
- "What upsell opportunities fit naturally with the experience?"
- "How do we build repeatability to drive return visits?"

#### Team & Service Perspective
- "What training will staff need to maintain character and service quality?"
- "How can we build team culture before opening?"
- "What incentive structures would retain quality staff through the season?"
- "How do we maintain consistency across different shift teams?"

### Universal Analysis Questions

#### Risk Identification
- "What are the top 3-5 risks that could prevent opening on November 1?"
- "What blind spots exist in our current planning?"
- "What dependencies could cascade if delayed?"
- "What external factors (weather, competition, economy) need contingency plans?"

#### Opportunity Discovery
- "What revenue streams are we not considering?"
- "What local partnerships would be mutually beneficial?"
- "How can we extend value beyond the 2-month run?"
- "What data should we capture for future ventures?"

#### Critical Path Analysis
- "What tasks must be completed in the next 7 days?"
- "What decisions are blocking other progress?"
- "Where should we focus resources this week?"
- "What can be delegated or deferred without impacting launch?"

### Custom Prompts for Your Situation
Based on the current project status and your specific role, you might ask:
- "Given our timeline, what should be the priority order for [your specific tasks]?"
- "How would you approach [specific challenge] given our constraints?"
- "What successful examples could we learn from for [specific element]?"
- "Generate a checklist for [specific milestone or task]"
"""
        self.content_sections.append(prompts)

    def _add_team_context(self):
        """Add team context section"""
        context = """## 👥 Team Context & Collaboration

### Project Team Structure
- **Team Size**: 3 core team members + 6-8 seasonal staff
- **Collaboration Tools**: Notion (primary), Google Drive (files), Figma (design)
- **Work Style**: Distributed team, asynchronous collaboration

### Using This Snapshot
1. **Generate regularly** - Weekly recommended, before major decisions
2. **Share with AI** - Each team member can analyze from their perspective
3. **Compare insights** - Different AIs or prompts may surface different opportunities
4. **Document findings** - Add insights back to Notion for team visibility

### Version Control
This snapshot represents a point-in-time view. For most current information:
- Check Notion for real-time updates
- Run a new snapshot before major decisions
- Consider the generation timestamp when reviewing

### Collaboration Tips
- Use consistent AI assistants for continuity
- Share particularly valuable AI insights with team
- Create role-specific prompt templates
- Track which recommendations get implemented
"""
        self.content_sections.append(context)

    def _add_metadata(self):
        """Add metadata section"""
        metadata = f"""## 📋 Document Metadata

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Purpose**: AI Analysis & Team Alignment
**Contents**: Executive Summary, 8 Project Areas, Tasks, Risks, Opportunities
**Usage**: Copy this entire document into any AI assistant for strategic analysis

### How to Use This Document
1. Copy the entire content
2. Paste into Claude, ChatGPT, or other AI assistant
3. Ask strategic questions about blind spots, opportunities, or specific areas
4. Use for team meetings to ensure everyone has the same context
5. Generate weekly to track progress

### Suggested AI Prompts
- "Analyze this project for critical dependencies and bottlenecks"
- "Identify the top 5 tasks that would have the highest impact if completed this week"
- "What creative marketing strategies would work for this concept?"
- "How could we reduce costs by 20% without impacting quality?"
- "What are similar successful projects we could learn from?"

---
*End of Project Snapshot*"""

        self.content_sections.append(metadata)

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Compile project snapshot")
    parser.add_argument('--no-pull', action='store_true',
                       help='Skip pulling latest from Notion')
    parser.add_argument('--output', help='Output filename')

    args = parser.parse_args()

    snapshot = ProjectSnapshot()
    filepath = snapshot.compile_snapshot(pull_latest=not args.no_pull)

    print(f"\n[SUCCESS] Your project snapshot is ready!")
    print(f"[LOCATION] {filepath}")
    print(f"\n[NEXT STEPS]")
    print("1. Open the file and copy all content")
    print("2. Paste into any AI assistant")
    print("3. Ask strategic questions about your project")

if __name__ == "__main__":
    main()