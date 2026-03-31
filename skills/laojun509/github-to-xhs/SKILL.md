---
name: github-to-xhs
description: Analyze a GitHub repository and generate Xiaohongshu (Little Red Book) infographic posts. Use when the user wants to create social media content about a GitHub project, including technical analysis, feature highlights, and promotional posts. Supports automatic content analysis, multiple outline strategies, and HTML-based visual output.
---

# GitHub to Xiaohongshu Skill

Transform any GitHub repository into engaging Xiaohongshu (小红书) infographic content.

## Usage

```bash
# Basic usage - analyze a GitHub repo and generate XHS content
/github-to-xhs https://github.com/user/repo

# With specific focus
/github-to-xhs https://github.com/user/repo --focus "AI features"

# After generation, files are in:
# /root/.openclaw/workspace/xhs-images/{repo-slug}/
```

## Workflow

### Step 1: Fetch GitHub Repository

Use `web_fetch` to get the repository's README and main content.

```
https://github.com/{owner}/{repo}
```

### Step 2: Content Analysis

Analyze the repository and create `analysis.md`:

```markdown
# {repo-name} Analysis

## Project Info
- Name: {name}
- Author: {author}
- Stars: {stars}
- Language: {language}
- Description: {description}

## Core Features
- Feature 1
- Feature 2
...

## Target Audience
- Audience 1
- Audience 2

## XHS Angles
- Hook ideas (max 20 characters for title)
- Visual opportunities
```

### Step 3: Generate Outline Strategies

Create 6 different outline strategies with distinct visual styles:

**Strategy A - Story-Driven** (outline-strategy-a.md)
- Personal discovery narrative
- Problem → Solution → Result flow
- 4 images, warm/cute style
- Soft gradients, bookmarks, progress bars

**Strategy B - Information-Dense** (outline-strategy-b.md)
- Feature highlights + technical details
- Comparison tables + code blocks
- 5 images, notion/minimal style
- Grid background, geometric shapes

**Strategy C - Visual-First** (outline-strategy-c.md)
- Bold visuals, minimal text
- Showcase/demo focus
- 3 images, bold/pop style
- Large icons, big numbers, solid colors

**Strategy D - Cyberpunk Tech** (outline-strategy-d.md) ⭐ NEW
- Neon colors, dark background
- Perfect for developer tools, AI projects
- 4-5 images, glowing accents
- Dark theme (#0a0a0a), neon cyan/pink/purple

**Strategy E - Warm Hand-drawn** (outline-strategy-e.md) ⭐ NEW
- Sketchy, organic, friendly
- Great for beginner tutorials, educational content
- 4-5 images, paper texture background
- Earth tones, hand-drawn icons, doodles

**Strategy F - Dark Professional** (outline-strategy-f.md) ⭐ NEW
- Sleek, premium, enterprise feel
- Ideal for business tools, SaaS products
- 5 images, dark navy background
- Gold/amber accents, glassmorphism effects

### Step 4: User Selection

Present all 6 strategies and ask user to choose:

```
📋 Select your preferred strategy:
- A: Story-Driven (4 images, emotional, warm)
- B: Information-Dense (5 images, technical, notion) ⭐ Default
- C: Visual-First (3 images, bold, minimal)
- D: Cyberpunk Tech (4-5 images, neon dark, dev tools)
- E: Warm Hand-drawn (4-5 images, sketchy, educational)
- F: Dark Professional (5 images, premium, enterprise)

Or specify a style: "Use cyberpunk style" / "Make it warm and friendly"
```

### Step 5: Generate Content

Create final files:

1. `outline.md` - Selected strategy
2. `prompts/NN-{type}-{slug}.md` - Image generation prompts for each slide
3. `xiaohongshu-post.html` - Complete HTML with all 5 slides styled for XHS

### Step 6: Package Output

Create tar.gz archive:
```bash
tar -czf {repo-slug}-xhs.tar.gz {repo-slug}/
```

## Output Structure

```
xhs-images/{repo-slug}/
├── source-{slug}.md              # Original GitHub content
├── analysis.md                   # Content analysis
├── outline-strategy-a.md         # Story-driven (warm)
├── outline-strategy-b.md         # Information-dense (notion)
├── outline-strategy-c.md         # Visual-first (bold)
├── outline-strategy-d.md         # Cyberpunk tech (NEW)
├── outline-strategy-e.md         # Warm hand-drawn (NEW)
├── outline-strategy-f.md         # Dark professional (NEW)
├── outline.md                    # Final selected outline
├── prompts/
│   ├── 01-cover-{slug}.md
│   ├── 02-features-{slug}.md
│   ├── 03-tech-{slug}.md
│   ├── 04-compare-{slug}.md
│   └── 05-cta-{slug}.md
└── xiaohongshu-post.html         # Complete visual output
```

## HTML Output Features

The generated `xiaohongshu-post.html` includes multiple visual style templates:

### Available Style Themes

| Theme | Best For | Colors | Aesthetic |
|-------|----------|--------|-----------|
| **Notion** (Default) | Technical docs, tools | Off-white, gray, subtle accents | Clean, minimal, grid background |
| **Cyberpunk** | AI tools, dev projects | Dark bg, neon cyan/pink/purple | Glowing, futuristic, high contrast |
| **Warm** | Tutorials, education | Cream, earth tones, warm accents | Hand-drawn, friendly, organic |
| **Dark Pro** | Enterprise, SaaS | Navy/black, gold/amber accents | Premium, sleek, glassmorphism |
| **Bold Pop** | Visual products | Solid vibrant colors, high contrast | Eye-catching, minimal text |

### CSS Features (All Themes)

- 5 responsive cards (375×500px each)
- Custom background patterns per theme
- Animated accents (where appropriate)
- Comparison tables with theme-appropriate styling
- Code blocks with syntax highlighting
- Mobile-first design

## Image Generation Prompts

Each prompt file includes:
- Canvas specifications (375×500px)
- Visual style (see Available Style Themes above)
- Content layout
- Color palette specific to theme
- Typography notes

## Examples

**Example 1: Tool/Library**
```
User: /github-to-xhs https://github.com/mvanhorn/last30days-skill

Output: 5-card XHS post about multi-source research tool
- P1: Cover with 10 platform logos
- P2: 4 core features
- P3: Algorithm pie chart
- P4: Manual vs Auto comparison
- P5: Install commands
```

**Example 2: Framework**
```
User: /github-to-xhs https://github.com/vercel/next.js

Output: Technical introduction with:
- Key features highlight
- Performance metrics
- Code examples
- Getting started guide
```

## Tips

- **Title limit**: Keep titles under 20 characters (XHS display limit)
- **Style selection guide**:
  - Use A (Story-Driven) for: personal projects, beginner tutorials, emotional connection
  - Use B (Information-Dense) for: technical tools, libraries, frameworks
  - Use C (Visual-First) for: visual products, demos, screenshot-heavy content
  - Use D (Cyberpunk) for: AI tools, dev tools, futuristic/tech projects
  - Use E (Hand-drawn) for: education, tutorials, friendly/approachable tools
  - Use F (Dark Pro) for: enterprise SaaS, business tools, premium products
- Always check if user has preferences for style/layout
- The HTML output can be screenshot for XHS posting
- Mix and match: You can combine elements from different styles
