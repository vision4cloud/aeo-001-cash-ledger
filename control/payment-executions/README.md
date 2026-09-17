# Payment executions

Actual payment-execution results for OWNER-CAPITAL-REQUESTs (same REQUEST_ID as `control/capital-requests/` and `control/capital-decisions/`).

- Path: `control/payment-executions/<REQUEST_ID>.json`
- Capital approval alone is **not** payment
- Absence of an execution file means funds were **NOT** deployed
- Only a successful terminal status confirms deployment
- **SANDBOX** records = zero real-money and zero economic effect (never count as capital, spend, revenue, profit, or seed recovery)
- Continue unrelated lawful work while pending
- Never store banking credentials, API secrets, PIN, OTP, CVV, passwords, recovery codes, or private keys
