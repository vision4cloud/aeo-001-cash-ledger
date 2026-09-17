# Capital decisions

Machine-readable OpenClaw decisions for AEO-001 capital requests.

- Path: `control/capital-decisions/<REQUEST_ID>.json`
- Absence of a decision is never approval.
- `POLICY_APPROVED_PENDING_PAYMENT_RAIL` is not proof of payment.
- Spending may occur only after a separate payment-execution confirmation.
- No secrets belong in these files.
