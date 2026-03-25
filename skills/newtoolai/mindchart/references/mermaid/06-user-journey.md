# User Journey

## Diagram Description
A user journey diagram displays the steps, emotional changes, and touchpoints a user experiences while accomplishing a goal. It helps teams understand the complete process of user interaction with a product/service.

## Applicable Scenarios
- User experience design
- Business process optimization
- Customer service improvement
- Product feature planning
- User research presentation

## Syntax Examples

```mermaid
journey
    title User Online Shopping Journey
    section Browse Products
        Enter Website: 3: User
        Browse Categories: 4: User
        View Product Details: 2: User
    section Place Order
        Add to Cart: 5: User
        Fill Information: 3: User
        Complete Payment: 4: User
    section Post-Purchase Tracking
        View Order: 4: User
        Receive Package: 3: User
        Rate Product: 2: User
```

```mermaid
journey
    title New User Registration Process
    section Registration Flow
        Open App: 5: New User
        Click Register: 4: New User
        Fill Information: 2: New User
        Verify Phone: 1: New User
        Complete Registration: 4: New User
```

## Syntax Reference

### Basic Structure
```mermaid
journey
    title Title
    section StageName
        Step: Score: Actor
        Step: Score: Actor
```

### Scoring System
- Score range: 1-5
- 1: Very dissatisfied / Painful
- 2: Dissatisfied
- 3: Neutral / Average
- 4: Satisfied
- 5: Very satisfied / Pleasant

### Syntax Details
- `title`: Journey diagram title
- `section`: Define a stage/step group
- `Step Name`: Specific action description
- `Score`: Satisfaction or importance rating
- `Actor`: User role performing the action

### Multi-Actor Journey
```mermaid
journey
    title Customer Service Process
    section Issue Handling
        Receive Complaint: 2: Customer
        Record Issue: 3: Agent
        Analyze Cause: 4: Agent
        Resolve Issue: 5: Agent
        Confirm Satisfaction: 4: Customer
```

## Configuration Reference

| Option | Description |
|--------|-------------|
| showShadow | Show shadow effects |
| journeyWrap | Step text wrapping |

### Style Customization
```mermaid
journey
    title Example
    style Step1 fill:#f9f,stroke:#333
```
