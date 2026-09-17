# cash-ledger (AEO-001 EX-001)

Append-only SHA-256 hash-chained personal/business cash journal (Python stdlib CLI).

## Quick start

```bash
python3 cash-ledger/cash_ledger.py -f ledger.csv init
python3 cash-ledger/cash_ledger.py -f ledger.csv add --amount 10.00 --currency INR --note "seed"
python3 cash-ledger/cash_ledger.py -f ledger.csv verify
```

## Download

See [Releases](https://github.com/vision4cloud/aeo-001-cash-ledger/releases) for `cash-ledger-v1.0.0.zip`.

## Docs

- [Guide: hash-chained cash journals](./docs/guide-hash-chained-journals.md)
- [Sample workflow](./cash-ledger/EXAMPLES.md)
- [Live offer page](https://vision4cloud.github.io/aeo-001-cash-ledger/)
- [FAQ (order & payment)](./docs/FAQ.md)

## Paid micro-automation offers

Fixed one-off tiers: **₹499 / ₹999 / ₹2499** — see [OFFER.md](./OFFER.md).

**How to order:** open a [GitHub Issue (order template)](https://github.com/vision4cloud/aeo-001-cash-ledger/issues/new?template=order.yml), agree written scope, then pay via receive-only UPI `9910990086@indie` (include the Issue URL in the UPI note). Revenue counted only after settlement. Do not send PIN/OTP/CVV/passwords.

## License

MIT — see [LICENSE](./LICENSE).
