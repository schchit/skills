# Entity Relationship Diagram (ER Diagram)

## Diagram Description
An entity relationship diagram represents entities in a database, their attributes, and relationships between entities. It is an important tool for database design and modeling.

## Applicable Scenarios
- Database design
- Data modeling
- Business data relationship organization
- API data structure design
- System integration data mapping

## Syntax Examples

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string email
        string password
        datetime created_at
    }

    ORDER {
        int id PK
        int user_id FK
        decimal total_amount
        string status
        datetime created_at
    }

    PRODUCT {
        int id PK
        string name
        string description
        decimal price
        int stock
    }

    ORDER_ITEM {
        int order_id FK
        int product_id FK
        int quantity
        decimal subtotal
    }

    USER ||--o{ ORDER : "places"
    ORDER ||--|{ ORDER_ITEM : "contains"
    PRODUCT ||--o{ ORDER_ITEM : "included in"
```

## Syntax Reference

### Basic Syntax
```mermaid
erDiagram
    ENTITY_NAME {
        type field_name PK "comment"
        type field_name FK "comment"
        type field_name "comment"
    }
```

### Field Types
- `int`, `string`, `boolean`, `datetime`, `decimal`, `float`

### Field Modifiers
- `PK`: Primary Key
- `FK`: Foreign Key
- `UK`: Unique Key
- `NN`: Not Null

### Relationship Symbols

| Symbol | Description |
|--------|-------------|
| `||` | Exactly one |
| `o|` | Zero or one |
| `}|` | One or more |
| `o{` | Zero or more |
| `||--||` | One-to-one |
| `||--o{` | One-to-many |
| `}|--||` | Many-to-one |
| `}|--o{` | Many-to-many |

### Relationship Labels
```mermaid
erDiagram
    A ||--o{ B : "Relationship Label"
    A {
        int id PK
    }
    B {
        int id PK
        int a_id FK
    }
```

## Configuration Reference

| Option | Description |
|--------|-------------|
| showEntityTypes | Show entity types |
| entitySeparation | Entity spacing |
| relationshipSeparation | Relationship spacing |

### Style Configuration
```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        string name "Name"
        int cust_id PK
    }
```
