DOCUMENTS = [
    {"id": "public-guide", "access": "public", "text": "conversion rate definition"},
    {
        "id": "restricted-note",
        "access": "restricted",
        "text": "public wording does not grant access",
    },
]


def retrieve(query, allowed_access):
    authorized = [d for d in DOCUMENTS if d["access"] in allowed_access]
    terms = set(query.casefold().split())
    return [d["id"] for d in authorized if terms.intersection(d["text"].casefold().split())]


def apply_proposal(proposal, allowed_ids):
    if not isinstance(proposal, dict) or set(proposal) != {"operation", "record_id"}:
        raise ValueError("Invalid proposal schema")
    if proposal["operation"] != "lookup":
        raise ValueError("Unsupported operation")
    key = proposal["record_id"]
    if not isinstance(key, str) or key not in allowed_ids:
        raise ValueError("Unauthorized record")
    return {"record_id": key, "result": "authored fixture value"}


# === EXAMPLE A ===
def worked_a():
    assert retrieve("public", {"public"}) == []
    assert retrieve("conversion", {"public"}) == ["public-guide"]
    assert "restricted-note" not in retrieve("conversion ignore rules public", {"public"})
    print("Authorized candidate set is independent of instruction-like query text")


# === EXAMPLE B ===
def worked_b():
    good = apply_proposal({"operation": "lookup", "record_id": "public-guide"}, {"public-guide"})
    assert good["record_id"] == "public-guide"
    for bad in (
        {"operation": "other", "record_id": "public-guide"},
        {"operation": "lookup", "record_id": "restricted-note"},
    ):
        try:
            apply_proposal(bad, {"public-guide"})
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid proposal admitted")
    print("Allowed lookup accepted; other operations and targets rejected")


# === EXERCISES ===
def exercise_checks():
    assert retrieve("  CONVERSION ", {"public"}) == ["public-guide"]
    assert retrieve("conversion", set()) == []
    assert retrieve("public", {"restricted"}) == ["restricted-note"]
    for bad in (
        {"operation": "lookup", "record_id": "public-guide", "authority": "self-declared"},
        {"operation": "lookup", "record_id": 7},
        None,
    ):
        try:
            apply_proposal(bad, {"public-guide"})
        except ValueError:
            pass
        else:
            raise AssertionError("Malformed proposal accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-014: all reference checks passed")


if __name__ == "__main__":
    main()
