# Kanban

## Diagram Description
A Kanban is a visual workflow management tool that displays task progress and status through columns and cards. Widely used in agile development and project management.

## Applicable Scenarios
- Project task management
- Agile development workflow
- Workflow visualization
- Team collaboration display
- Progress tracking

## Syntax Examples

```mermaid
kanban
    title Project Development Kanban

    [To Do] --> [In Progress] --> [Testing] --> [Done]

    [To Do]:
        - User Story A
        - User Story B
        - Bug Fix 1

    [In Progress]:
        - Feature Development X
        - Performance Optimization Y

    [Testing]:
        - Feature Module Z

    [Done]:
        - Infrastructure Setup
        - Database Design
```

```mermaid
kanban
    title Software Release Process

    [Backlog] --> [Sprint Planning] --> [In Progress] --> [Code Review] --> [Staging] --> [Production]

    [Backlog]:
        - Requirements gathering
        - Priority sorting

    [Sprint Planning]:
        - Sprint 1 planning

    [In Progress]:
        - Development Task 1
        - Development Task 2

    [Code Review]:
        - PR #123
        - PR #124

    [Staging]:
        - Release candidate

    [Production]:
        - v1.0.0 released
        - v1.0.1 released
```

## Syntax Reference

### Basic Syntax
```mermaid
kanban
    title Title

    [Column 1] --> [Column 2] --> [Column 3]

    [Column 1]:
        - Task 1
        - Task 2
```

### Column Definition
```mermaid
kanban
    [To Do]
    [In Progress]
    [Completed]
```

### Flow Arrows
```mermaid
kanban
    [A] --> [B]
    [B] --> [C]
    [A] -.-> [D]: Fast lane
```

### Task Items
- Use `-` prefix to list tasks
- Can nest sub-tasks
- Supports checkbox format

### Multiple Lanes
```mermaid
kanban
    [Team A Tasks] & [Team B Tasks] --> [Shared Tasks]
```

## Configuration Reference

### Style Options
```mermaid
kanban
    title Example

    style [In Progress] fill:#fff3e0
    style [Done] fill:#e8f5e9
```

### WIP Limits
```mermaid
kanban
    [In Progress]: 3
```

### Notes
- Moderate number of tasks
- Clear and readable flow
- Column names should be concise
