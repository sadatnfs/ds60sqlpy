"""llm-applied-011: bounded local reference checks. No network or persistent data writes."""


def extractive_answer(document, start, end, claim_id):
    if document is None:
        return {"status": "unknown", "claims": [], "citations": [], "reason": "missing evidence"}
    if not 0 <= start < end <= len(document["text"]):
        raise ValueError("valid nonempty source span required")
    return {
        "status": "answered",
        "claims": [{"id": claim_id, "quote": document["text"][start:end]}],
        "citations": [
            {
                "document_id": document["id"],
                "version": document["version"],
                "start": start,
                "end": end,
            }
        ],
    }


def verify():
    # Exercise 1: Return a supported extractive answer
    text = "Conversion rate equals purchases divided by eligible visits. Exclude test accounts."
    document = {"id": "metric-v1", "version": 1, "text": text}
    end = text.index(".") + 1
    answer = extractive_answer(document, 0, end, "conversion-definition")
    assert answer["status"] == "answered" and len(answer["claims"]) == 1
    assert (
        text[answer["citations"][0]["start"] : answer["citations"][0]["end"]]
        == answer["claims"][0]["quote"]
    )

    # Exercise 2: Reject a corrupted span
    bad = {"quote": "Conversion rate is always one."}
    assert text[0:end] != bad["quote"]

    # Exercise 3: Abstain on missing evidence
    unknown = extractive_answer(None, 0, 0, "comet-period")
    assert unknown == {
        "status": "unknown",
        "claims": [],
        "citations": [],
        "reason": "missing evidence",
    }

    # Exercise 4: Separate a valid citation from support
    support = {"conversion-definition": {"metric-v1"}, "test-account-exclusion": {"metric-v1"}}
    assert document["id"] == "metric-v1" and document["id"] not in support.get(
        "significance", set()
    )

    # Exercise 5: Bind the source version
    citation = answer["citations"][0]
    newer = {**document, "version": 2}
    assert citation["version"] != newer["version"]

    # Exercise 6: Keep arithmetic separate from prose
    calculation = {"purchases": 3, "visits": 10}
    value = calculation["purchases"] / calculation["visits"]
    record = {
        "computed_rate": value,
        "inputs": calculation,
        "method": "purchases / eligible visits",
    }
    assert record["computed_rate"] == 0.3 and record["inputs"]["visits"] == 10
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
