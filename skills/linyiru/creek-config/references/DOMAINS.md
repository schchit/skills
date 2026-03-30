# Custom Domain Setup

## Steps

1. **Add the domain**:
   ```bash
   creek domains add app.example.com
   ```

2. **Configure DNS** at your DNS provider:
   - **CNAME record**: `app.example.com` → `cname.creek.dev`
   - Or use a **TXT record** for verification: `_creek.app.example.com` → `<verification-token>`

3. **Activate the domain**:
   ```bash
   creek domains activate app.example.com
   ```
   This provisions an SSL certificate automatically.

## Domain Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Waiting for DNS configuration |
| `provisioning` | SSL certificate being provisioned |
| `active` | Domain is live with SSL |
| `failed` | DNS misconfigured — verify CNAME record |

## Per-Project Domains

Use `--project` to manage domains for a specific project:

```bash
creek domains add app.example.com --project my-app
creek domains ls --project my-app
```
