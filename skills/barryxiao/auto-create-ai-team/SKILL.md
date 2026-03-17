# Auto Create AI Team

## Description
Creates AI team directory structures for projects. This is a simple, standalone Python script that generates organized team folders and configuration files locally.

## Usage
```bash
python create_ai_team.py --project-path /path/to/project [--team-type single|dual] [--project-type web_app|ecommerce|mobile_app|generic]
```

## Features
- Creates internal AI team directory structure with configuration files
- Optional internet marketing team (dual mode)  
- Project type detection for appropriate team member assignment
- Generates project progress tracking file
- Works completely offline with no external dependencies

## Output Structure
```
project/
└── ai-team/
    ├── internal-team/
    │   └── team-info/
    │       └── AI_TEAM_CONFIG.md
    ├── internet-team/     # Only created in dual mode
    │   └── team-info/
    │       └── INTERNET_TEAM_CONFIG.md
    └── PROJECT_PROGRESS.md
```

## Requirements
- Python 3.6+
- No external dependencies (uses only standard library)

## Security
- **Completely offline**: No network calls, API requests, or external data transmission
- **Local file operations only**: Only reads/writes files in the specified project directory
- **No credentials required**: Does not require or store any authentication tokens or API keys
- **Fully transparent**: All functionality is contained in the single create_ai_team.py file
- **No environment variables**: All configuration is done via command line arguments