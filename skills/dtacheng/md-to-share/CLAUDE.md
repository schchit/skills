# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MD to Share is a Markdown-to-long-image converter. It converts `.md` files to PNG images using Puppeteer and Chrome for rendering. Designed to be callable by AI Agents.

## Commands

```bash
# Install dependencies
npm install

# Convert markdown to image
node md2img.mjs <input.md> <output.png>

# Or use global command after npm link
npm link
md2img <input.md> <output.png>
```

## Architecture

Single-file architecture in `md2img.mjs`:
1. Reads markdown file → parses with `marked`
2. Wraps HTML in styled template (800px width, mobile-optimized)
3. Renders with Puppeteer using system Chrome
4. Screenshots full page to PNG

**Key path**: Chrome executable is hardcoded to macOS path: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

## Dependencies

- Node.js 18+
- puppeteer-core (uses system Chrome, not bundled Chromium)
- marked (markdown parser)
- System Google Chrome must be installed
