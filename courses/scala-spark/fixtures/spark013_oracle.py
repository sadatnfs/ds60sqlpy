from collections import defaultdict

fixture = [
    (1, "A", 100, "paid"), (2, "A", None, "paid"),
    (3, "B", 0, "paid"), (4, None, 50, "paid"),
    (5, "B", 150, "void"), (6, "A", 100, "paid"),
    (7, "C", None, "paid"),
]
assert len({event[0] for event in fixture}) == 7
paid_fixture = [event for event in fixture if event[3] == "paid"]
assert [event[0] for event in paid_fixture] == [1, 2, 3, 4, 6, 7]

def reference_metrics(events):
    observed = [event[2] for event in events if event[2] is not None]
    return (len(events), len(observed), sum(observed) if observed else None)

def reference_summary(events):
    grouped = defaultdict(list)
    for event in events:
        grouped[event[1]].append(event)
    keys = sorted(grouped, key=lambda team: (team is None, team or ""))
    return [(team, *reference_metrics(grouped[team])) for team in keys]

golden = [
    ("A", 3, 2, 200), ("B", 1, 1, 0),
    ("C", 1, 0, None), (None, 1, 1, 50),
]
assert reference_metrics(fixture) == (7, 5, 400)
assert reference_metrics(paid_fixture) == (6, 4, 250)
assert reference_summary(paid_fixture) == golden
projected_distinct = {(event[1], event[2]) for event in paid_fixture}
assert len(projected_distinct) == 5
assert sum(amount for _, amount in projected_distinct if amount is not None) == 150
assert [event[0] for event in paid_fixture if event[2] is None] == [2, 7]
assert [event[0] for event in paid_fixture if event[2] == 0] == [3]
assert [event[0] for event in paid_fixture if event[1] is None] == [4]
print("Reference checks passed: 7 raw, 6 paid, 4 observed, 250 cents.")
