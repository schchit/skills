# State Diagram

## Diagram Description
A state diagram describes the various states an object or system undergoes during its lifecycle, along with events or conditions that cause state transitions.

## Applicable Scenarios
- Object state management design
- State machine modeling
- Business process state flow
- Protocol state machines
- UI component state management

## Syntax Examples

```mermaid
stateDiagram
    [*] --> InitialState
    InitialState --> Processing: Event1
    Processing --> Completed: Event2
    Processing --> Error: Event3
    Error --> Processing: Retry
    Completed --> [*]

    state Processing {
        [*] --> Step1
        Step1 --> Step2
        Step2 --> [*]
    }
```

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> InProgress: Start Task
    InProgress --> Paused: Pause Command
    Paused --> InProgress: Resume Command
    InProgress --> Completed: Task Completed

    state Completed {
        [*] --> SaveResult
        SaveResult --> GenerateReport
        GenerateReport --> [*]
    }

    Completed --> [*]: End
```

## Syntax Reference

### Basic Syntax
```mermaid
stateDiagram
    [*] --> StateName: Transition Condition
    StateName --> [*]: End Transition
```

### Composite States
```mermaid
stateDiagram
    state CompositeStateName {
        [*] --> SubState1
        SubState1 --> SubState2
        SubState2 --> [*]
    }
```

### Conditional Branching
```mermaid
stateDiagram
    StateA --> StateB: ConditionX
    StateA --> StateC: ConditionY
```

### Special Markers
- `[*]`: Start or end state
- `state xxx`: Normal state definition
- `state xxx { ... }`: Composite state

### History States
```mermaid
stateDiagram
    state PausedState {
        H --> RecoveryPoint
        [*] --> RecoveryPoint
    }
```

## Configuration Reference

| Option | Description |
|--------|-------------|
| showNullElements | Show null elements |
| hideEmptyDescription | Hide empty descriptions |
| fork/join | Fork/join support |

### Styles
```mermaid
stateDiagram
    [*] --> State1
    State1: This is state description

    classDef active fill:#f96
    class State1 active
```
