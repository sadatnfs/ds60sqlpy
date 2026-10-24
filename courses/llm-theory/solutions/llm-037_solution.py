"""llm-037: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Exercise 1: Classify four cases
    rows = [
        {"id": "q1", "miss": True, "unsupported": False, "abstain": False, "correct": False},
        {"id": "q2", "miss": False, "unsupported": True, "abstain": False, "correct": False},
        {"id": "q3", "miss": False, "unsupported": False, "abstain": True, "correct": True},
        {"id": "q4", "miss": False, "unsupported": False, "abstain": False, "correct": True},
    ]
    assert sum(r["miss"] for r in rows) == 1 and sum(r["unsupported"] for r in rows) == 1

    # Exercise 2: Compute appropriate abstention
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
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
