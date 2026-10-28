"""mle-002: worked starting point; complete the guide's six changes."""


def example_one():
    records = [
        {"id": 1, "event_at": 2, "known_at": 3, "value": 10},
        {"id": 2, "event_at": 4, "known_at": 7, "value": 999},
        {"id": 3, "event_at": 8, "known_at": 8, "value": 30},
    ]

    def select(cutoff):
        valid = [r for r in records if r["event_at"] <= cutoff and r["known_at"] <= cutoff]
        return max(valid, key=lambda r: (r["event_at"], r["known_at"]))["value"]

    assert [select(5), select(9)] == [10, 30]
    assert (
        max([r for r in records if r["event_at"] <= 5], key=lambda r: r["event_at"])["value"] == 999
    )
    return {"eligible": [10, 30], "event_only_leak": 999}


if __name__ == "__main__":
    print(example_one())

# TODO 1: Make the revision known before cutoff 5.
# TODO 2: Set known_at equal to the prediction cutoff.
# TODO 3: Move training cutoff from 180 to 181.
# TODO 4: Name a post-decision field that should not be used as a predictor.
# TODO 5: Explain why immature labels should not be filled with 0.
# TODO 6: Replace integer clocks with timezone-aware times.
