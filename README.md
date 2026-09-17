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

## Paid micro-automation offers

See [OFFER.md](./OFFER.md) (₹499 / ₹999 / ₹2499). Landing page: GitHub Pages `/docs`.

## License

MIT — see [LICENSE](./LICENSE).
