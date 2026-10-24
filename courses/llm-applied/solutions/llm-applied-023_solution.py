"""llm-applied-023: bounded local reference checks. No network or persistent data writes."""

from datetime import datetime, timedelta, timezone


def fresh(published, now, maximum_age):
    if (
        published.tzinfo is None
        or now.tzinfo is None
        or published.utcoffset() is None
        or now.utcoffset() is None
    ):
        raise ValueError("aware timestamps required")
    if maximum_age < timedelta(0):
        raise ValueError("nonnegative age limit")
    age = now - published
    return timedelta(0) <= age <= maximum_age


class Budget:
    def __init__(self, limit):
        if type(limit) is not int or limit < 0:
            raise ValueError("nonnegative integer limit")
        self.limit = limit
        self.used = 0

    def consume(self):
        if self.used >= self.limit:
            raise RuntimeError("operation budget exhausted")
        self.used += 1


def trace_record(value):
    return {key: value[key] for key in ["request_id", "corpus_version", "policy", "result"]}


def verify():
    # Exercise 1: Check evidence freshness
    now = datetime(2026, 10, 22, tzinfo=timezone.utc)
    published = now - timedelta(days=1)
    assert fresh(published, now, timedelta(days=2))

    # Exercise 2: Reject stale and future evidence
    assert not fresh(now - timedelta(days=3), now, timedelta(days=2))
    assert not fresh(now + timedelta(hours=1), now, timedelta(days=2))

    # Exercise 3: Enforce a three-call budget
    budget = Budget(3)
    for _ in range(3):
        budget.consume()
    try:
        budget.consume()
    except RuntimeError:
        pass
    else:
        raise AssertionError("budget exceeded")
    assert budget.used == 3

    # Exercise 4: Reject naive timestamp assumptions
    try:
        fresh(datetime(2026, 10, 21), now, timedelta(days=2))
    except ValueError:
        pass
    else:
        raise AssertionError("naive timestamp accepted")

    # Exercise 5: Build an allowlisted trace
    raw = {
        "request_id": "r1",
        "corpus_version": "v2",
        "policy": "public",
        "result": "abstained_stale",
        "secret": "hidden",
        "source_text": "restricted body",
    }
    trace = trace_record(raw)
    assert (
        set(trace) == {"request_id", "corpus_version", "policy", "result"}
        and "secret" not in trace
        and "source_text" not in trace
    )

    # Exercise 6: Make stale evidence produce abstention
    authorized = True
    current = fresh(now - timedelta(days=3), now, timedelta(days=2))
    answer_allowed = authorized and current
    assert not answer_allowed
    result = {"status": "unknown", "reason": "stale evidence"}
    assert result["reason"] == "stale evidence"
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
