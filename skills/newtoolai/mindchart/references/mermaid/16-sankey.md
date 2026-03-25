# Sankey Diagram

## Diagram Description
A Sankey diagram is an energy flow diagram used to display data flow between different states or categories. Commonly used for energy analysis, cost breakdown, and traffic analysis scenarios.

## Applicable Scenarios
- Energy flow analysis
- Cost structure analysis
- User behavior flow
- Budget allocation display
- Conversion funnel analysis

## Syntax Examples

```mermaid
sankey-beta

    Visitors["Visitors<br>1000"]: 900
    Registered["Registered Users<br>300"]: 300
    Active["Active Users<br>150"]: 150
    Paid["Paid Users<br>50"]: 50

    Visitors --> Registered: 300
    Visitors --> Bounced["Bounced Users<br>600"]: 600
    Registered --> Active: 150
    Registered --> Churned["Churned Users<br>150"]: 150
    Active --> Paid: 50
    Active --> Free["Free Users<br>100"]: 100
```

## Syntax Reference

### Basic Syntax
```mermaid
sankey-beta

    NodeA["Label<br>Value"]: FlowValue
    NodeB["Label"]: FlowValue

    NodeA --> NodeB: FlowValue
```

### Node Format
```mermaid
sankey-beta
    NodeName["Display Label"]: Value
```

### Node Naming Rules
- Use meaningful names
- Can include HTML line breaks `<br>`
- Value represents the flow magnitude of the node

### Connection Syntax
```mermaid
sankey-beta
    A --> B: FlowValue
    A --> C: FlowValue
    B --> D: FlowValue
```

### Flow Calculation
- Total input flow = Total output flow
- Flow values should match values on connection lines

## Configuration Reference

### Sankey Configuration Options
```mermaid
sankey-beta
    config
        width: 800
        height: 600
```

### Style Settings
```mermaid
sankey-beta
    style Node fill:#f9f,stroke:#333
```

### Notes
- Sankey is a beta feature; syntax may change
- Flows need to be conserved (input = output)
- Moderate number of nodes and flows
- Recommend validating syntax before using in production
