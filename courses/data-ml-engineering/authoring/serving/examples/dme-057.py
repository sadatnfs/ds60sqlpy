"""Request identity is a contract before it is a model invocation."""

import hashlib
import json


def fingerprint(prompt, version, seed):
    if not isinstance(prompt, str) or not 1 <= len(prompt.encode("utf-8")) <= 100:
        raise ValueError("bounded UTF-8 prompt required")
    if type(seed) is not int or not 0 <= seed < 2**31:
        raise ValueError("bounded integer seed required")
    raw = json.dumps(
        {"prompt": prompt, "model": version, "seed": seed}, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(raw.encode()).hexdigest()


def example_one():
    accepted = {}
    calls = 0

    def create(key, prompt):
        nonlocal calls
        digest = fingerprint(prompt, "synthetic-v1", 7)
        if key in accepted:
            if accepted[key] != digest:
                raise ValueError("idempotency conflict")
            return "existing"
        accepted[key] = digest
        calls += 1
        return "created"

    assert create("request-a", "model") == "created"
    assert create("request-a", "model") == "existing"
    assert calls == 1
    try:
        create("request-a", "changed")
    except ValueError as error:
        print("Conflict:", error)
    else:
        raise AssertionError("Changed source reused a key")
    print("admitted", calls, "digest", accepted["request-a"][:12])


def example_two():
    decomposed = "e\u0301"
    composed = "é"
    assert fingerprint(composed, "synthetic-v1", 7) != fingerprint(decomposed, "synthetic-v1", 7)
    assert len(composed.encode()) == 2 and len(decomposed.encode()) == 3
    for invalid in (True, -1, 2**31):
        try:
            fingerprint("safe", "synthetic-v1", invalid)
        except ValueError:
            print("Rejected seed", repr(invalid))
        else:
            raise AssertionError("Invalid seed accepted")
    print("No implicit Unicode normalization; identities remain source-bound.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
