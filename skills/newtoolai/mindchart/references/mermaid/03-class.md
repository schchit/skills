# Class Diagram

## Diagram Description
A class diagram is a diagram in object-oriented programming used to display classes, class attributes, methods, and relationships between classes. It is one of the most commonly used diagrams in UML (Unified Modeling Language).

## Applicable Scenarios
- Software architecture design
- Code structure documentation
- Object relationship modeling
- API interface design
- Database table structure design

## Syntax Examples

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
        +eat() void
    }

    class Dog {
        +String breed
        +bark() void
        +fetch() void
    }

    class Cat {
        +boolean isIndoor
        +meow() void
        +scratch() void
    }

    Animal <|-- Dog : Inheritance
    Animal <|-- Cat : Inheritance
    Dog ..> Animal : Dependency
```

```mermaid
classDiagram
    class UserService {
        -UserRepository userRepo
        +createUser(name: String) User
        +deleteUser(id: Long) boolean
        +findUserById(id: Long) User
    }

    class UserRepository {
        +save(User) User
        +findById(Long) User
        +findAll() List~User~
        +deleteById(Long) void
    }

    UserService o-- UserRepository : Aggregation
```

## Syntax Reference

### Class Declaration
```mermaid
classDiagram
    class ClassName {
        +publicField String
        -privateField int
        #protectedField boolean
        ~packageField double
        +publicMethod() void
        -privateMethod() int
    }
```

### Access Modifiers
- `+`: public
- `-`: private
- `#`: protected
- `~`: package-level

### Relationship Types
- `<|--`: Inheritance (generalization)
- `*--`: Composition
- `o--`: Aggregation
- `-->`: Association
- `..>`: Dependency
- `..|>`: Implementation (interface)

### Relationship Labels
```mermaid
classDiagram
    A "1" *-- "many" B : Composition
    C "1" --> "1" D : One-to-One
```

### Interfaces and Abstract Classes
```mermaid
classDiagram
    interface Printable {
        <<interface>>
        +print() void
    }

    class Document {
        <<abstract>>
        +print() void
    }

    Document ..|> Printable : Implementation
```

### Class Annotations
```mermaid
classDiagram
    class Singleton {
        <<Singleton>>
        -static instance: Singleton
        -Singleton()
        +getInstance(): Singleton
    }
```

## Configuration Reference

| Option | Description |
|--------|-------------|
| showClassMembers | Show class members |
| defaultMemberAlignment | Member alignment |
| nodeSpacing | Node spacing |
| rankSpacing | Level spacing |

### Relationship Styles
```mermaid
classDiagram
    style A fill:#f9f,stroke:#333,stroke-width:2px
```
