# cash-ledger

Tiny, dependency-free **append-only SHA-256 hash-chained** personal/business cash journal.

One Python file. One CSV. A `verify` command that proves the chain has not been silently rewritten.

## Why

Spreadsheets are easy to edit after the fact. `cash-ledger` makes every row cryptographically depend on the previous tip, so rewriting history fails `verify`.

Useful for:

- Solo operators / side projects who want a tamper-evident cash journal
- Experiment logs where you need integrity without a full accounting suite
- Handing a client a starter ledger they can keep verifying locally

## Requirements

- Python 3.9+ (stdlib only — no pip install)

## Quick start

```bash
# Initialize a new ledger (INR by default; Asia/Kolkata local timestamps)
python3 cash_ledger.py -f my_cash.csv init --currency INR --memo "Opening journal"

# Record an inflow
python3 cash_ledger.py -f my_cash.csv add --amount 499 --direction in \
  --type SALE --counterparty customer_001 --memo "Micro-automation gig"

# Record an outflow
python3 cash_ledger.py -f my_cash.csv add --amount 50 --direction out \
  --type EXPENSE --counterparty vendor_x --memo "Domain renewal"

# Verify the chain
python3 cash_ledger.py -f my_cash.csv verify

# Show tip hash / balances
python3 cash_ledger.py -f my_cash.csv tip
python3 cash_ledger.py -f my_cash.csv balance
```

## Commands

| Command | Purpose |
|---------|---------|
| `init` | Create ledger with `GENESIS` row (64-zero previous hash) |
| `add` | Append entry; auto-chains from tip |
| `verify` | Recompute all hashes; print `PASS` or `FAIL` |
| `tip` | Print current tip `entry_hash` |
| `balance` | Sum `cash_effect` by currency (runs verify first) |

## CSV schema

`entry_id, timestamp_utc, timestamp_local, entry_type, counterparty, currency, amount, cash_effect, memo, evidence_ref, prev_entry_hash, entry_hash`

- `amount` — absolute magnitude (always ≥ 0)
- `cash_effect` — signed business cash movement (`+` in, `-` out)
- Hash input = `prev_entry_hash + "\n" + canonical JSON` of all non-hash fields (8-decimal money, sorted keys)

## Integrity model

1. Genesis `prev_entry_hash` = 64 zero hex digits.
2. Each `entry_hash` = SHA-256 hex of `prev_entry_hash || "\n" || canonical_payload`.
3. `verify` walks the chain; any edit to a past row breaks subsequent hashes.

This is **not** a substitute for independent custody, bank statements, or audited books. It is a local tamper-evident journal.

## Starter file

`starter_ledger.csv` ships as a verified empty genesis you can copy, or run `init` yourself.

## License

MIT — use freely; no warranty.
