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


def worked_a():
    assert retrieve("public", {"public"}) == []
    assert retrieve("conversion", {"public"}) == ["public-guide"]
    assert "restricted-note" not in retrieve("conversion ignore rules public", {"public"})
    print("Authorized candidate set is independent of instruction-like query text")


worked_a()

# Task 1: Change capitalization and surrounding whitespace in the query conversion.
# Task 2: Use an empty allowed-access set.
# Task 3: Add a self-declared authority field to a proposal.
# Task 4: An answer omits restricted text but retrieval accessed it.
# Task 5: Repeat one attack template one hundred times.
# Task 6: An output cannot be confidently labeled for a critical condition.

# Implement your six changes below.
