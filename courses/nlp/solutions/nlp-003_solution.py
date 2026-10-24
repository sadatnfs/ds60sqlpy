"""Exact-span extraction with original fixed invoice fixtures."""

import math
import re

INITIAL = re.compile(r"\bINV-(?P<number>[0-9]{4})\b")
CANDIDATE = re.compile(r"\b[Ii][Nn][Vv]-(?P<number>[0-9]{4})\b")


def extract_invoices(text):
    result = []
    for match in CANDIDATE.finditer(text):
        digits = match.group("number")
        if digits != "0000":
            result.append({"raw": match.group(0), "id": "INV-" + digits, "span": match.span()})
    return result


def exact_metrics(predicted, gold):
    tp, fp, fn = len(predicted & gold), len(predicted - gold), len(gold - predicted)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
    }


def verify():
    # Exercise 1: exact spans and captures, not just matching text.
    text = "Pay INV-1042, then review INV-9012."
    matches = list(INITIAL.finditer(text))
    assert [(m.group(0), m.group("number"), m.span()) for m in matches] == [
        ("INV-1042", "1042", (4, 12)),
        ("INV-9012", "9012", (26, 34)),
    ]
    assert all(text[m.start() : m.end()] == m.group(0) for m in matches)

    # Exercise 2: plausible overmatching rules must fail these counterexamples.
    for invalid in ("INV-10420", "xINV-1042", "_INV-1042", "INV-１２３４"):
        assert list(INITIAL.finditer(invalid)) == []
    assert INITIAL.search("(INV-1042)").group(0) == "INV-1042"

    # Exercise 3: extraction and field validation are distinct operations.
    pattern = re.compile(r"INV-[0-9]{4}")
    assert [
        pattern.search("ticket: INV-1042") is not None,
        pattern.match("ticket: INV-1042") is not None,
        pattern.fullmatch("INV-1042") is not None,
        pattern.fullmatch("INV-1042 extra") is not None,
    ] == [True, False, True, False]

    # Exercise 4: semantics and canonicalization retain raw provenance.
    text = "INV-0000, inv-7777 and INV-10420"
    assert extract_invoices(text) == [{"raw": "inv-7777", "id": "INV-7777", "span": (10, 18)}]
    assert text == "INV-0000, inv-7777 and INV-10420"
    assert extract_invoices("INV-0012")[0]["id"] == "INV-0012"

    # Exercise 5: entity identity includes the document and exact span.
    gold = {("t1", 0, 8, "INV-1042"), ("t2", 0, 8, "INV-9012"), ("t4", 0, 8, "INV-7777")}
    predicted = {("t1", 0, 8, "INV-1042"), ("t2", 0, 8, "INV-9012"), ("t3", 0, 8, "INV-0000")}
    metrics = exact_metrics(predicted, gold)
    assert (metrics["tp"], metrics["fp"], metrics["fn"]) == (2, 1, 1)
    assert math.isclose(metrics["precision"], 2 / 3) and math.isclose(metrics["recall"], 2 / 3)
    moved = (predicted - {("t1", 0, 8, "INV-1042")}) | {("other", 0, 8, "INV-1042")}
    assert exact_metrics(moved, gold)["tp"] == 1
    assert exact_metrics(set(), set())["precision"] is None

    # Exercise 6: action interpretation needs a written semantic contract.
    assert extract_invoices("Please pay INV-1042")[0]["id"] == "INV-1042"
    assert extract_invoices("Do not pay INV-1042")[0]["id"] == "INV-1042"
    return {"status": "passed", "automated_exercises": 5, "written_exercises": 1}


if __name__ == "__main__":
    print(verify())
