---
name: mindchart
description: "This skill is triggered immediately when a user wants to convert text, documents, requirement descriptions, or data into visual diagrams. Supported diagram types include: flowcharts, sequence diagrams, mind maps, Gantt charts, ER diagrams, state diagrams, class diagrams, pie charts, quadrant charts, and more. Trigger keywords include but are not limited to: draw, generate diagram, flowchart, mind map, sequence diagram, Gantt chart, ER diagram, visualization, mindmap, mermaid, diagram, flowchart, sequence diagram, etc. This skill should be triggered whenever the user expresses any intent to \"turn content into a diagram\" - do not rely on the user explicitly mentioning technical terms."
compatibility: "Requires JavaScript runtime environment (Node.js or Bun). Dependencies: @mermaid-js/mermaid-cli, markmap-cli, markmap-lib, markmap-render, puppeteer"
---

# Mindchart — Diagram Generation Skill

Automatically convert text, documents, and process descriptions into high-quality visual images (PNG).

---

## Dependency Installation

```bash
# Using npm
npm install @mermaid-js/mermaid-cli markmap-cli markmap-lib markmap-render puppeteer

# Using bun
bun install @mermaid-js/mermaid-cli markmap-cli markmap-lib markmap-render puppeteer
```

---

## Quick Decision: Which Tool to Use?

| User Requirement | Diagram Type | Tool to Use | Reference Document |
|---|---|---|---|
| Mind maps, knowledge structure diagrams, tree hierarchies | Mindmap | markmap-cli | `references/mindmap.md` |
| Flowcharts, sequence diagrams, Gantt charts, ER diagrams, state diagrams, class diagrams, pie charts, etc. | All others | mermaid-cli | `references/mermaid.md` |

> If the user does not explicitly specify a type, make an autonomous judgment based on content characteristics: hierarchical/divergent structure → Mindmap; process/time/relationships → Mermaid.

---

## Workflow

- If the user requests a mind map, read file `references/mindmap.md`
- If the user requests other diagrams, read file `references/mermaid.md`
- Generated images are saved to: current working directory by default, or a user-specified directory. If using bots like openclaw, send as image files to the user
- Temporary files are saved to: `/tmp/__mindchart__`
