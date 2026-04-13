---
name: session-log-analyzer
description: Analyze agent session logs and generate PDF reports with Notion sync
version: 1.1.0
author: ClawdBot
tags: [logs, analysis, reporting, notion]
requires_bins: [python3]
requires_env: [NOTION_API_KEY, NOTION_REPORTS_DB_ID]
requires_config: []
---

# Session Log Analyzer

Analyze agent session logs and generate comprehensive PDF reports with Notion database integration.

## Available Tools

This skill uses ClawdBot's standard tools:
- **bash** - Execute commands
- **read_file** - Read files
- **write_file** - Write files  
- **web_fetch** - Fetch web content
- **web_search** - Search the web

## Usage

### Generate Log Analysis Report

User: "Analyze the session logs"
1. Run `python3 scripts/analyze_logs.py` to generate PDF report
2. Reports are saved to `pdfs/session_analysis_report.pdf`

### Sync Report to Notion

User: "Sync report to Notion"
1. Ensure NOTION_API_KEY and NOTION_REPORTS_DB_ID environment variables are set
2. Run `python3 scripts/sync_to_notion.py`

## Features

- Session count tracking
- Skill invocation statistics
- Success rate calculation
- Error tracking and reporting
- Skill usage breakdown
- Notion database synchronization

## Changelog

### Version 1.1.0
- 修复日志分析报告生成和 Notion 同步问题
- Fixed PDF generation path configuration
- Fixed Notion sync path issues
- Improved path handling for cross-environment compatibility

### Version 1.0.0
- Initial release
- Basic log analysis and PDF generation
- Notion integration support
