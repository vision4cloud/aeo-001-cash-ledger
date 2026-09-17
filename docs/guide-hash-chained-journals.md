# Hash-chained cash journals in ~100 lines of Python (and why spreadsheets silently lie)

If you keep a personal or micro-business cash log in a spreadsheet, you already know the failure mode: **anyone with edit access can rewrite yesterday**. Cells do not complain. Formulas still sum. The story of the money quietly changes.

Accounting software solves some of that with permissions and audit trails — at the cost of accounts, subscriptions, and ceremony you may not want for a solo experiment or a client handoff.

This guide is about a smaller idea: an **append-only cash journal** where every row cryptographically depends on the previous tip. If someone edits history, `verify` fails. No blockchain. No SaaS. One CSV. One Python file. Stdlib only.

**Free tool:** [cash-ledger](https://vision4cloud.github.io/aeo-001-cash-ledger/) (MIT) — [repo](https://github.com/vision4cloud/aeo-001-cash-ledger)

---

## What “hash-chained” means here

1. Start with a **genesis** row whose `prev_entry_hash` is sixty-four zero hex digits.
2. For each new entry, take the previous tip hash, then SHA-256 a **canonical JSON** payload of the new row’s fields (sorted keys, fixed decimal money, no fluff).
3. Store `entry_hash = SHA256(prev_entry_hash + "\n" + payload)`.
4. The next row’s `prev_entry_hash` **must** equal the prior `entry_hash`.

Change any past amount, memo, or timestamp → hashes diverge → `verify` prints `FAIL`.

This is **not** independent custody. It does not replace bank statements or audited books. It *does* make silent rewrite obvious on a laptop you control.

---

## Quick start (copy-paste)

Requirements: Python 3.9+ (no `pip install`).

```bash
# From the release zip or cash-ledger/ folder:
python3 cash_ledger.py -f my_cash.csv init --currency INR --memo "Opening journal"

python3 cash_ledger.py -f my_cash.csv add --amount 999 --direction in \
  --type SALE --counterparty customer_001 --memo "Ledger setup gig"

python3 cash_ledger.py -f my_cash.csv add --amount 50 --direction out \
  --type EXPENSE --counterparty vendor_x --memo "Domain renewal"

python3 cash_ledger.py -f my_cash.csv verify
python3 cash_ledger.py -f my_cash.csv tip
python3 cash_ledger.py -f my_cash.csv balance
```

| Command | Purpose |
|---------|---------|
| `init` | Create ledger + genesis |
| `add` | Append a chained entry |
| `verify` | Recompute the whole chain |
| `tip` | Show current tip hash |
| `balance` | Sum cash effects (verify first) |

See also [EXAMPLES.md](../cash-ledger/EXAMPLES.md) for a short sample workflow.

---

## A tiny mental model

Think of the CSV as a **tamper-evident notebook**:

- Spreadsheets optimize for *editing*.
- Hash chains optimize for *append + proof*.

When you hand a client a starter ledger, they can keep adding rows and periodically run `verify`. If a file “comes back different,” the chain says so without arguing about who edited cell B14.

Useful for:

- Solo operators / side projects who want integrity without QuickBooks
- Experiment logs where rewriting history is a bug, not a feature
- Handing someone a starter journal they keep verifying locally

---

## Honest scope (what this is not)

- Not a payment processor
- Not tax advice
- Not a substitute for regulated accounting when you need it
- Not “AI will make you rich” content

If you need a one-off **cleanup script**, **ledger setup**, or **spreadsheet automation**, fixed-price micro-scripts are available as an India-based solo offer — no fake testimonials, no retainers, clear deliverables:

| Tier | What | Price |
|------|------|------:|
| A | CSV/sheet cleanup script | ₹499 |
| B | `cash-ledger` setup for your workflow | ₹999 |
| C | Fixed-scope import→transform→export automation | ₹2499 |

Details: **[offer page](https://vision4cloud.github.io/aeo-001-cash-ledger/)** · order via [GitHub Issue](https://github.com/vision4cloud/aeo-001-cash-ledger/issues/new).

Payment settles on **owner-held** rails after written scope — do not send bank PINs, OTPs, or CVVs. If you only want the free CLI, take it and ignore the tiers. That is a success outcome.

---

## Try the integrity check yourself

1. `init` a ledger and `add` two rows.
2. Run `verify` → expect `PASS`.
3. Open the CSV in a text editor and change an old `amount`.
4. Run `verify` again → expect `FAIL`.

That five-minute exercise teaches more than a paragraph of theory.

---

## Links

- Landing + offers: https://vision4cloud.github.io/aeo-001-cash-ledger/
- Guide (this page): https://vision4cloud.github.io/aeo-001-cash-ledger/guide-hash-chained-journals.html *(raw markdown also at `/docs/guide-hash-chained-journals.md`)*
- Source / zip: https://github.com/vision4cloud/aeo-001-cash-ledger

*Built as a $0-capex experiment. Tool stays free/MIT either way.*
