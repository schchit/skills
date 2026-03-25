---
name: temporam-temp-mail
version: 1.0.0
author: Temporam
description: "Provides temporary email receiving functionality using the Temporam API. Use for: generating temporary email addresses, listing emails for a given address, and retrieving the content of specific emails."
---

# Temporam Temporary Mail Skill

This skill enables Manus to interact with the Temporam API to manage temporary email addresses. It can generate new email addresses, check for incoming mail, and retrieve email content, which is useful for tasks requiring email verification or temporary communication.

## Capabilities

- **Generate Temporary Email Address**: Automatically creates a new, unique email address using an available domain from the Temporam service.
- **List Emails**: Retrieves a list of emails received by a specified temporary email address.
- **Get Email Content**: Fetches the full content of a specific email using its ID.

## Usage Instructions

### Prerequisites

To use this skill, you must have a valid Temporam API Key. Set it as an environment variable named `TEMPORAM_API_KEY` in the sandbox environment before invoking any functions from this skill.

```bash
export TEMPORAM_API_KEY="YOUR_API_KEY"
```

### Generating a Temporary Email Address

To generate a new temporary email address, use the `generate_random_email` function from the `client.py` script. Manus will automatically select an available domain.

**Example Prompt:**

"请帮我生成一个临时的邮箱地址。"

**Internal Action (Manus will execute):**

```python
from skills.temporam-temp-mail.scripts.client import TemporamClient

client = TemporamClient()
email_address = client.generate_random_email()
print(f"Generated temporary email: {email_address}")
```

### Listing Emails for an Address

To list emails received by a specific temporary email address, use the `list_emails` function. You can specify pagination parameters if needed.

**Example Prompt:**

"查看 `test@example.com` 这个邮箱收到了哪些邮件。"

**Internal Action (Manus will execute):**

```python
from skills.temporam-temp-mail.scripts.client import TemporamClient

client = TemporamClient()
email_address = "test@example.com" # Replace with the actual email address
emails = client.list_emails(email_address, page=1, limit=10)
for email in emails:
    print(f"Subject: {email["subject"]}, From: {email["from_email"]}")
```

### Getting Specific Email Content

To retrieve the full content of a particular email, provide the email ID to the `get_email_detail` function.

**Example Prompt:**

"获取 ID 为 `12345` 的邮件内容。"

**Internal Action (Manus will execute):**

```python
from skills.temporam-temp-mail.scripts.client import TemporamClient

client = TemporamClient()
email_id = "12345" # Replace with the actual email ID
email_detail = client.get_email_detail(email_id)
if email_detail:
    print(f"Email Subject: {email_detail["subject"]}")
    print(f"Email Content: {email_detail["content"]}")
```

## Workflow Example: Email Verification

When a task requires email verification, Manus can perform the following steps:

1.  Generate a temporary email address.
2.  Provide this email address to the service requiring verification.
3.  Periodically call `list_emails` to check for new emails.
4.  Once a verification email is received, extract the verification link or code using `get_email_detail`.
5.  Complete the verification process.

## References

- [Temporam API Reference](https://www.temporam.com/docs/api-reference) [1]

[1]: https://www.temporam.com/docs/api-reference "Temporam API Reference"