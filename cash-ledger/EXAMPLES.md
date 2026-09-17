# cash-ledger — sample workflow

Short conversion-friendly walkthrough. Stdlib Python 3.9+ only.

## 1. Init a journal (INR)

```bash
python3 cash_ledger.py -f demo_cash.csv init --currency INR --memo "Demo opening"
```

Expect a genesis row and a tip hash printed.

## 2. Record two cash moves

```bash
# Inflow
python3 cash_ledger.py -f demo_cash.csv add --amount 999 --direction in \
  --type SALE --counterparty acme_client --memo "Tier B ledger setup"

# Outflow
python3 cash_ledger.py -f demo_cash.csv add --amount 50 --direction out \
  --type EXPENSE --counterparty registrar --memo "Domain renewal"
```

## 3. Verify + tip + balance

```bash
python3 cash_ledger.py -f demo_cash.csv verify   # expect PASS
python3 cash_ledger.py -f demo_cash.csv tip
python3 cash_ledger.py -f demo_cash.csv balance  # net should reflect +999 -50
```

## 4. Prove tamper detection (optional)

1. Open `demo_cash.csv` in a text editor.
2. Change an old `amount` (or memo) on a non-genesis row.
3. Run `verify` again → expect **FAIL**.

That is the product promise in one minute: silent spreadsheet rewrites become loud.

## 5. Starter file

Copy `starter_ledger.csv` if you want a pre-made genesis, or always `init` fresh.

## Next steps

- Longer explainer: [guide (HTML)](https://vision4cloud.github.io/aeo-001-cash-ledger/guide-hash-chained-journals.html) · [markdown](../docs/guide-hash-chained-journals.md)
- Landing / tiers: https://vision4cloud.github.io/aeo-001-cash-ledger/
- Order / questions: https://github.com/vision4cloud/aeo-001-cash-ledger/issues/new?template=order.yml
- Pages sample workflow: https://vision4cloud.github.io/aeo-001-cash-ledger/examples.html
