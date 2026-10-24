"""llm-021: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Exercise 1: Fingerprint exact text
    import hashlib, json

    hash_text = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
    a = hash_text("red square")
    copy = hash_text("red square")
    para = hash_text("square colored red")
    assert a == copy and a != para

    # Exercise 2: Assign whole families
    family = {"a": "F", "a2": "F", "b": "G", "c": "H"}
    policy = {"F": "train", "G": "validation", "H": "test"}
    manifest = {doc: policy[group] for doc, group in family.items()}
    assert manifest == {"a": "train", "a2": "train", "b": "validation", "c": "test"}

    # Exercise 3: Audit all partition pairs
    sets = {part: {family[d] for d, p in manifest.items() if p == part} for part in policy.values()}
    assert (
        not sets["train"] & sets["validation"]
        and not sets["train"] & sets["test"]
        and not sets["validation"] & sets["test"]
    )

    # Exercise 4: Inject a known leak
    bad = dict(manifest)
    bad["a2"] = "validation"
    train = {family[d] for d, p in bad.items() if p == "train"}
    valid = {family[d] for d, p in bad.items() if p == "validation"}
    assert train & valid == {"F"}

    # Exercise 5: Preserve the manifest identity
    payload = lambda: json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    before = hashlib.sha256(payload()).hexdigest()
    summary = {"test_documents": sum(p == "test" for p in manifest.values())}
    assert summary["test_documents"] == 1 and hashlib.sha256(payload()).hexdigest() == before

    # Exercise 6: Distinguish normalization policy
    assert hash_text("red square") != hash_text("red square ")
    assert hash_text("red square".strip()) == hash_text("red square ".strip())
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
