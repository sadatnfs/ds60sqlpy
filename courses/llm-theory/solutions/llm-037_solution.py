"""llm-037: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Worked example A: Classify four cases
    rows = [
        {"id": "q1", "miss": True, "unsupported": False, "abstain": False, "correct": False},
        {"id": "q2", "miss": False, "unsupported": True, "abstain": False, "correct": False},
        {"id": "q3", "miss": False, "unsupported": False, "abstain": True, "correct": True},
        {"id": "q4", "miss": False, "unsupported": False, "abstain": False, "correct": True},
    ]
    assert sum(r["miss"] for r in rows) == 1 and sum(r["unsupported"] for r in rows) == 1

    # Worked example B: Compute appropriate abstention
    assert sum(r["abstain"] and r["correct"] for r in rows) == 1
    assert sum(not r["abstain"] and r["correct"] for r in rows) == 1

    # Exercise 3: Attach a claim span
    text = "red square has four sides"
    claim = {
        "document": "d1",
        "span": "square has four sides",
        "text": "The square has four sides.",
    }
    assert claim["span"] in text

    # Exercise 4: Reject a misleading citation
    claim = {"document": "d1", "text": "The square weighs 10kg."}
    evidence = {"d1": text}
    assert claim["document"] in evidence and "10kg" not in evidence["d1"]

    # Exercise 5: Use an oracle-context control
    control = {"id": "q1", "oracle_context": True, "retrieval_miss": False, "answer_correct": True}
    assert control["oracle_context"] and not control["retrieval_miss"]

    # Exercise 6: Preserve question identity
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids))
    bad = ids + ["q1"]
    assert len(bad) != len(set(bad))

    # Exercise 1: Classify five new cases
    rows2 = [
        {"id": "r1", "miss": True, "unsupported": False, "abstain": False, "correct": False},
        {"id": "r2", "miss": True, "unsupported": False, "abstain": False, "correct": False},
        {"id": "r3", "miss": False, "unsupported": True, "abstain": False, "correct": False},
        {"id": "r4", "miss": False, "unsupported": False, "abstain": False, "correct": True},
        {"id": "r5", "miss": False, "unsupported": False, "abstain": True, "correct": False},
    ]
    assert sum(r["miss"] for r in rows2) == 2 and sum(r["unsupported"] for r in rows2) == 1
    assert (
        sum(r["abstain"] for r in rows2) == 1
        and sum(r["abstain"] and r["correct"] for r in rows2) == 0
    )

    # Exercise 2: Predict coverage and answered accuracy
    answered = [r for r in rows2 if not r["abstain"]]
    assert len(answered) / len(rows2) == 0.8
    assert sum(r["correct"] for r in answered) / len(answered) == 0.25
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
