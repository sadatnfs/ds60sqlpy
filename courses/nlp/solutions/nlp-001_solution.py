"""Original corpus-contract examples. No network or external data is used."""

from collections import Counter
from copy import deepcopy
import math

DOCUMENTS = [
    {"id": "a", "family": "account-reset", "text": "Reset password", "label": "account"},
    {"id": "b", "family": "billing-charge", "text": "Double charge", "label": "billing"},
    {"id": "c", "family": "account-reset", "text": "Password reset please", "label": "account"},
    {"id": "d", "family": "billing-refund", "text": "Refund request", "label": "billing"},
]


def validate_corpus(rows):
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each example must be a record.")
        for field in ("id", "family", "text", "label"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Missing or blank {field}.")
        if row["id"] in seen:
            raise ValueError("Duplicate document identity.")
        seen.add(row["id"])
    return len(seen)


def corpus_counts(rows):
    validate_corpus(rows)
    return {
        "documents": len(rows),
        "classes": dict(Counter(row["label"] for row in rows)),
        "whitespace_pieces": sum(len(row["text"].split()) for row in rows),
    }


def family_overlap(left, right):
    return {row["family"] for row in left} & {row["family"] for row in right}


def verify():
    # Exercise 1: unique identity and nonmutation.
    before = deepcopy(DOCUMENTS)
    assert validate_corpus(DOCUMENTS) == 4
    try:
        validate_corpus(DOCUMENTS + [dict(DOCUMENTS[0])])
    except ValueError:
        pass
    else:
        raise AssertionError("A repeated document ID was accepted.")
    assert DOCUMENTS == before

    # Exercise 2: invalid text and missing provenance are errors.
    for broken in (
        {**DOCUMENTS[0], "text": "  "},
        {key: value for key, value in DOCUMENTS[0].items() if key != "family"},
    ):
        try:
            validate_corpus([broken])
        except ValueError:
            pass
        else:
            raise AssertionError("An invalid text record was accepted.")

    # Exercise 3: text length and number of prediction units differ.
    assert corpus_counts(DOCUMENTS) == {
        "documents": 4,
        "classes": {"account": 2, "billing": 2},
        "whitespace_pieces": 9,
    }
    changed = deepcopy(DOCUMENTS)
    changed[0]["text"] += " " + changed[0]["text"]
    assert corpus_counts(changed) == {
        "documents": 4,
        "classes": {"account": 2, "billing": 2},
        "whitespace_pieces": 11,
    }

    # Exercise 4: the weighted score answers a different question.
    correct = [1, 0]
    assert sum(correct) / len(correct) == 0.5
    scores = [
        sum(c * w for c, w in zip(correct, weights)) / sum(weights)
        for weights in ([1000, 10], [10, 1000])
    ]
    assert math.isclose(scores[0], 1000 / 1010, abs_tol=1e-12)
    assert math.isclose(scores[1], 10 / 1010, abs_tol=1e-12)

    # Exercise 5: related text stays together, and no row disappears.
    assert family_overlap(DOCUMENTS[:2], DOCUMENTS[2:]) == {"account-reset"}
    train, holdout = [DOCUMENTS[0], DOCUMENTS[2]], [DOCUMENTS[1], DOCUMENTS[3]]
    assert family_overlap(train, holdout) == set()
    assert sorted(row["id"] for row in train + holdout) == ["a", "b", "c", "d"]

    # Exercise 6 requires an explained task contract, not a fake automatic grade.
    return {"status": "passed", "automated_exercises": 5, "written_exercises": 1}


if __name__ == "__main__":
    print(verify())
