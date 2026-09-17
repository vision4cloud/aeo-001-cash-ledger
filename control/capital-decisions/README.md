# Capital decisions (OpenClaw)

Authoritative decisions for OWNER-CAPITAL-REQUESTs mirrored under `control/capital-requests/`.

- Path: `control/capital-decisions/<REQUEST_ID>.json` (same REQUEST_ID)
- Absence of a decision is **NOT** approval
- `REJECTED_INVALID` → do not spend
- `OWNER_REQUIRED` → do not spend; continue unrelated lawful work
- `POLICY_APPROVED_PENDING_PAYMENT_RAIL` → policy eligibility only; **NOT** funds deployed
- Do not spend merely because a request or policy approval exists
- Only a future explicit payment-execution confirmation counts as funds actually deployed
- Never store secrets here
