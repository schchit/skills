# Validation Rules

## Arithmetic Checks
1. **lineItemSum** — Sum of lineTotal values must match netTotal (±0.02 tolerance)
2. **vatCalculation** — Per-line: lineTotal × vatRate/100 must match expected VAT
3. **grossEqualsNetPlusVat** — netTotal + vatTotal must equal grossTotal (±0.02)

## Document Classification (9 types)
invoice, credit-note, receipt, purchase-order, delivery-note, confirmation, statement, other-financial, not-financial

### Accept Modes
- **strict**: invoice, credit-note only
- **relaxed** (default): + receipt, proforma
- **any**: extract from all, classify only

## Business Rules (15)
1. Missing invoice number
2. Missing invoice date
3. Missing supplier name
4. Missing buyer name
5. Missing currency
6. Future invoice date (>7 days ahead)
7. Due date before invoice date
8. Suspicious invoice number (too short, placeholder patterns)
9. Receipt signals on invoice (till number, transaction ID, card ending)
10. No line items extracted
11. Line items without amounts
12. Missing VAT when VAT numbers present
13. Missing payment information (no terms, no bank, no reference)
14. Unusually high confidence with many missing fields
15. Currency mismatch between header and line items

## Amount Due / Amount Paid Checks
16. amountDue should equal grossTotal - amountPaid (±0.02 tolerance) when all three are present
17. amountPaid should not exceed grossTotal (warning, not error — overpayments/credits exist)

## Quality Score
- Count present key fields: invoiceNumber, invoiceDate, supplierName, buyerName, currency, netTotal, vatTotal, grossTotal, lineItems (≥1)
- Score = present / 9
- Rating: ≥0.8 = good, ≥0.5 = partial, <0.5 = poor
