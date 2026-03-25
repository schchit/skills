# Architecture Diagram

## Diagram Description
An architecture diagram displays the components, connections, and dependencies of a software system or technical architecture. It is an important tool for system design and documentation.

## Applicable Scenarios
- System architecture design
- Technology stack presentation
- Cloud architecture visualization
- Microservices architecture
- Infrastructure architecture

## Syntax Examples

```mermaid
architecture-beta

   group api[API Layer]
        service apiserver[API Server]::cloud
        service gateway[API Gateway]::cloud
    end

    group application[Application Layer]
        service frontend[Frontend Application]::web
        service backend[Backend Service]::app
        service worker[Background Task]::app
    end

    group data[Data Layer]
        database db[(Database)]
        cache redis[Cache]
        queue queue[Message Queue]
    end

    api.apiserver --> application.backend
    api.gateway --> application.frontend
    application.backend --> data.db
    application.backend --> data.cache
    application.worker --> data.queue
    data.queue --> application.backend
```

```mermaid
architecture-beta

    service internet[Internet]:::public
    service cdn[CDN]:::cloud
    service lb[Load Balancer]:::infrastructure
    service web1[Web Server 1]:::web
    service web2[Web Server 2]:::web
    service app1[App Server 1]:::app
    service app2[App Server 2]:::app
    service db[Primary Database]:::database
    service dbreplica[Replica Database]:::database

    internet --> cdn
    cdn --> lb
    lb --> web1
    lb --> web2
    web1 --> app1
    web2 --> app2
    app1 --> db
    app2 --> dbreplica
    app1 --> app2
```

## Syntax Reference

### Basic Syntax
```mermaid
architecture-beta

    group GroupName[Group Label]
        service ServiceName[Service Label]::type
    end

    ServiceA --> ServiceB
```

### Service Definition
```mermaid
architecture-beta
    service name[Display Name]::type
```

### Service Types
- `cloud`: Cloud service
- `web`: Web service
- `app`: Application
- `database`: Database
- `infrastructure`: Infrastructure
- `external`: External service

### Group Definition
```mermaid
architecture-beta
    group GroupName[Display Name]
        ...
    end
```

### Connection Relationships
```mermaid
architecture-beta
    service a[...]:::type
    service b[...]:::type

    a --> b: Connection description
```

### Style Classes
```mermaid
architecture-beta
    service s[...]:::type

    classDef custom fill:#f9f,stroke:#333
    class s custom
```

## Configuration Reference

### Layout Options
```mermaid
architecture-beta
    config
        showShadows true
```

### Notes
- Architecture is a beta feature
- Syntax may change with version updates
- Recommend checking official documentation for latest syntax
