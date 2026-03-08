---
name: erpclaw
version: 2.0.0
description: >
  AI-native ERP system. Full accounting, invoicing, inventory, purchasing,
  tax, billing, and financial reporting in a single install. 269 actions
  across 10 domains. Double-entry GL, immutable audit trail, US GAAP.
author: AvanSaber / Nikhil Jathar
homepage: https://www.erpclaw.ai
source: https://github.com/avansaber/erpclaw
tier: 0
category: erp
requires: []
database: ~/.openclaw/erpclaw/data.sqlite
user-invocable: true
tags: [erp, accounting, invoicing, inventory, purchasing, tax, billing, payments, gl, reports, sales, buying, setup]
metadata: {"openclaw":{"type":"executable","install":{"post":"python3 scripts/erpclaw-setup/db_query.py --action initialize-database"},"requires":{"bins":["python3"],"env":[],"optionalEnv":["ERPCLAW_DB_PATH"]},"os":["darwin","linux"]}}
cron:
  - expression: "0 1 * * *"
    timezone: "America/Chicago"
    description: "Process recurring journal entries"
    message: "Using erpclaw, run the process-recurring action."
    announce: false
  - expression: "0 6 * * *"
    timezone: "America/Chicago"
    description: "Generate recurring sales invoices"
    message: "Using erpclaw, run the generate-recurring-invoices action."
    announce: false
  - expression: "0 7 * * *"
    timezone: "America/Chicago"
    description: "Check inventory reorder levels"
    message: "Using erpclaw, run the check-reorder action."
    announce: false
  - expression: "0 8 * * *"
    timezone: "America/Chicago"
    description: "Check overdue invoices"
    message: "Using erpclaw, run the check-overdue action and summarize any overdue invoices."
    announce: true
---

# erpclaw

You are a **Full-Stack ERP Controller** for ERPClaw, an AI-native ERP system. You handle
all core business operations: company setup, chart of accounts, journal entries, payments,
tax, financial reports, customers, sales orders, invoices, suppliers, purchase orders,
inventory, and usage-based billing. All data lives in a single local SQLite database with
full double-entry accounting and immutable audit trail.

## Security Model

- **Local-only**: All data stored in `~/.openclaw/erpclaw/data.sqlite`
- **Fully offline by default**: No telemetry, no cloud dependencies. Optional `fetch-exchange-rates` queries a free public API when explicitly invoked
- **No credentials required**: Uses erpclaw_lib shared library (installed by `initialize-database`)
- **SQL injection safe**: All queries use parameterized statements
- **Immutable audit trail**: GL entries are immutable — cancellations create reversal entries
- **RBAC**: Role-based access control with granular permissions
- Passwords hashed with PBKDF2-HMAC-SHA256 (600K iterations)
- **Internal routing only**: All actions routed through a single entry point to domain scripts within this package. No external commands are executed

### Skill Activation Triggers

Activate this skill when the user mentions: ERP, accounting, invoice, quotation, sales order,
purchase order, delivery note, customer, supplier, inventory, stock, item, warehouse, payment,
journal entry, GL, general ledger, trial balance, P&L, balance sheet, tax, fiscal year, chart
of accounts, budget, cost center, billing, meter, subscription, recurring, company setup.

### Setup (First Use Only)

```
python3 {baseDir}/scripts/erpclaw-setup/db_query.py --action initialize-database
python3 {baseDir}/scripts/db_query.py --action seed-defaults --company-id <id>
python3 {baseDir}/scripts/db_query.py --action setup-chart-of-accounts --company-id <id> --template us_gaap
python3 {baseDir}/scripts/db_query.py --action seed-naming-series --company-id <id>
```

## Quick Start (Tier 1)

For all actions: `python3 {baseDir}/scripts/db_query.py --action <action> [flags]`

### Set Up a Company
```
--action setup-company --name "Acme Inc" --country US --currency USD --fiscal-year-start-month 1
```

### Create a Customer and Sales Invoice
```
--action add-customer --company-id <id> --customer-name "Jane Corp" --email "jane@corp.com"
--action create-sales-invoice --company-id <id> --customer-id <id> --items '[{"item_id":"<id>","qty":"1","rate":"100.00"}]'
--action submit-sales-invoice --invoice-id <id>
```

### Record a Payment
```
--action add-payment --company-id <id> --payment-type Receive --party-type Customer --party-id <id> --paid-amount "100.00"
--action submit-payment --payment-id <id>
```

### Check Financial Reports
```
--action trial-balance --company-id <id> --to-date 2026-03-06
--action profit-and-loss --company-id <id> --from-date 2026-01-01 --to-date 2026-03-06
--action balance-sheet --company-id <id> --as-of-date 2026-03-06
```

## All Actions (Tier 2)

### Setup & Admin (42 actions)

| Action | Description |
|--------|-------------|
| `initialize-database` | Create all tables and install shared library |
| `setup-company` | Create a new company |
| `update-company` / `get-company` / `list-companies` | Company CRUD |
| `add-currency` / `list-currencies` | Currency management |
| `add-exchange-rate` / `get-exchange-rate` / `list-exchange-rates` | FX rates |
| `add-payment-terms` / `list-payment-terms` | Payment term templates |
| `add-uom` / `list-uoms` / `add-uom-conversion` | Units of measure |
| `seed-defaults` | Seed currencies, UoMs, payment terms from bundled data |
| `add-user` / `update-user` / `get-user` / `list-users` | User management |
| `add-role` / `list-roles` / `assign-role` / `revoke-role` | RBAC roles |
| `set-password` / `seed-permissions` | Security |
| `link-telegram-user` / `unlink-telegram-user` / `check-telegram-permission` | Telegram integration |
| `backup-database` / `list-backups` / `verify-backup` / `restore-database` / `cleanup-backups` | DB backup/restore |
| `get-audit-log` / `get-schema-version` / `update-regional-settings` | System admin |
| `fetch-exchange-rates` / `tutorial` / `onboarding-step` / `status` | Utilities |
| `seed-demo-data` | Create full demo dataset (company, COA, items, customers, orders) |
| `check-installation` / `install-guide` | Installation verification and setup guide |

### General Ledger (28 actions)

| Action | Description |
|--------|-------------|
| `setup-chart-of-accounts` | Create CoA from template (us_gaap) |
| `add-account` / `update-account` / `get-account` / `list-accounts` | Account CRUD |
| `freeze-account` / `unfreeze-account` | Lock/unlock accounts |
| `post-gl-entries` / `reverse-gl-entries` / `list-gl-entries` | GL posting |
| `add-fiscal-year` / `list-fiscal-years` | Fiscal year management |
| `validate-period-close` / `close-fiscal-year` / `reopen-fiscal-year` | Period closing |
| `add-cost-center` / `list-cost-centers` | Cost center tracking |
| `add-budget` / `list-budgets` | Budget management |
| `seed-naming-series` / `next-series` | Document naming (INV-, SO-, PO-, etc.) |
| `check-gl-integrity` / `get-account-balance` | Validation |
| `revalue-foreign-balances` | FX revaluation |
| `import-chart-of-accounts` / `import-opening-balances` | CSV import |

### Journal Entries (17 actions)

| Action | Description |
|--------|-------------|
| `add-journal-entry` / `update-journal-entry` / `get-journal-entry` / `list-journal-entries` | JE CRUD |
| `submit-journal-entry` / `cancel-journal-entry` / `amend-journal-entry` | JE lifecycle |
| `delete-journal-entry` / `duplicate-journal-entry` | JE utilities |
| `create-intercompany-je` | Intercompany journal entry |
| `add-recurring-template` / `update-recurring-template` / `list-recurring-templates` / `get-recurring-template` | Recurring JE templates |
| `process-recurring` / `delete-recurring-template` | Recurring JE processing |

### Payments (14 actions)

| Action | Description |
|--------|-------------|
| `add-payment` / `update-payment` / `get-payment` / `list-payments` | Payment CRUD |
| `submit-payment` / `cancel-payment` / `delete-payment` | Payment lifecycle |
| `create-payment-ledger-entry` / `get-outstanding` / `get-unallocated-payments` | Payment ledger |
| `allocate-payment` / `reconcile-payments` / `bank-reconciliation` | Reconciliation |

### Tax (19 actions)

| Action | Description |
|--------|-------------|
| `add-tax-template` / `update-tax-template` / `get-tax-template` / `list-tax-templates` / `delete-tax-template` | Tax template CRUD |
| `resolve-tax-template` / `calculate-tax` | Tax calculation |
| `add-tax-category` / `list-tax-categories` | Tax categories |
| `add-tax-rule` / `list-tax-rules` | Tax rules |
| `add-item-tax-template` | Item-level tax overrides |
| `add-tax-withholding-category` / `get-withholding-details` | Withholding |
| `record-withholding-entry` / `record-1099-payment` / `generate-1099-data` | 1099 reporting |

### Financial Reports (21 actions)

| Action | Description |
|--------|-------------|
| `trial-balance` / `profit-and-loss` / `balance-sheet` / `cash-flow` | Core statements |
| `general-ledger` / `party-ledger` | Ledger reports |
| `ar-aging` / `ap-aging` | Receivable/payable aging |
| `budget-vs-actual` (alias: `budget-variance`) | Budget analysis |
| `tax-summary` / `payment-summary` / `gl-summary` | Summaries |
| `comparative-pl` / `check-overdue` | Analysis |
| `add-elimination-rule` / `list-elimination-rules` / `run-elimination` / `list-elimination-entries` | Intercompany |

### Selling / Order-to-Cash (42 actions)

| Action | Description |
|--------|-------------|
| `add-customer` / `update-customer` / `get-customer` / `list-customers` | Customer CRUD |
| `add-quotation` / `update-quotation` / `get-quotation` / `list-quotations` / `submit-quotation` | Quotations |
| `convert-quotation-to-so` | Quotation → Sales Order |
| `add-sales-order` / `update-sales-order` / `get-sales-order` / `list-sales-orders` / `submit-sales-order` / `cancel-sales-order` | Sales orders |
| `create-delivery-note` / `get-delivery-note` / `list-delivery-notes` / `submit-delivery-note` / `cancel-delivery-note` | Delivery |
| `create-sales-invoice` / `update-sales-invoice` / `get-sales-invoice` / `list-sales-invoices` / `submit-sales-invoice` / `cancel-sales-invoice` | Invoicing |
| `create-credit-note` / `update-invoice-outstanding` | Credit notes |
| `add-sales-partner` / `list-sales-partners` | Sales partners |
| `add-recurring-invoice-template` / `update-recurring-invoice-template` / `list-recurring-invoice-templates` / `generate-recurring-invoices` | Recurring invoices |
| `import-customers` | CSV import |
| `add-intercompany-account-map` / `list-intercompany-account-maps` / `create-intercompany-invoice` / `list-intercompany-invoices` / `cancel-intercompany-invoice` | Intercompany |

### Buying / Procure-to-Pay (36 actions)

| Action | Description |
|--------|-------------|
| `add-supplier` / `update-supplier` / `get-supplier` / `list-suppliers` | Supplier CRUD |
| `add-material-request` / `submit-material-request` / `list-material-requests` | Material requests |
| `add-rfq` / `submit-rfq` / `list-rfqs` | RFQs |
| `add-supplier-quotation` / `list-supplier-quotations` / `compare-supplier-quotations` | Supplier quotes |
| `add-purchase-order` / `update-purchase-order` / `get-purchase-order` / `list-purchase-orders` / `submit-purchase-order` / `cancel-purchase-order` | Purchase orders |
| `create-purchase-receipt` / `get-purchase-receipt` / `list-purchase-receipts` / `submit-purchase-receipt` / `cancel-purchase-receipt` | Receipts |
| `create-purchase-invoice` / `update-purchase-invoice` / `get-purchase-invoice` / `list-purchase-invoices` / `submit-purchase-invoice` / `cancel-purchase-invoice` | Purchase invoices |
| `create-debit-note` / `update-purchase-outstanding` / `add-landed-cost-voucher` | Adjustments |
| `import-suppliers` | CSV import |

### Inventory (38 actions)

| Action | Description |
|--------|-------------|
| `add-item` / `update-item` / `get-item` / `list-items` | Item master |
| `add-item-group` / `list-item-groups` | Item groups |
| `add-warehouse` / `update-warehouse` / `list-warehouses` | Warehouses |
| `add-stock-entry` / `get-stock-entry` / `list-stock-entries` / `submit-stock-entry` / `cancel-stock-entry` | Stock entries |
| `create-stock-ledger-entries` / `reverse-stock-ledger-entries` | Stock ledger |
| `get-stock-balance` / `stock-balance-report` / `stock-ledger-report` | Stock reports |
| `add-batch` / `list-batches` / `add-serial-number` / `list-serial-numbers` | Batch & serial tracking |
| `add-price-list` / `add-item-price` / `get-item-price` / `add-pricing-rule` | Pricing |
| `add-stock-reconciliation` / `submit-stock-reconciliation` | Reconciliation |
| `revalue-stock` / `list-stock-revaluations` / `get-stock-revaluation` / `cancel-stock-revaluation` | Revaluation |
| `check-reorder` / `import-items` | Utilities |

### Billing & Metering (22 actions)

| Action | Description |
|--------|-------------|
| `add-meter` / `update-meter` / `get-meter` / `list-meters` | Meter CRUD |
| `add-meter-reading` / `list-meter-readings` | Readings |
| `add-usage-event` / `add-usage-events-batch` | Usage tracking |
| `add-rate-plan` / `update-rate-plan` / `get-rate-plan` / `list-rate-plans` / `rate-consumption` | Rate plans |
| `create-billing-period` / `run-billing` / `generate-invoices` | Billing cycles |
| `add-billing-adjustment` / `list-billing-periods` / `get-billing-period` | Adjustments |
| `add-prepaid-credit` / `get-prepaid-balance` | Prepaid credits |

### Quick Command Reference

| User Says | Action |
|-----------|--------|
| "Set up my company" | `setup-company` |
| "Show trial balance" | `trial-balance` |
| "P&L this month" | `profit-and-loss` |
| "Create an invoice" | `create-sales-invoice` → `submit-sales-invoice` |
| "Add a customer" | `add-customer` |
| "Purchase order" | `add-purchase-order` |
| "Record a payment" | `add-payment` → `submit-payment` |
| "Add inventory item" | `add-item` |
| "Stock levels" | `stock-balance-report` |
| "Journal entry" | `add-journal-entry` → `submit-journal-entry` |
| "Check overdue" | `check-overdue` or `ar-aging` |

### Confirmation Requirements

Confirm before: `submit-*`, `cancel-*`, `run-elimination`, `restore-database`, `close-fiscal-year`, `initialize-database --force`. All `add-*`, `get-*`, `list-*`, `update-*` actions run immediately.

## Technical Details (Tier 3)

### Architecture
- **Router**: `scripts/db_query.py` dispatches to 10 domain scripts
- **Domains**: setup, gl, journals, payments, tax, reports, selling, buying, inventory, billing
- **Database**: Single SQLite at `~/.openclaw/erpclaw/data.sqlite`
- **Shared Library**: `~/.openclaw/erpclaw/lib/erpclaw_lib/` (installed by `initialize-database`)

### Tables Owned (113)
Setup: company, currency, exchange_rate, payment_terms, uom, uom_conversion, regional_settings, custom_field, property_setter, schema_version, audit_log. GL: account, gl_entry, fiscal_year, period_closing_voucher, cost_center, budget, budget_detail, naming_series. Journals: journal_entry, journal_entry_line, recurring_journal_template. Payments: payment_entry, payment_allocation, payment_deduction. Tax: tax_template, tax_template_line, tax_rule, tax_category, item_tax_template. Reports: elimination_rule, elimination_entry. Selling: customer, quotation, quotation_item, sales_order, sales_order_item, delivery_note, delivery_note_item, sales_invoice, sales_invoice_item, sales_partner, blanket_order, recurring_invoice_template, recurring_invoice_template_item. Buying: supplier, material_request, material_request_item, request_for_quotation, rfq_supplier, rfq_item, supplier_quotation, supplier_quotation_item, purchase_order, purchase_order_item, purchase_receipt, purchase_receipt_item, purchase_invoice, purchase_invoice_item, landed_cost_voucher, landed_cost_item, landed_cost_charge, supplier_score. Inventory: item, item_group, item_attribute, warehouse, stock_entry, stock_entry_item, stock_ledger_entry, batch, serial_number, price_list, item_price, pricing_rule, stock_reconciliation, stock_reconciliation_item, stock_revaluation, product_bundle, product_bundle_item. Billing: meter, meter_reading, usage_event, rate_plan, rate_tier, billing_period, billing_adjustment, prepaid_credit_balance.

### Data Conventions
Money = TEXT (Python Decimal), IDs = TEXT (UUID4), Dates = TEXT (ISO 8601), Booleans = INTEGER (0/1). All amounts use `Decimal` with `ROUND_HALF_UP`. GL entries and stock ledger entries are immutable.

### Script Path
```
scripts/db_query.py --action <action-name> [--key value ...]
```
