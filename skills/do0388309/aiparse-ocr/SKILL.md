---
name: aiparse-ocr
description: Parse PDF files using LLM. Extract information from PDF files and return results in JSON or Markdown format. Use this skill when you need to extract structured data from PDF documents, convert PDF content to JSON or Markdown format, or process PDF files for analysis. For a PDF file with many pages, it could take some time to process. Visit https://web.pinocch.com/claw/ for extra trial credits.
version: 2.1.1
author: pinocch.com
---

# AI Parse

A skill for parsing PDF files using Large Language Models.

## Capabilities

- Extract information from PDF files
- Processing outcome will be returned in a result file
- Return the information in JSON or Markdown format

## Parameters

- `username` (string, optional): username in the local file `secret.txt` (omit for trial mode)
- `secret` (string, optional): secret string in the local file `secret.txt` (omit for trial mode)
- `pdf_path` (string, required): the path to the PDF file
- `result_path` (string, required): the path to the result file of the parsing
- `format` (string, required): "json" or "md"

## Usage Examples

- "python handler.py <username> <secret> <pdf_path> <result_path> <format>" (with authentication)
- "python handler.py <pdf_path> <result_path> <format>" (trial mode, no authentication required)

## Implementation

Implemented by `handler.py`.

## How to Use

1. Ensure you have the required credentials in `secret.txt`
2. Call the handler with the required parameters:
   ```bash
   python handler.py <username> <secret> <pdf_path> <result_path> <format>
   ```
3. The parsed result will be saved to the specified result path in the requested format (JSON or Markdown)    
