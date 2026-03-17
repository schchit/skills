# Auto Create AI Team

A simple, transparent Python script that creates organized AI team directory structures for your projects.

## What it actually does
This tool creates a standardized `ai-team` folder in your project directory containing:
- Internal AI team configuration files
- Optional internet marketing team configuration (dual mode)
- Project progress tracking file

**Important**: This is a **local file creation tool only**. It does not:
- Make any network requests
- Connect to external services  
- Require API keys or credentials
- Collect or transmit any data

## Installation
No installation required! Just download the `create_ai_team.py` file and run it.

## Usage Examples

### Basic usage (single team):
```bash
python create_ai_team.py --project-path ./my-project
```

### Dual team mode:
```bash
python create_ai_team.py --project-path ./my-project --team-type dual
```

### Specify project type:
```bash
python create_ai_team.py --project-path ./my-ecommerce-site --team-type dual --project-type ecommerce
```

## Command Line Options
- `--project-path` (required): Path to your project directory
- `--team-type` (optional): `single` (default) or `dual`
- `--project-type` (optional): `web_app`, `ecommerce`, `mobile_app`, or `generic` (default)

## Security & Privacy
- **100% offline**: No network connectivity whatsoever
- **Local files only**: Only creates files in your specified project directory
- **No dependencies**: Uses only Python standard library
- **Fully auditable**: All code is in the single `create_ai_team.py` file
- **No hidden functionality**: What you see is exactly what it does

## Requirements
- Python 3.6 or higher
- No additional packages needed