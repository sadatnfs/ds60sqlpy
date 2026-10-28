"""Two complete investigations of a small delivery-summary contract."""


def summarize(records):
    accepted = []
    rejected = []
    seen = set()
    for position, record in enumerate(records):
        if not isinstance(record, dict):
            rejected.append({"position": position, "reason": "record must be a mapping"})
            continue
        delivery_id = record.get("delivery_id")
        packages = record.get("packages")
        if not isinstance(delivery_id, str) or not delivery_id.strip():
            rejected.append({"position": position, "reason": "missing delivery identity"})
        elif delivery_id in seen:
            rejected.append({"position": position, "reason": "duplicate delivery identity"})
        elif type(packages) is not int or packages < 1:
            rejected.append({"position": position, "reason": "packages must be a positive integer"})
        else:
            seen.add(delivery_id)
            accepted.append({"delivery_id": delivery_id, "packages": packages})
    total = 0
    for record in accepted:
        total += record["packages"]
    return {
        "input_rows": len(records),
        "accepted_rows": len(accepted),
        "candidate_packages": total,
        "rejected": rejected,
        "publishable": not rejected,
    }


def example_one():
    records = [
        {"delivery_id": "A", "packages": 2},
        {"delivery_id": "B", "packages": 3},
        {"delivery_id": "C", "packages": 1},
    ]
    result = summarize(records)
    assert result["candidate_packages"] == 6 and result["accepted_rows"] == 3
    assert result["publishable"] is True
    return result


def example_two():
    records = [
        {"delivery_id": "A", "packages": 2},
        {"delivery_id": "B", "packages": 3},
        {"delivery_id": "C", "packages": 1},
        {"delivery_id": "D", "packages": "4"},
    ]
    result = summarize(records)
    assert result["input_rows"] == result["accepted_rows"] + len(result["rejected"]) == 4
    assert result["candidate_packages"] == 6 and result["publishable"] is False
    assert result["rejected"][0]["position"] == 3
    assert summarize([{"delivery_id": "Z", "packages": True}])["publishable"] is False
    return result


def main():
    print("Complete valid delivery:", example_one())
    print("Changed input, publication withheld:", example_two())


if __name__ == "__main__":
    main()
