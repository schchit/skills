---
name: rapay
description: Send compliant fiat USD payments via Ra Pay CLI — the first CLI-native AI payment platform
homepage: https://rapay.ai
user-invocable: true
metadata: {"openclaw": {"emoji": "💸", "requires": {"bins": ["node", "npm"]}, "os": ["darwin", "linux", "win32"], "install": [{"node": "@rapay/cli"}]}}
---

# Ra Pay — AI-Native Fiat Payments

Ra Pay is the first CLI-native payment platform built for AI agents. It lets you send compliant fiat USD payments using simple CLI commands. Every payment goes through Stripe's regulated infrastructure with full compliance screening.

**This skill teaches you how to use the Ra Pay CLI to send business payments on behalf of your user.**

**Need to pay or get paid by another agent?** If the other party doesn't have Ra Pay, see the Transaction Protocol and shareable onboarding scripts at the bottom of this file — they let you onboard the other agent without them needing this skill.

## Installation

```bash
npm install -g @rapay/cli
```

Verify installation:

```bash
ra --version
```

Expected output: `ra-cli 1.5.0` or later.

## One-Time Setup

Before sending payments, the user must complete account setup. The steps depend on whether they want to **send**, **receive**, or **both**.

### Setup Paths

| Goal | Required Command | What It Does |
|------|-----------------|--------------|
| **Send payments** | `ra add-card` | Saves a credit card via Stripe Checkout (no bank account needed) |
| **Receive payments** | `ra link-bank` | Connects a bank account via Stripe Connect (for payouts) |
| **Both** | `ra add-card` + `ra link-bank` | Full sender + receiver setup |

### To Send: Add a Credit Card

```bash
ra add-card
```

This opens a Stripe Checkout page in the browser where the user securely saves a credit card. Once complete, the card is stored with Stripe (not locally) and payments can be sent immediately. No bank account or Stripe Connect onboarding is needed to send.

### To Receive: Link a Bank Account

```bash
ra link-bank
```

This opens a Stripe-hosted flow in the browser where the user connects their bank account via Stripe Connect. Once complete, the CLI stores the session locally. This is required to **receive** payments — senders do not need this step.

To reconnect an existing verified account:

```bash
ra link-bank --account acct_XXXXXXXXX
```

### Accept Terms of Service

```bash
ra accept-tos
```

The user must accept Ra Pay's Terms of Service before sending any payments.

Check TOS status at any time:

```bash
ra tos-status
```

### Verify Account

```bash
ra whoami
```

Confirm the account shows as linked and verified before proceeding with payments.

## Sending Payments

Ra Pay uses a **two-step confirmation flow** for every payment. This is mandatory — never skip the preview step.

### Step 1: Preview the Payment

```bash
ra send <AMOUNT> USD to <RECIPIENT_ID> --for "<BUSINESS_PURPOSE>" --json
```

Example:

```bash
ra send 150 USD to acct_1A2B3C4D5E --for "Logo design work - Invoice #427" --json
```

This returns a fee breakdown without executing the payment:

```json
{
  "status": "preview",
  "amount": 150.00,
  "currency": "USD",
  "recipient": "acct_1A2B3C4D5E",
  "fee": 3.00,
  "recipient_receives": 147.00,
  "business_purpose": "Logo design work - Invoice #427"
}
```

### Step 2: Show the Preview and Get User Approval

**You MUST show the fee breakdown to the user and ask for explicit confirmation before proceeding.** Never auto-confirm a payment.

Present the details clearly:
- Amount charged: $150.00
- Ra Pay fee (2%): $3.00
- Recipient receives: $147.00
- Recipient: acct_1A2B3C4D5E
- Purpose: Logo design work - Invoice #427

### Step 3: Execute the Payment

Only after the user explicitly confirms, add the `--confirm` flag:

```bash
ra send 150 USD to acct_1A2B3C4D5E --for "Logo design work - Invoice #427" --json --confirm
```

The `--confirm` flag executes the payment. Without it, you always get a preview.

### Amount Rules

- Minimum payment: $1.00
- Currency: USD only
- Recipients must be valid Stripe connected accounts (format: `acct_` followed by alphanumeric characters)

## Business Purpose Requirements

Ra Pay is a **business-to-business payment platform**. Every payment requires a `--for` flag with a legitimate business purpose (10–200 characters).

### Valid Business Purposes

Good examples:
- `"Freelance development work - Invoice #123"`
- `"API consulting services - March 2026"`
- `"Logo design work"`
- `"Website hosting fees - Q1 2026"`
- `"Content writing - 5 blog posts"`

Business purposes should be specific and describe real goods or services rendered.

### Blocked Patterns — Do NOT Use These

Ra Pay will reject payments with purposes that match these categories:

**Peer-to-peer language** — Ra Pay is not for personal transfers:
- friend, family, roommate, splitting bills, payback, loan, personal reimbursement

**Gift language:**
- gift, birthday, holiday

**Money laundering red flags:**
- gift cards, prepaid cards, cryptocurrency purchase, wire transfer

**Vague or unspecific purposes:**
- "for services" (too vague — specify what services)
- "payment" (not a purpose)
- "transfer" (not a purpose)

**Gibberish or test strings:**
- Repetitive characters (e.g., "aaaaaaaaaa")
- Random letters (e.g., "asdfghjkl")
- Repeated words (e.g., "test test test")

### If a Purpose Is Rejected

Tell the user: "Ra Pay is for business transactions only. Please provide a specific business purpose describing the goods or services involved."

Help them rewrite their purpose to be specific and business-related.

## Other Commands

### Add or Update Payment Card

```bash
ra add-card
```

Opens Stripe Checkout in the browser to save or update a credit card for sending payments. The card is stored securely with Stripe, not locally.

To **remove** a saved card, use `ra dashboard` to open the Stripe Dashboard where the user can manage or delete their payment methods.

### Check Balance

```bash
ra balance --json
```

Returns current balance, pending amounts, and payout schedule.

### View Transaction History

```bash
ra history --json
```

Returns recent payments with timestamps and status. To show more transactions:

```bash
ra history --limit 50 --json
```

The `--limit` flag accepts values from 1 to 100 (default: 20 in CLI, 10 in MCP).

### Account Info

```bash
ra whoami
```

Shows user ID, Stripe account status, verification status, and account tier.

### Manage Refunds

```bash
ra refund
```

Opens the Stripe Dashboard in the browser for processing refunds. Refunds must be handled through the Stripe interface for security.

### Manage Disputes

```bash
ra dispute
```

Opens the Stripe Disputes page. Remind the user: disputes must be responded to within the given timeframe or they auto-resolve against the user.

### Open Stripe Dashboard

```bash
ra dashboard
```

Opens the full Stripe account dashboard in the browser. Use this for managing payment methods (including removing saved cards), viewing detailed transaction records, and account settings.

### Unlink Account

```bash
ra unlink
```

Disconnects the Stripe account and clears the local session.

## Using the --json Flag

Always use `--json` when calling Ra Pay commands. This returns structured JSON output that you can parse reliably instead of human-formatted text.

Commands that support `--json`:
- `ra send ... --json`
- `ra balance --json`
- `ra history --json`

## Error Handling

- **"Not linked"** — The user hasn't set up a payment method. To send, run `ra add-card`. To receive, run `ra link-bank`.
- **"TOS not accepted"** — The user needs to run `ra accept-tos`.
- **"Invalid business purpose"** — The purpose was rejected by compliance screening. Help the user write a specific, business-related purpose.
- **"Invalid recipient"** — The recipient ID must match the format `acct_` followed by alphanumeric characters.
- **"Minimum amount"** — Payment must be at least $1.00.
- **"CLI version outdated"** — The user needs to update: `npm install -g @rapay/cli`

## Important Rules

1. **Never auto-confirm payments.** Always show the fee preview and get explicit user approval.
2. **Never fabricate recipient IDs.** Only use real `acct_` IDs provided by the user.
3. **Never bypass business purpose validation.** If a purpose is rejected, help the user write a valid one.
4. **Always use `--json` for structured output.**
5. **Ra Pay credentials stay local.** Never ask users to share API keys, session tokens, or account IDs with you. Everything runs on their machine.

---

## Transaction Protocol — Coordinating Payments Between Agents

When your user wants to pay another user whose agent you can communicate with, follow this protocol. It handles the common case where the other agent has never heard of Ra Pay.

### Step 1: Check Your Own Setup

Run `ra whoami` to confirm your user has a linked account and payment method. If not, walk them through the setup steps above before proceeding.

### Step 2: Ask the Other Agent for Their Recipient ID

Message the seller/recipient agent and ask: "Does your user have a Ra Pay account? If so, what is their Stripe connected account ID? It starts with `acct_`."

### Step 3: If They Don't Have Ra Pay

If the other agent doesn't know what Ra Pay is or their user isn't set up, send them the **Seller Onboarding Script** below. Copy the entire block and send it to the other agent as a message.

### Step 4: Preview the Payment

Once you have the recipient's `acct_` ID:

```bash
ra send <AMOUNT> USD to <RECIPIENT_ACCT_ID> --for "<BUSINESS_PURPOSE>" --json
```

### Step 5: Get Your User's Approval

Show your user the full fee breakdown from the preview. **Do not proceed without explicit approval.**

### Step 6: Execute the Payment

```bash
ra send <AMOUNT> USD to <RECIPIENT_ACCT_ID> --for "<BUSINESS_PURPOSE>" --json --confirm
```

### Step 7: Confirm to the Other Agent

Send the other agent the payment confirmation JSON so they can inform their user that the payment has been received.

---

## Shareable Script — Send This to a Seller Agent

When a seller agent doesn't have Ra Pay set up, copy everything inside the fence below and send it to them as a message. It is self-contained — they do not need the Ra Pay skill installed.

```
INCOMING PAYMENT NOTIFICATION

A buyer wants to pay your user via Ra Pay (rapay.ai), a CLI-based business
payment platform that processes payments through Stripe.

To receive this payment, your user needs to complete a short one-time setup.
Please walk them through the following steps:

STEP 1 — Install the Ra Pay CLI:
  npm install -g @rapay/cli

STEP 2 — Connect a bank account to receive payouts:
  ra link-bank
  (This opens a Stripe-hosted page in the browser. Your user connects their
  bank account through Stripe — no sensitive info is entered in the terminal.)

STEP 3 — Accept the Terms of Service:
  ra accept-tos

STEP 4 — Get the account ID:
  ra whoami
  Look for the Stripe connected account ID — it starts with "acct_".

Once setup is complete, send back the acct_ ID so the buyer can complete
the payment. The funds will be deposited to your user's bank account via
Stripe's standard payout schedule.

Your user can verify their account status at any time with: ra whoami
Your user can check their balance with: ra balance --json
Your user can view received payments with: ra history --json
```

---

## Shareable Script — Send This to a Buyer Agent

When a buyer agent needs to pay your user but doesn't have Ra Pay set up, copy everything inside the fence below and send it to them as a message. Replace `YOUR_ACCT_ID_HERE` with your user's actual `acct_` ID before sending.

```
PAYMENT SETUP INSTRUCTIONS

Your user can pay via Ra Pay (rapay.ai), a CLI-based business payment platform
that processes payments through Stripe.

To send a payment, your user needs to complete a short one-time setup:

STEP 1 — Install the Ra Pay CLI:
  npm install -g @rapay/cli

STEP 2 — Add a credit card for sending payments:
  ra add-card
  (This opens a Stripe Checkout page in the browser. The card is stored
  securely with Stripe — no card details are entered in the terminal.)

STEP 3 — Accept the Terms of Service:
  ra accept-tos

STEP 4 — Send the payment:
  ra send [AMOUNT] USD to YOUR_ACCT_ID_HERE --for "[BUSINESS PURPOSE]" --json

  This will show a fee preview. Show it to your user for approval.
  Once approved, add --confirm to execute:

  ra send [AMOUNT] USD to YOUR_ACCT_ID_HERE --for "[BUSINESS PURPOSE]" --json --confirm

IMPORTANT: Always preview the payment first and get your user's explicit
approval before adding --confirm. Never auto-confirm payments.

Ra Pay charges a 2% fee on each transaction. The fee is shown in the preview.
```
