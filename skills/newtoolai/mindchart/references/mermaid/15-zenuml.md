# ZenUML

## Diagram Description
ZenUML is a diagram type for drawing sequence diagrams using concise text descriptions to generate professional sequence diagrams, with special emphasis on consistency between code and diagrams.

## Applicable Scenarios
- Core process description
- API call demonstration
- Technical documentation
- Architecture design documentation
- Teaching demonstrations

## Syntax Examples

```mermaid
zenuml
    title User Login Flow

    @Actor User
    @Participants
    User->>"Web Browser" : Open login page
    User->>"Web Application" : Enter username and password
    Web Application->>"Authentication Service" : Verify credentials
    alt Authentication successful
        Authentication Service-->>Web Application : Return Token
        Web Application-->>User : Redirect to home page
    else Authentication failed
        Authentication Service-->>Web Application : Return error
        Web Application-->>User : Display error message
    end
```

## Syntax Reference

### Basic Syntax
```mermaid
zenuml
    @Actor RoleName
    @Participants
    Participant1->>"Participant2" : Message content
```

### Participant Declaration
- `@Actor`: Define actor
- `@Participants`: Start defining participants

### Message Types
- `->>`: Synchronous message (solid arrow)
- `-->>`: Return message (dashed arrow)
- `->"Participant"`: Send message to specified participant

### Control Structures
```mermaid
zenuml
    alt Condition description
        ... messages ...
    else
        ... messages ...
    end

    loop Loop description
        ... messages ...
    end

    par Parallel execution
        ... messages ...
    and
        ... messages ...
    end
```

### Notes
```mermaid
zenuml
    @Note position : Note content
```

### Position Options
- `over Participant`: Above participant
- `left of Participant`: Left of participant
- `right of Participant`: Right of participant

## Configuration Reference

### Style Configuration
ZenUML supports custom colors, fonts, and other styles.

### Notes
- ZenUML is an experimental feature
- Syntax may differ from standard sequence diagrams
- Recommend checking official documentation for latest information
