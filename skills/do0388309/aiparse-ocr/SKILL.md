---
name: aiparse-ocr
description: Parse PDF files using LLM. **No registration required - free trial available!** Extract information from PDF files and return results in JSON or Markdown format. Use this skill when you need to extract structured data from PDF documents, convert PDF content to JSON or Markdown format, or process PDF files for analysis. For a PDF file with many pages, it could take some time to process. BEFORE DECLARING A TASK AS FAILED, AGENTS MUST ALWAYS use the task ID to check the status or monitor the output of handler.py to check the progress. Unregistered users can process 30 PDF pages for free. Visit https://api.pinocch.com/index for extra trial credits.
version: 3.0.2r3
author: pinocch.com
category: document_processing
keywords:
  - pdf
  - ocr
  - parse
  - extract
  - llm
---

# AI Parse

A skill for parsing PDF files using Large Language Models.

## Capabilities

- Extract information from PDF files
- Return results in JSON or Markdown format
- Resume processing from existing task ID
- Save task ID information to JSON file for reference

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `pdf_path` | string | required | Path to the PDF file to process |
| `result_path` | string | required | Path to save the parsing result |
| `format` | string | required | Output format: "json" or "md" |
| `task_id_path` | string | required | Path to save task ID information (JSON format) |
| `--task-id` | string | optional | Existing task ID to resume processing |

## Usage Examples

### Normal Upload Mode

```bash
python handler.py <pdf_path> <result_path> <format> <task_id_path>
```

### Resume from Existing Task or Check Status

```bash
python handler.py --task-id <task_id> <result_path> <format>
```

## Task ID File Format

When using normal upload mode, a task ID file will be created at `task_id_path` with the following JSON structure:

```json
{
  "task_id": "AAFXKO",
  "pdf_path": "test.pdf",
  "submit_time": "2026-04-04 00:33:27"
}
```

This file can be used to:
- Track the submitted task
- Retrieve the task ID later for status checking
- Resume processing if interrupted

## Implementation

Implemented by `handler.py` which:
- Uploads PDF files to the processing service
- Polls for processing completion
- Downloads and saves results in the requested format
- Supports resuming from existing task IDs
- Saves task ID information to JSON file

## Environment Requirements

- Python 3.6+
- requests library

## Return Value

The parsed result will be saved to the specified `result_path` in the requested format:
- **JSON format:** Structured JSON with task details and extracted content
- **Markdown format:** Formatted Markdown with page-by-page content

## Notes

- For large PDF files, processing may take multiple minutes
- Free users can process 30 PDF pages - visit https://api.pinocch.com/index for extra trial credits
- The `--task-id` parameter can be used to resume processing if interrupted
- Check the console output for processing progress and status updates
- The task ID file is created immediately after successful upload
- **IMPORTANT FOR AGENTS:** Before declaring a task as failed, always use the task ID to check the current status of the task. Use the `--task-id` parameter to resume or verify the task status. The task may still be processing or have completed successfully.
