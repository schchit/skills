# Mermaid Diagram

## Description

This skill is triggered when users want to generate various Mermaid diagrams (flowcharts, sequence diagrams, mind maps, Gantt charts, ER diagrams, etc.) from text, documents, or descriptions. It automatically analyzes user requirements, looks up syntax for the corresponding diagram type from reference documentation, generates concise and elegant Mermaid code, and renders it as a PNG image for delivery to the user.

## Supported Diagram Types

| ID | Diagram Type | Mermaid Syntax | Reference File |
|----|-------------|----------------|----------------|
| 01 | Flowchart | `flowchart` | mermaid/01-flowchart.md |
| 02 | Sequence Diagram | `sequenceDiagram` | mermaid/02-sequence.md |
| 03 | Class Diagram | `classDiagram` | mermaid/03-class.md |
| 04 | State Diagram | `stateDiagram` | mermaid/04-state.md |
| 05 | Entity Relationship Diagram | `erDiagram` | mermaid/05-entity-relationship.md |
| 06 | User Journey | `journey` | mermaid/06-user-journey.md |
| 07 | Gantt Chart | `gantt` | mermaid/07-gantt.md |
| 08 | Pie Chart | `pie` | mermaid/08-pie.md |
| 09 | Quadrant Chart | `quadrantChart` | mermaid/09-quadrant.md |
| 10 | Requirement Diagram | `requirementDiagram` | mermaid/10-requirement.md |
| 11 | Git Graph | `gitGraph` | mermaid/11-git-graph.md |
| 12 | C4 Diagram | `c4context` | mermaid/12-c4.md |
| 13 | Mind Map | `mindmap` | mermaid/13-mindmap.md |
| 14 | Timeline | `timeline` | mermaid/14-timeline.md |
| 15 | ZenUML | `zenuml` | mermaid/15-zenuml.md |
| 16 | Sankey Diagram | `sankey` | mermaid/16-sankey.md |
| 17 | XY Chart | `xychart` | mermaid/17-xy-chart.md |
| 18 | Block Diagram | `block` | mermaid/18-block.md |
| 19 | Packet Diagram | `packet` | mermaid/19-packet.md |
| 20 | Kanban | `kanban` | mermaid/20-kanban.md |
| 21 | Architecture Diagram | `architecture` | mermaid/21-architecture.md |
| 22 | Other | `graph` | mermaid/22-others.md |

## Workflow

### Step 1: Intent Recognition and Diagram Type Matching

Analyze user input to identify the diagram type to generate:

1. **Keyword Matching**: Identify diagram type based on keywords in user description
   - "mind map" → mindmap
   - "sequence diagram", "sequence", "interaction flow" → sequenceDiagram
   - "flowchart", "flow" → flowchart
   - "Gantt chart", "progress" → gantt
   - "architecture diagram", "architecture" → architecture
   - "ER diagram", "entity relationship" → erDiagram
   - "class diagram" → classDiagram
   - "state diagram" → stateDiagram
   - And so on for pie charts, quadrant charts, Git graphs, etc.

2. **Context Inference**: If direct matching is not possible, infer the most suitable diagram type based on the user's business scenario

3. **Fallback**: If still unable to determine, use `graph` (standard flowchart) as the default

### Step 2: Read Reference Documentation

Based on the identified diagram type, read the corresponding reference documentation:

```
skills/mindflow/references/mermaid/{id}-{typename}.md
```

Reference documentation contains for each diagram type:
- Diagram description and applicable scenarios
- Syntax examples
- Detailed syntax explanation
- Configuration options

### Step 3: Generate Mermaid Code (text-to-mmd)

Generate Mermaid code based on user requirements and reference syntax:

**Requirements**:
- Strictly follow Mermaid official syntax specifications
- **Core code within 250 tokens** (concise and powerful, avoid redundancy)
- Use Chinese node names (Mermaid natively supports Chinese)
- Clear code structure with proper indentation

**Generation Strategy**:
1. Extract key entities and relationships from user requirements
2. Reference example syntax from documentation
3. Generate concise but complete Mermaid code
4. Write code to a temporary `.mmd` file

### Step 4: Render PNG (mmd-to-png)

Use Mermaid CLI for rendering:

**Ensure width and height are 20000px**

```bash
mmdc -i <mmd_file> -o <png_file> -e png -w 20000 -H 20000
```

### Step 5: Deliver PNG File

Inform the user of the generated PNG file path.

**Output Format**:
```
Diagram generated: [Diagram Type Description]

File location: /path/to/output.png

You can use this image directly, or let me know if you need adjustments.
```

## Notes

1. **Mermaid Syntax Correctness**: Verify syntax in mind before generating; ensure node names, connectors, and indentation are correct
2. **Token Limit**: Keep core diagram code within 250 tokens; complex diagrams can use abbreviations or concise descriptions
3. **Chinese Support**: Mermaid fully supports Chinese; node names can use Chinese directly
5. **File Cleanup**: Temporary .mmd files should be deleted after rendering

## Error Handling

| Error Situation | Handling |
|----------------|----------|
| Rendering fails due to Mermaid syntax error | Analyze error message, fix code and retry |
| User-requested diagram type not in supported list | Use `graph` (flowchart) as fallback |
| Diagram too complex exceeds token limit | Simplify content, keep core elements, or ask user which content to prioritize |
