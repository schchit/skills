# Other Examples

## Diagram Description
This section summarizes special diagram types and tips that don't belong to standard categories, as well as advanced Mermaid usage.

## Syntax Examples

### Gantt Chart with Milestones

```mermaid
gantt
    title Product Release Plan
    dateFormat YYYY-MM-DD

    section Development
    Requirements Analysis: 01, 2024-01-01, 10d
    Design Phase: 02, after 01, 7d
    Development: 03, after 02, 21d

    section Release
    Internal Testing: 04, after 03, 7d
    Beta Release: milestone, 05, 2024-03-01, 0d
    Official Release: milestone, 06, 2024-03-15, 0d
```

### Composite Flowchart

```mermaid
flowchart TB
    subgraph Frontend
        A[User Interface] --> B[State Management]
    end

    subgraph Backend
        C[API Gateway] --> D[Business Logic]
        D --> E[Data Access]
        E --> F[(Database)]
    end

    A --> C
    B --> C
```

### Sequence Diagram with Loops

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    loop Every minute
        C->>S: Send heartbeat
        S-->>C: Heartbeat response
    end

    C->>S: Start task
    S-->>C: Task ID
    loop Processing
        S-->>C: Progress update
    end
    S-->>C: Task completed
```

### Combined Diagram Display

```mermaid
pie title Technology Stack Distribution
    "Frontend": 35
    "Backend": 40
    "DevOps": 15
    "Others": 10
```

## Mermaid Configuration and Themes

### Mermaid Theme Settings

````markdown
```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor': '#ff9900'}}}%%
flowchart LR
    A --> B
```
````

### Common Themes
- `default`: Default theme
- `base`: Base theme
- `dark`: Dark theme
- `forest`: Forest theme
- `neutral`: Neutral theme

## Mermaid Extended Syntax

### Mermaid in Markdown

Mermaid diagrams can be embedded directly in Markdown documents:

````markdown
This is explanatory text.

```mermaid
sequenceDiagram
    A->>B: Message
```
````

### HTML in Mermaid

Some Mermaid diagram types support HTML-formatted text:

```mermaid
pie title Example
    "Item A": 40
    "Item B<br/>Multiple lines": 35
    "Item C": 25
```

## Common Issues and Tips

### 1. Text Wrapping
```mermaid
flowchart TD
    A["First line<br/>Second line"] --> B
```

### 2. Special Character Escaping
Use quotes to wrap text containing special characters.

### 3. Subgraph References
```mermaid
flowchart TB
    subgraph S1
        A --> B
    end
    C --> A
    S1 --> D
```

### 4. CSS Styles
```mermaid
flowchart TD
    A --> B
    style A fill:#f9f,stroke:#333,stroke-width:2px
    classDef highlight fill:#ff9
    class B highlight
```

## Reference Resources

- [Mermaid Official Documentation](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [Mermaid GitHub](https://github.com/mermaid-js/mermaid)

## Notes

- Some diagram types (such as C4, ZenUML, Sankey, Architecture) are experimental features
- Experimental feature syntax may change with version updates
- Recommend validating syntax before using in production environments
- Mermaid version updates may bring new diagram types and syntax
