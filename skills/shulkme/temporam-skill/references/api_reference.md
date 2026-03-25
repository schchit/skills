# Temporam API Reference Details

This document outlines the key technical details of the Temporam API for temporary email services, based on the official API documentation.

## Base URL
`https://api.temporam.com/v1`

## Authentication
All API requests require authentication via an API Key. The API Key must be included in the `Authorization` header as a Bearer token.

**Header Format:**
`Authorization: Bearer YOUR_API_KEY`

**Note:** An active subscription is required. Missing or invalid API keys will result in `401` or `403` errors.

## Rate Limiting
*   **Rate limit**: 10 requests per second
*   **Quota**: Based on subscription plan (default: 100,000 requests per billing period)

## Endpoints

### 1. GET /v1/domains
**Description**: Returns a list of available email domains.
**Parameters**: None.
**Response Example (Data field)**:
```json
[
  {
    "id": "1",
    "domain": "temporam.com",
    "type": 0,
    "created_at": "2026-03-16T00:00:00.000Z"
  }
]
```

### 2. GET /v1/emails
**Description**: Returns a list of emails received by a specific email address.
**Parameters**:
*   `email` (string, Required): The full email address to query.
*   `page` (number, Optional, Default: 1): Page number for pagination.
*   `limit` (number, Optional, Default: 20, Max: 50): Number of emails per page.
**Response Example (Data field)**:
```json
[
  {
    "id": "12345",
    "created_at": "2026-03-16T12:30:00.000Z",
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "from_name": "GitHub",
    "from_email": "noreply@github.com",
    "to_name": null,
    "to_email": "user@temporam.com",
    "subject": "Verify your email address",
    "summary": "Please verify your email address by clicking...",
    "from_domain": "github.com",
    "to_domain": "temporam.com"
  }
]
```

### 3. GET /v1/emails/:id
**Description**: Returns full details of a specific email, including the email content.
**Path Parameters**:
*   `id` (string, Required): The email ID.
**Response Example (Data field)**:
```json
{
  "id": "12345",
  "createdAt": "2026-03-16T12:30:00.000Z",
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "fromName": "GitHub",
  "fromEmail": "noreply@github.com",
  "toName": null,
  "toEmail": "user@temporam.com",
  "subject": "Verify your email address",
  "content": "<html>...</html>",
  "summary": "Please verify your email address by clicking...",
  "fromDomain": "github.com",
  "toDomain": "temporam.com"
}
```

## Error Codes
Common error codes include `400` (Bad Request), `401` (Unauthorized), `403` (Forbidden), `404` (Not Found), and `429` (Too Many Requests/Quota Exceeded).