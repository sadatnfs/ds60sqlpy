from datetime import datetime


def timestamp(value):
    result = datetime.fromisoformat(value)
    assert result.utcoffset() is not None
    return result


revisions = [
    {
        "order": 1,
        "revision": 1,
        "event": "2026-01-01T23:00:00+00:00",
        "ingested": "2026-01-01T23:01:00+00:00",
        "amount": 4,
    },
    {
        "order": 2,
        "revision": 1,
        "event": "2026-01-01T23:30:00+00:00",
        "ingested": "2026-01-02T02:00:00+00:00",
        "amount": 9,
    },
    {
        "order": 1,
        "revision": 2,
        "event": "2026-01-01T23:00:00+00:00",
        "ingested": "2026-01-03T01:00:00+00:00",
        "amount": 6,
    },
]
start = timestamp("2026-01-01T00:00:00+00:00")
end = timestamp("2026-01-02T00:00:00+00:00")


def report(cutoff):
    selected = {}
    identities = {}
    for row in revisions:
        identity = (row["order"], row["revision"])
        assert identity not in identities or identities[identity] == row
        identities[identity] = row
        if timestamp(row["ingested"]) < timestamp(cutoff):
            previous = selected.get(row["order"])
            if previous is None or row["revision"] > previous["revision"]:
                selected[row["order"]] = row
    return sum(row["amount"] for row in selected.values() if start <= timestamp(row["event"]) < end)


cutoffs = ["2026-01-02T00:00:00+00:00", "2026-01-03T00:00:00+00:00", "2026-01-04T00:00:00+00:00"]
assert [report(c) for c in cutoffs] == [4, 13, 15]
assert report(cutoffs[0]) == 4
print(list(zip(cutoffs, [report(c) for c in cutoffs], strict=True)))
