# Gantt Chart

## Diagram Description
A Gantt chart is a bar chart used to display project progress, scheduling, and task dependencies. The horizontal axis represents time, and the vertical axis represents tasks or project components.

## Applicable Scenarios
- Project management progress display
- Task scheduling
- Resource allocation visualization
- Milestone tracking
- Production planning

## Syntax Examples

```mermaid
gantt
    title Project Development Plan
    dateFormat YYYY-MM-DD
    section Design Phase
        Requirements Analysis: a1, 2024-01-01, 7d
        Prototype Design: a2, after a1, 5d
        UI Design: a3, after a2, 5d
    section Development Phase
        Frontend Development: b1, after a3, 10d
        Backend Development: b2, after a3, 12d
        API Integration: b3, after b1, 3d
    section Testing Phase
        Unit Testing: c1, after b1, 5d
        Integration Testing: c2, after b2, 4d
        Deployment: c3, after c1 c2, 2d
```

```mermaid
gantt
    title Milestone Example
    dateFormat YYYY-MM-DD

    section Project Phases
    Kickoff Meeting: milestone0, 2024-01-01, 0d
    Requirements Complete: milestone1, 2024-01-15, 0d
    Development Complete: milestone2, 2024-02-15, 0d
    Testing Complete: milestone3, 2024-03-01, 0d
    Release: milestone4, 2024-03-15, 0d
```

## Syntax Reference

### Basic Syntax
```mermaid
gantt
    title Title
    dateFormat DateFormat
    section SectionName
        Task Name: TaskID, StartDate, Duration
```

### Date Formats
- `YYYY-MM-DD`: 2024-01-15
- `YYYY-MM-DD HH:mm`: 2024-01-15 09:00
- `DD/MM/YYYY`: 15/01/2024
- `MM-DD`: 01-15 (current year)

### Duration Representation
- `7d`: 7 days
- `3w`: 3 weeks
- `2m`: 2 months
- `10h`: 10 hours
- `30m`: 30 minutes

### Task Dependencies
```mermaid
gantt
    task1: t1, 2024-01-01, 5d
    task2: t2, after t1, 3d
    task3: t3, after t2, 2d
```

### Critical Tasks and Milestones
```mermaid
gantt
    Completed Task: done, t1, 2024-01-01, 10d
    Active Task: active, t2, 2024-01-05, 5d
    Future Task: t3, 2024-01-10, 3d
    Milestone: milestone, m1, 2024-01-15, 0d
```

### Task Status
- `done`: Completed (dark)
- `active`: In progress (colored)
- `crit`: Critical task (red border)
- Default: Future task (light)

## Configuration Reference

| Option | Description |
|--------|-------------|
| title | Chart title |
| dateFormat | Date format |
| axisFormat | Timeline format |
| sectionSeparator | Section separator |
| inclusiveEndDates | End date inclusiveness |

### Timeline Format
```mermaid
gantt
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
```
