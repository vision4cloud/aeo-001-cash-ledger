#!/usr/bin/env python3
"""
cash-ledger — append-only SHA-256 hash-chained personal/business cash journal.

A tiny, dependency-free Python CLI. Entries are stored in a CSV with a
tamper-evident chain: each row's entry_hash covers prev_entry_hash + canonical
JSON of the row fields (excluding the hash columns).

Commands:
  init     Create a new ledger CSV with genesis row
  add      Append a cash journal entry
  verify   Recompute the chain and report PASS/FAIL
  tip      Print the current tip hash
  balance  Sum cash_effect by currency (informational)

License: MIT
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional

VERSION = "1.0.0"
GENESIS_PREV = "0" * 64
FIELDS = [
    "entry_id",
    "timestamp_utc",
    "timestamp_local",
    "entry_type",
    "counterparty",
    "currency",
    "amount",
    "cash_effect",
    "memo",
    "evidence_ref",
    "prev_entry_hash",
    "entry_hash",
]
MONEY = {"amount", "cash_effect"}
CANON_EXCLUDE = {"prev_entry_hash", "entry_hash"}


def d8(x: Decimal) -> str:
    return str(x.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_EVEN))


def parse_money(v: str) -> Decimal:
    try:
        return Decimal(str(v))
    except (InvalidOperation, TypeError) as e:
        raise SystemExit(f"Invalid money value: {v!r}") from e


def now_pair(tz_offset_hours: float = 5.5) -> tuple[str, str]:
    utc = datetime.now(timezone.utc).replace(microsecond=0)
    offset = timezone(timedelta(hours=tz_offset_hours))
    local = utc.astimezone(offset)
    # ISO-8601 with offset
    return (
        utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        local.isoformat(),
    )


def canonical_payload(row: Dict[str, Any]) -> str:
    obj: Dict[str, Any] = {}
    for k in sorted(set(FIELDS) - CANON_EXCLUDE):
        v = row.get(k)
        if v is None or v == "":
            obj[k] = None
        elif k in MONEY:
            obj[k] = d8(Decimal(str(v)))
        else:
            obj[k] = v
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def compute_hash(prev: str, row: Dict[str, Any]) -> str:
    payload = canonical_payload(row)
    return hashlib.sha256((prev + "\n" + payload).encode("utf-8")).hexdigest()


def read_rows(path: Path) -> List[Dict[str, Optional[str]]]:
    if not path.exists():
        raise SystemExit(f"Ledger not found: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if list(reader.fieldnames or []) != FIELDS:
            raise SystemExit(
                f"Unexpected header.\n  expected: {FIELDS}\n  got:      {reader.fieldnames}"
            )
        rows = []
        for r in reader:
            rows.append({k: (None if r.get(k, "") == "" else r.get(k, "")) for k in FIELDS})
    return rows


def write_rows(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            out = {}
            for k in FIELDS:
                v = r.get(k)
                if v is None:
                    out[k] = ""
                elif k in MONEY:
                    out[k] = d8(Decimal(str(v)))
                else:
                    out[k] = str(v)
            w.writerow(out)


def cmd_init(args: argparse.Namespace) -> int:
    path = Path(args.ledger)
    if path.exists() and not args.force:
        print(f"Refusing to overwrite existing ledger: {path}", file=sys.stderr)
        print("Pass --force to replace (destructive).", file=sys.stderr)
        return 1
    ts_utc, ts_local = now_pair(args.tz_offset)
    row: Dict[str, Any] = {
        "entry_id": "E0001",
        "timestamp_utc": ts_utc,
        "timestamp_local": ts_local,
        "entry_type": "GENESIS",
        "counterparty": "self",
        "currency": args.currency.upper(),
        "amount": Decimal("0"),
        "cash_effect": Decimal("0"),
        "memo": args.memo or "Genesis — empty cash journal",
        "evidence_ref": args.evidence or "",
        "prev_entry_hash": GENESIS_PREV,
    }
    row["entry_hash"] = compute_hash(GENESIS_PREV, row)
    write_rows(path, [row])
    print(f"Initialized {path}")
    print(f"tip={row['entry_hash']}")
    return 0


def next_entry_id(rows: List[Dict[str, Any]]) -> str:
    n = len(rows) + 1
    return f"E{n:04d}"


def cmd_add(args: argparse.Namespace) -> int:
    path = Path(args.ledger)
    rows = read_rows(path)
    if not rows:
        raise SystemExit("Empty ledger; run init first")
    tip = rows[-1]["entry_hash"]
    assert tip is not None
    amount = parse_money(args.amount)
    # cash_effect: + for inflow, - for outflow; default = signed amount
    if args.cash_effect is not None:
        cash = parse_money(args.cash_effect)
    else:
        cash = amount if args.direction == "in" else -amount if args.direction == "out" else amount

    ts_utc, ts_local = now_pair(args.tz_offset)
    row: Dict[str, Any] = {
        "entry_id": next_entry_id(rows),
        "timestamp_utc": ts_utc,
        "timestamp_local": ts_local,
        "entry_type": args.type.upper(),
        "counterparty": args.counterparty or "",
        "currency": (args.currency or rows[-1].get("currency") or "INR").upper(),
        "amount": abs(amount),
        "cash_effect": cash,
        "memo": args.memo or "",
        "evidence_ref": args.evidence or "",
        "prev_entry_hash": tip,
    }
    row["entry_hash"] = compute_hash(tip, row)
    rows.append(row)
    write_rows(path, rows)
    print(f"Added {row['entry_id']} cash_effect={d8(cash)} {row['currency']}")
    print(f"tip={row['entry_hash']}")
    return 0


def verify_rows(rows: List[Dict[str, Any]]) -> tuple[bool, str]:
    if not rows:
        return False, "empty ledger"
    ids = [r["entry_id"] for r in rows]
    if len(ids) != len(set(ids)):
        return False, "duplicate entry_id"
    prev = GENESIS_PREV
    for i, r in enumerate(rows):
        if r["prev_entry_hash"] != prev:
            return False, f"broken chain at {r['entry_id']}: prev_entry_hash mismatch"
        if r["entry_type"] == "GENESIS" and i != 0:
            return False, "GENESIS not first"
        if i == 0 and r["prev_entry_hash"] != GENESIS_PREV:
            return False, "genesis prev hash must be 64 zeros"
        expect = compute_hash(r["prev_entry_hash"] or GENESIS_PREV, r)
        if expect != r["entry_hash"]:
            return False, f"entry_hash mismatch at {r['entry_id']}"
        eh = r["entry_hash"] or ""
        ph = r["prev_entry_hash"] or ""
        if eh != eh.lower() or ph != ph.lower():
            return False, f"non-lowercase hash at {r['entry_id']}"
        prev = eh
    return True, f"{len(rows)} entries; tip={rows[-1]['entry_hash']}"


def cmd_verify(args: argparse.Namespace) -> int:
    rows = read_rows(Path(args.ledger))
    ok, msg = verify_rows(rows)
    if ok:
        print(f"PASS: {msg}")
        return 0
    print(f"FAIL: {msg}")
    return 1


def cmd_tip(args: argparse.Namespace) -> int:
    rows = read_rows(Path(args.ledger))
    if not rows:
        print("empty")
        return 1
    print(rows[-1]["entry_hash"])
    return 0


def cmd_balance(args: argparse.Namespace) -> int:
    rows = read_rows(Path(args.ledger))
    ok, msg = verify_rows(rows)
    if not ok:
        print(f"FAIL (verify first): {msg}", file=sys.stderr)
        return 1
    totals: Dict[str, Decimal] = {}
    for r in rows:
        ccy = (r.get("currency") or "?").upper()
        totals[ccy] = totals.get(ccy, Decimal("0")) + Decimal(str(r.get("cash_effect") or "0"))
    for ccy in sorted(totals):
        print(f"{ccy}\t{d8(totals[ccy])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cash-ledger",
        description="Append-only SHA-256 hash-chained cash journal (v%s)" % VERSION,
    )
    p.add_argument("--version", action="version", version="cash-ledger %s" % VERSION)
    p.add_argument(
        "-f", "--ledger",
        default="ledger.csv",
        help="Path to ledger CSV (default: ledger.csv)",
    )
    p.add_argument(
        "--tz-offset",
        type=float,
        default=5.5,
        help="Local timezone offset hours from UTC (default: 5.5 Asia/Kolkata)",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init", help="Create a new ledger with genesis row")
    init_p.add_argument("--currency", default="INR")
    init_p.add_argument("--memo", default="")
    init_p.add_argument("--evidence", default="")
    init_p.add_argument("--force", action="store_true")
    init_p.set_defaults(func=cmd_init)

    add_p = sub.add_parser("add", help="Append a journal entry")
    add_p.add_argument("--amount", required=True, help="Absolute amount (positive)")
    add_p.add_argument(
        "--direction",
        choices=["in", "out", "signed"],
        default="signed",
        help="in=+amount, out=-amount, signed=use amount as cash_effect (default)",
    )
    add_p.add_argument("--cash-effect", default=None, help="Override signed cash_effect")
    add_p.add_argument("--type", default="CASH", help="Entry type label (default CASH)")
    add_p.add_argument("--counterparty", default="")
    add_p.add_argument("--currency", default=None)
    add_p.add_argument("--memo", default="")
    add_p.add_argument("--evidence", default="")
    add_p.set_defaults(func=cmd_add)

    ver_p = sub.add_parser("verify", help="Verify hash chain integrity")
    ver_p.set_defaults(func=cmd_verify)

    tip_p = sub.add_parser("tip", help="Print tip entry_hash")
    tip_p.set_defaults(func=cmd_tip)

    bal_p = sub.add_parser("balance", help="Sum cash_effect by currency (after verify)")
    bal_p.set_defaults(func=cmd_balance)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
