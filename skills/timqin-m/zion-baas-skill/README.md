# Zion.app Headless BaaS Skill

This skill provides instructions and authentication code for building headless BaaS applications with [Zion.app](https://www.functorz.com) (functorz.com).

## Overview

Zion.app is a full-stack no-code development platform that can be used headlessly. This skill helps you build custom frontend applications while leveraging Zion as a pure backend-as-a-service (BaaS).

## Key URLs

- **HTTP URL**: `https://zion-app.functorz.com/zero/{projectExId}/api/graphql-v2`
- **WebSocket URL**: `wss://zion-app.functorz.com/zero/{projectExId}/api/graphql-subscription`
- **Meta API**: `https://zionbackend-internal.functorz.com/api/graphql`
- **Auth**: `https://auth.functorz.com/login`

## Quick Start

### 1. Install Dependencies

```bash
cd scripts
npm install
```

### 2. Authenticate

**Option A: OAuth Flow**
```bash
npm run auth
```

**Option B: Email/Password**
```bash
npm run auth:email <email> <password>
```

### 3. Fetch Runtime Token

```bash
npm run fetch-token -- <projectExId>
```

### 4. Use CLI Tools

**Execute GraphQL Query:**
```bash
npm run gql -- <projectExId> <role> '<query>' '[variables]'
```

**Subscribe to Events:**
```bash
npm run subscribe -- <projectExId> <role> '<subscription>' '[variables]'
```

**Search Projects:**
```bash
npm run meta -- search-projects [searchTerm]
```

**Fetch Schema:**
```bash
npm run meta -- fetch-schema <projectExId>
```

## Credential Storage

All credentials are stored in `.zion/credentials.yaml`:

```yaml
developer_token:
  token: "<token>"
  expiry: "<timestamp>"

project:
  exId: "<project_ex_id>"
  name: "<project_name>"
  admin_token:
    token: "<admin_token>"
    expiry: "<timestamp>"
```

## Features

- **Database Operations**: Full CRUD via GraphQL
- **Actionflows**: Sync and async workflow execution
- **AI Agents**: Multi-modal AI agent integration
- **File Upload**: Binary asset upload (images, videos, files)
- **Third-Party APIs**: HTTP API integration
- **Real-time**: GraphQL subscriptions via WebSocket

## Differences from Momen

This skill is adapted from the Momen BaaS skill with the following key changes:

| Aspect | Momen | Zion |
|--------|-------|------|
| Domain | momen.app | functorz.com |
| HTTP URL | villa.momen.app | zion-app.functorz.com |
| Meta API | backend.momen.app | zionbackend-internal.functorz.com |
| Auth | auth.momen.app | auth.functorz.com |
| Config Dir | .momen | .zion |

## License

MIT
