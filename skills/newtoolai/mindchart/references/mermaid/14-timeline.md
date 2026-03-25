# Timeline

## Diagram Description
A timeline displays events in chronological order, suitable for showing historical development, project progress, or event chronology.

## Applicable Scenarios
- Historical event display
- Project development history
- Company/product milestones
- Personal resume/CV
- Project retrospective

## Syntax Examples

```mermaid
timeline
    title Project Development History

    2020 : Project Launch
        Complete feasibility study
        Form core team
    2021 : Rapid Growth
        v1.0 Release
        Series A Funding
        Team expands to 50
    2022 : Steady Development
        v2.0 Release
        Expand overseas markets
        Industry recognition
    2023 : Innovation Breakthrough
        v3.0 Release
        Launch AI features
        10 million users reached
```

```mermaid
timeline
    title Technology Development History

    1990s : Early Days
        Internet born
        Web 1.0 era
    2000s : Growth Period
        Web 2.0 emergence
        Social networks appear
    2010s : Explosion
        Mobile internet
        Cloud computing普及
        Big data era
    2020s : Intelligence Era
        AI/ML rise
        Metaverse concept
        AIGC explosion
```

## Syntax Reference

### Basic Syntax
```mermaid
timeline
    title Title

    Timepoint1 : Event1
        Event1 Details
    Timepoint2 : Event2
        Event2 Details
        Event2 Additional Notes
```

### Timepoint Formats
- Year: `2020`
- Year-month: `2020-03`
- Specific date: `2020-03-15`
- Era: `1990s`

### Event Hierarchy
- Main event: First line after colon
- Sub-event: Indented detailed description

### Multiple Events in Parallel
```mermaid
timeline
    title Example

    2023 : Event A
        : Event B
        : Event C
```

## Configuration Reference

### Style Options
```mermaid
timeline
    title Example
    sectionStyle 1 fill:#eaf
    sectionStyle 2 fill:#efe
```

### Theme Support
Can use Mermaid theme configuration for colors and styles.

### Notes
- Timeline order is important
- Moderate number of events
- Labels should be concise and clear
