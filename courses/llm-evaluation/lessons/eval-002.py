import hashlib


def validate_split(rows):
    seen = set()
    groups = {}
    for row in rows:
        if row["id"] in seen:
            raise ValueError("Duplicate ID")
        seen.add(row["id"])
        prior = groups.setdefault(row["family"], row["split"])
        if prior != row["split"]:
            raise ValueError("Family leakage")
    return groups


def training_ids(rows, cutoff):
    return [r["id"] for r in rows if r["event"] <= cutoff and r["label_available"] <= cutoff]


def fingerprint(text):
    normalized = " ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def worked_a():
    rows = [
        {"id": "m1", "family": "metrics", "split": "train"},
        {"id": "m2", "family": "metrics", "split": "train"},
        {"id": "p1", "family": "policy", "split": "test"},
    ]
    assert validate_split(rows) == {"metrics": "train", "policy": "test"}
    broken = [dict(r) for r in rows]
    broken[1]["split"] = "test"
    try:
        validate_split(broken)
    except ValueError as error:
        assert str(error) == "Family leakage"
    else:
        raise AssertionError("Leaking split accepted")
    print("Family split accepted; leaking split rejected")


worked_a()

# Task 1: Put two paraphrases from one family into train and test.
# Task 2: Use event and label times exactly equal to the cutoff.
# Task 3: Use event 9, label 11, cutoff 10.
# Task 4: Compare fingerprints of rate and rates.
# Task 5: Explain why a document corrected after the cutoff needs another corpus
# version.
# Task 6: Create a valid group assignment with an empty test partition.

# Implement your six changes below.
