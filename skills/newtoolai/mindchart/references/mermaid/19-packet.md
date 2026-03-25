# Packet Diagram

## Diagram Description
A packet diagram displays the structure of network packets or the composition of Protocol Data Units (PDU). Suitable for network protocol learning and communication architecture documentation.

## Applicable Scenarios
- Network protocol teaching
- Data structure display
- Communication protocol documentation
- Data encapsulation and parsing
- OSI model visualization

## Syntax Examples

```mermaid
packet
    title Packet Structure Example

    0-15: Source Port
    16-31: Destination Port
    32-63: Sequence Number
    64-95: Acknowledgment Number
    96-99: Data Offset|Reserved|Control Flags
    100-111: Window Size
    112-127: Checksum
    128-143: Urgent Pointer
    144-159: Options
    160-191: Data
```

```mermaid
packet
    title IPv4 Packet Header

    0-3: Version (4 bits)
    4-7: Header Length (4 bits)
    8-15: Type of Service (TOS)
    16-31: Total Length
    32-47: Identification
    48-50: Flags
    51-63: Fragment Offset
    64-71: Time to Live (TTL)
    72-79: Protocol
    80-95: Header Checksum
    96-127: Source IP Address
    128-159: Destination IP Address
    160-191: Options (optional)
```

## Syntax Reference

### Basic Syntax
```mermaid
packet
    title Title

    Start-End: Field Name (optional description)
    Start-End: Field Name
```

### Field Format
- `Start-End`: Bit positions (0-indexed)
- Can include description text in parentheses
- One field per line

### Color Markers
```mermaid
packet
    0-7: Header
    8-31: Data

    style 0-7 fill:#f96
```

### Grouped Display
```mermaid
packet
    title Grouping Example

    0-3: Group 1
    4-7: Group 2
    0-7: Overall Coverage
```

## Configuration Reference

### Width Settings
```mermaid
packet
    title Example
    0-15: Field 1
        0-7: Subfield 1a
        8-15: Subfield 1b
```

### Style Configuration
```mermaid
packet
    0-31: Data

    style 0-31 fill:#e1f5fe
```

### Notes
- Position ranges should be correct
- Avoid overlapping
- Field names should be clear
