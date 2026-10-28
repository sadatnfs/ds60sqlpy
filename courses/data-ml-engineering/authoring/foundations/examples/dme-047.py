"""Explicit retry and breaker state models over local call outcomes, not a network service."""


class Breaker:
    def __init__(self):
        self.state = "closed"
        self.failures = 0
        self.opened_at = None
        self.last_time = -1
        self.calls = 0

    def request(self, now, dependency):
        if type(now) is not int or now < 0 or now < self.last_time:
            raise ValueError("Use a monotone integer model clock")
        self.last_time = now
        if self.state == "open":
            if now < self.opened_at + 5:
                return "fallback"
            self.state = "half-open"
        attempts = 1 if self.state == "half-open" else 2
        for _ in range(attempts):
            self.calls += 1
            if dependency():
                self.state, self.failures = "closed", 0
                return "live"
            self.failures += 1
            if self.state == "half-open" or self.failures >= 3:
                self.state, self.opened_at = "open", now
                break
        return "fallback"


def example_one():
    outcomes = iter([False, False, False, True, True])
    breaker = Breaker()
    observations = []
    for now in [0, 1, 2, 6, 7]:
        result = breaker.request(now, lambda: next(outcomes))
        observations.append([now, result, breaker.state, breaker.calls])
    assert observations == [
        [0, "fallback", "closed", 2],
        [1, "fallback", "open", 3],
        [2, "fallback", "open", 3],
        [6, "live", "closed", 4],
        [7, "live", "closed", 5],
    ]
    return {
        "observations": observations,
        "dependency_calls": 5,
        "scope": (
            "local state-machine model; fallback is explicitly labelled "
            "and performs no business mutation"
        ),
    }


def nested_retries(shared_budget=None):
    if shared_budget is not None and (type(shared_budget) is not int or shared_budget < 1):
        raise ValueError("The shared attempt budget must be a positive integer")
    calls = 0
    for _outer in range(3):
        for _inner in range(3):
            if shared_budget is not None and calls >= shared_budget:
                return calls
            calls += 1
    return calls


def example_two():
    uncoordinated = nested_retries()
    bounded = nested_retries(shared_budget=4)
    assert uncoordinated == 9 and bounded == 4
    return {
        "one_logical_request_uncoordinated_calls": uncoordinated,
        "shared_budget_calls": bounded,
        "all_attempts_failed": True,
        "unsafe_mutations_need_idempotency_not_just_retry_limits": True,
    }


def main():
    print("Bounded attempts, cooldown and a recovery probe:", example_one())
    print("Nested retries amplify dependency traffic:", example_two())


if __name__ == "__main__":
    main()
