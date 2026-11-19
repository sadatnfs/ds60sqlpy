"""llm-021: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Worked example A: Fingerprint exact text
    import hashlib, json

    hash_text = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
    a = hash_text("red square")
    copy = hash_text("red square")
    para = hash_text("square colored red")
    assert a == copy and a != para

    # Worked example B: Assign whole families
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

    # Exercise 1: Assign a second family policy
    family2 = {"p": "J", "p2": "J", "p3": "J", "q": "K", "r": "L"}
    policy2 = {"J": "test", "K": "train", "L": "validation"}
    manifest2 = {doc: policy2[group] for doc, group in family2.items()}
    assert sorted(d for d, s in manifest2.items() if s == "test") == ["p", "p2", "p3"]
    assert list(manifest2.values()).count("train") == 1 and manifest2["r"] == "validation"

    # Exercise 2: Predict the effect of key order
    forward = json.dumps({"a": "train", "b": "test"})
    backward = json.dumps({"b": "test", "a": "train"})
    assert hash_text(forward) != hash_text(backward)
    assert hash_text(json.dumps({"a": "train", "b": "test"}, sort_keys=True)) == hash_text(
        json.dumps({"b": "test", "a": "train"}, sort_keys=True)
    )
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
