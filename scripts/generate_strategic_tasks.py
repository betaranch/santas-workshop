#!/usr/bin/env python3
"""
Generate strategic task markdown files for each project
Creates consolidated, higher-level tasks without priorities
"""

import os
from pathlib import Path
from datetime import datetime

# Strategic consolidated tasks by project
STRATEGIC_TASKS = {
    "01_Permits_Legal": [
        "Complete all permits and licenses package (TCO, liquor, food, business)",
        "Establish liability protection and insurance coverage",
        "Ensure ADA and safety compliance for venue",
        "Legal review of customer agreements and waivers"
    ],

    "02_Space_Ops": [
        "Design and finalize venue layout for 75-person capacity",
        "Establish daily operational procedures and checklists",
        "Set up complete inventory and supply chain system",
        "Create emergency and safety protocols",
        "Develop service standards and flow management",
        "Install and test all equipment and systems"
    ],

    "03_Theme_Design_Story": [
        "Create complete brand identity and visual system",
        "Develop immersive story world and character bible",
        "Design signature experiences and surprise moments",
        "Build atmosphere package (lighting, sound, scent)",
        "Create photo-worthy installations and backdrops",
        "Design and produce all collateral materials"
    ],

    "04_Marketing_Sales": [
        "Launch pre-sales campaign (target 70% capacity)",
        "Build social media presence and content strategy",
        "Develop corporate and group sales packages",
        "Create PR and influencer outreach program",
        "Set up reservation and ticketing systems",
        "Design merchandise and upsell programs"
    ],

    "05_Team": [
        "Recruit and hire complete staff (8-10 people)",
        "Develop training program and character guides",
        "Create staff handbook and operational policies",
        "Design performance and compensation structure",
        "Build team culture and pre-opening preparation"
    ],

    "06_Budget_Finance": [
        "Finalize complete budget and financial model",
        "Set up accounting and financial tracking systems",
        "Establish cash management and banking",
        "Create financial reporting and monitoring process",
        "Develop pricing strategy and revenue optimization"
    ],

    "07_Vendors_Suppliers": [
        "Source and contract all F&B suppliers",
        "Procure furniture, fixtures, and equipment",
        "Establish vendor relationships and payment terms",
        "Source all themed decor and props",
        "Set up utilities and service contracts"
    ],

    "08_Evaluation_Scaling": [
        "Design success metrics and tracking systems",
        "Create guest feedback and improvement process",
        "Develop franchise/expansion playbook",
        "Build investor reporting framework",
        "Plan year 2 growth strategy"
    ]
}

# Project name mapping
PROJECT_NAMES = {
    "01_Permits_Legal": "Permits & Legal",
    "02_Space_Ops": "Space & Operations",
    "03_Theme_Design_Story": "Theme, Design & Story",
    "04_Marketing_Sales": "Marketing & Sales",
    "05_Team": "Team",
    "06_Budget_Finance": "Budget & Finance",
    "07_Vendors_Suppliers": "Vendors & Suppliers",
    "08_Evaluation_Scaling": "Evaluation & Scaling"
}

def generate_task_markdown(project_folder, tasks):
    """Generate markdown content for a project's tasks"""
    project_name = PROJECT_NAMES.get(project_folder, project_folder)

    md = f"# Tasks for {project_name}\n\n"
    md += f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
    md += f"**Total Tasks: {len(tasks)}**\n\n"
    md += "## Strategic Deliverables\n\n"

    for task in tasks:
        md += f"### ⬜ {task}\n\n"
        md += "---\n\n"

    md += "\n## Notes\n\n"
    md += "These are strategic-level deliverables. Each can be broken down into specific actions as needed.\n"
    md += "Priorities will be set during team planning sessions.\n"

    return md

def main():
    """Generate all task markdown files"""
    base_dir = Path(__file__).parent.parent
    docs_dir = base_dir / "Docs"

    print("[INFO] Generating strategic task files...\n")

    for project_folder, tasks in STRATEGIC_TASKS.items():
        # Create project directory if needed
        project_dir = docs_dir / project_folder
        project_dir.mkdir(exist_ok=True)

        # Generate markdown
        markdown = generate_task_markdown(project_folder, tasks)

        # Write file
        tasks_file = project_dir / "tasks.md"
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        project_name = PROJECT_NAMES.get(project_folder, project_folder)
        print(f"[OK] Generated {project_folder}/tasks.md - {len(tasks)} strategic tasks")

    print(f"\n[SUMMARY]")
    total_tasks = sum(len(tasks) for tasks in STRATEGIC_TASKS.values())
    print(f"  Total strategic tasks: {total_tasks}")
    print(f"  Projects covered: {len(STRATEGIC_TASKS)}")
    print(f"\nThese consolidated tasks replace the previous granular task list.")
    print("Each strategic task encompasses multiple tactical actions.")

if __name__ == "__main__":
    main()