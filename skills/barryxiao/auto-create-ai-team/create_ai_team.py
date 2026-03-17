#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Create AI Team - Simple Local File Creator
Creates AI team directory structures for projects.
No network calls, no external dependencies, completely offline.
"""

import os
import sys
import argparse
from pathlib import Path

def create_ai_team_structure(project_path, team_type='single', project_type='generic'):
    """Create AI team directory structure in the specified project path."""
    
    # Ensure project path exists
    if not os.path.exists(project_path):
        print(f"Error: Project path does not exist: {project_path}")
        sys.exit(1)
    
    # Create ai-team directory
    ai_team_dir = os.path.join(project_path, 'ai-team')
    os.makedirs(ai_team_dir, exist_ok=True)
    
    # Create internal team
    internal_dir = os.path.join(ai_team_dir, 'internal-team', 'team-info')
    os.makedirs(internal_dir, exist_ok=True)
    
    # Determine team members based on project type
    if project_type == 'web_app':
        members = ['Product Manager', 'Frontend Developer', 'Backend Developer', 'QA Engineer', 'UX/UI Designer']
    elif project_type == 'ecommerce':
        members = ['Technical Architect', 'Full-stack Developer', 'UX Designer', 'Payment Integration Specialist', 'QA Engineer']
    elif project_type == 'mobile_app':
        members = ['Mobile Developer', 'Backend Engineer', 'UI/UX Designer', 'QA Engineer', 'DevOps Engineer']
    else:
        members = ['AI Assistant', 'Data Processor', 'Content Generator', 'Quality Checker', 'Project Coordinator']
    
    # Create internal team config
    with open(os.path.join(internal_dir, 'AI_TEAM_CONFIG.md'), 'w', encoding='utf-8') as f:
        f.write(f"""# Internal AI Team Configuration
Project Type: {project_type}
Team Type: Internal AI Team
Creation Date: {os.popen('date').read().strip()}
Team Members: {', '.join(members)}
""")
    
    # Create internet team if dual mode
    if team_type == 'dual':
        internet_dir = os.path.join(ai_team_dir, 'internet-team', 'team-info')
        os.makedirs(internet_dir, exist_ok=True)
        
        internet_members = ['Product Manager', 'Marketing Specialist', 'Social Media Operator', 'Data Analyst', 'Business Development Manager']
        
        with open(os.path.join(internet_dir, 'INTERNET_TEAM_CONFIG.md'), 'w', encoding='utf-8') as f:
            f.write(f"""# Internet Team Configuration  
Project Type: {project_type}
Team Type: Internet Team
Creation Date: {os.popen('date').read().strip()}
Team Members: {', '.join(internet_members)}
""")
    
    # Create project progress file
    with open(os.path.join(ai_team_dir, 'PROJECT_PROGRESS.md'), 'w', encoding='utf-8') as f:
        team_desc = "Dual team (Internal + Internet)" if team_type == 'dual' else "Single team (Internal only)"
        f.write(f"""# Project Progress Overview
Project Name: {os.path.basename(project_path)}
Project Type: {project_type}
Team Architecture: {team_desc}
Creation Date: {os.popen('date').read().strip()}
""")

def main():
    parser = argparse.ArgumentParser(description='Create AI team directory structure for projects')
    parser.add_argument('--project-path', required=True, help='Path to the project directory')
    parser.add_argument('--team-type', choices=['single', 'dual'], default='single', help='Team type (default: single)')
    parser.add_argument('--project-type', choices=['web_app', 'ecommerce', 'mobile_app', 'generic'], default='generic', help='Project type (default: generic)')
    
    args = parser.parse_args()
    
    print(f"Creating AI team structure...")
    print(f"Project path: {args.project_path}")
    print(f"Team type: {args.team_type}")
    print(f"Project type: {args.project_type}")
    
    create_ai_team_structure(args.project_path, args.team_type, args.project_type)
    
    print(f"\n✅ AI team structure created successfully!")
    print(f"Location: {os.path.join(args.project_path, 'ai-team')}")

if __name__ == '__main__':
    main()