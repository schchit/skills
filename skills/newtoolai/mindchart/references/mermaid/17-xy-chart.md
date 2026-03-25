# XY Chart

## Diagram Description
An XY chart is a chart type used to display relationships between two variables, supporting line charts, scatter plots, and other forms. Suitable for data analysis and trend presentation.

## Applicable Scenarios
- Data trend analysis
- Variable correlation display
- Business data visualization
- Scientific experiment results
- Statistical data analysis

## Syntax Examples

```mermaid
xychart-beta
    title Sales Trend
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    y-axis Sales(10k) 0 --> 100
    line [25, 45, 35, 65, 70, 85]
```

```mermaid
xychart-beta
    title Height and Weight Distribution
    x-axis Weight(kg) [40, 50, 60, 70, 80, 90]
    y-axis Height(cm) [150, 160, 170, 180, 190]
    scatter [65, 170], [70, 175], [55, 160], [80, 180]
```

## Syntax Reference

### Basic Syntax
```mermaid
xychart-beta
    title Chart Title
    x-axis X-axis Label [Value1, Value2, Value3]
    y-axis Y-axis Label MinValue --> MaxValue
    line [DataPoint1, DataPoint2, DataPoint3]
```

### Chart Types
- `line`: Line chart
- `bar`: Bar chart
- `scatter`: Scatter plot

### Data Format
```mermaid
xychart-beta
    x-axis [Category1, Category2, Category3]
    y-axis Value 0 --> 100

    line [Data1, Data2, Data3]
    bar [Data1, Data2, Data3]
```

### Multiple Series Data
```mermaid
xychart-beta
    title Multiple Series Comparison
    x-axis [Q1, Q2, Q3, Q4]
    y-axis Sales(10k) 0 --> 200

    line SeriesA [45, 65, 85, 95]
    line SeriesB [35, 55, 75, 90]
```

## Configuration Reference

### Axis Configuration
```mermaid
xychart-beta
    x-axis [A, B, C, D]
    y-axis Value -50 --> 150
```

### Theme Styles
Can use Mermaid theme configuration for color schemes.

### Notes
- XY Chart is a beta feature
- Moderate number of data points
- Set axis ranges appropriately
- Recommend validating latest syntax support
