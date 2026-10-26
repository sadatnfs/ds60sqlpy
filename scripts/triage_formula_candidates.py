#!/usr/bin/env python3
"""Classify an audit inventory for review without rewriting any course content.

Categories describe likely notation, not correctness. Only explicit reviewed
source patterns receive a manual-review status. Everything else remains an
unverified candidate, even when its category has high confidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATH = re.compile(
    r"[∑∏∂∫∝]|\\(?:frac|sum|sqrt|partial)\b"
    r"|\b(?:PMI|IDF|KL|Var|Cov|SE|softmax|sigmoid|log|exp)\s*\("
    r"|\b(?:[A-Za-z]_[A-Za-z0-9]+|[A-Za-z])\s*=\s*[^.,;]+[-+*/^]"
    r"|\b(?:gradient|derivative|variance|probability|equation|matrix)\b.*[=^]"
)
CODE = re.compile(
    r"\b[a-z][a-z0-9]*_[a-z0-9_]+\b|\b\w+\.\w+\s*\("
    r"|\b(?:SELECT|FROM|WHERE|JOIN|ORDER BY|GROUP BY|assert|return|import)\b"
    r"|\b\w+\([^)]*=[^)]*\)|(?:===|=>|::|->)|\$[A-Za-z_]"
)


def classify(source: str) -> tuple[str, str]:
    """Keep existing explicit math/code out of raw-notation classification."""
    residual = re.sub(r"\\\(.*?\\\)|\\\[.*?\\\]", " ", source)
    residual = re.sub(r"`+[^`]*`+", " ", residual)
    if MATH.search(residual):
        return "math", "mathematical notation or an equation in surrounding prose"
    if CODE.search(residual):
        return "code", "program identifier, API, query or programming operator"
    return "prose", "no decisive mathematical or programming pattern after exclusions"


def triage(
    inventory: dict[str, Any], ledger: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = []
    for item in inventory["items"]:
        if item["kind"] != "raw_notation_candidate":
            continue
        category, reason = classify(item["source"])
        matching = [
            case["id"]
            for case in ledger["notation_corrections"]
            if any(item["path"].startswith(prefix) for prefix in case["path_prefixes"])
            and any(pattern in item["source"] for pattern in case["original_patterns"])
        ]
        rows.append(
            {
                "path": item["path"],
                "location": item.get("location", ""),
                "line": item["line"],
                "category": category,
                "classification_method": "heuristic",
                "review_status": "reviewed_notation_correction" if matching else "unverified",
                "review_cases": ",".join(matching),
                "reason": reason,
                "source": item["source"],
            }
        )
    summary = {
        "candidate_lines": len(rows),
        "categories": dict(Counter(row["category"] for row in rows)),
        "review_status": dict(Counter(row["review_status"] for row in rows)),
        "boundary": (
            "Classification is heuristic. A reviewed notation correction does not prove every "
            "claim on that line. Unverified candidates are not automatically errors or approved "
            "formulas. No source rewriting or runtime qualification is performed."
        ),
    }
    return rows, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path, help="Previously saved source inventory JSON")
    parser.add_argument("--csv", type=Path, help="Optional review queue destination")
    parser.add_argument("--summary", type=Path, help="Optional summary JSON destination")
    args = parser.parse_args()
    raw = args.inventory.read_bytes()
    ledger = json.loads((ROOT / "curriculum/formula-review.json").read_text(encoding="utf-8"))
    rows, summary = triage(json.loads(raw), ledger)
    summary["inventory_sha256"] = hashlib.sha256(raw).hexdigest()
    if args.csv:
        with args.csv.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]) if rows else [])
            writer.writeheader()
            writer.writerows(rows)
    encoded = json.dumps(summary, indent=2) + "\n"
    if args.summary:
        args.summary.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
