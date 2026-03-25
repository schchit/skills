# Pie Chart

## Diagram Description
A pie chart is a circular diagram used to display the proportion of parts to the whole. The size of each sector visually represents the percentage of different categories.

## Applicable Scenarios
- Proportion analysis display
- Survey result distribution
- Resource allocation ratios
- Budget allocation
- Category statistics

## Syntax Examples

```mermaid
pie title Programming Language Usage Statistics
    "JavaScript": 45
    "Python": 30
    "Java": 15
    "Go": 5
    "Others": 5
```

```mermaid
pie title Project Budget Allocation
    "Labor Costs": 500000
    "Servers": 150000
    "Marketing": 100000
    "Office Equipment": 50000
    "Others": 20000
```

## Syntax Reference

### Basic Syntax
```mermaid
pie title Title
    "Label1": Value1
    "Label2": Value2
    "Label3": Value3
```

### Label Format
- Strings can be enclosed in quotes
- Values can be integers or decimals
- Values are automatically calculated as percentages

### Special Value Handling
```mermaid
pie
    "Completed": 120
    "In Progress": 80
    "Not Started": 30
```

### Pie Chart with Descriptions
```mermaid
pie title Market Share
    "Product A - Leading Brand": 40
    "Product B - Rising Star": 35
    "Product C - Professional Field": 15
    "Others": 10
```

## Configuration Reference

### Style Options
```mermaid
pie title Example
    style .1 fill:#f9f
    style .2 fill:#9f9
```

### Legend Position
Mermaid pie charts display the legend on the right by default.

### Color Customization
CSS styles or Mermaid's `style` directive can be used to set colors for each sector.

### Notes
- Pie charts are suitable for displaying a small number of categories (3-7)
- Too many categories will make it difficult to read
- All values should be positive numbers
