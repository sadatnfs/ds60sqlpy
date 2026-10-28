"""Scheduling models compare latency and fairness, not GPU throughput."""

from collections import deque


def sequential(lengths):
    clock = 0
    finish = {}
    first = {}
    for identity, count in lengths.items():
        first[identity] = clock + 1
        clock += count
        finish[identity] = clock
    return first, finish


def round_robin(lengths):
    remaining = dict(lengths)
    ready = deque(lengths)
    first, finish = {}, {}
    clock = 0
    while ready:
        identity = ready.popleft()
        clock += 1
        first.setdefault(identity, clock)
        remaining[identity] -= 1
        if remaining[identity]:
            ready.append(identity)
        else:
            finish[identity] = clock
    return first, finish


def example_one():
    lengths = {"long": 8, "short": 2}
    first_a, finish_a = sequential(lengths)
    first_b, finish_b = round_robin(lengths)
    assert first_a == {"long": 1, "short": 9}
    assert first_b == {"long": 1, "short": 2}
    assert finish_a == {"long": 8, "short": 10}
    assert finish_b == {"short": 4, "long": 10}
    print("FIFO", first_a, finish_a, "round robin", first_b, finish_b)


def example_two():
    prompt_lengths = [2, 10, 11]
    padded_tokens = len(prompt_lengths) * max(prompt_lengths)
    actual_tokens = sum(prompt_lengths)
    assert padded_tokens == 33 and actual_tokens == 23
    bucketed_tokens = 2 + 2 * 11
    assert bucketed_tokens == 24
    print(
        "Padding before/after grouping:",
        padded_tokens - actual_tokens,
        bucketed_tokens - actual_tokens,
    )
    print(
        "Grouping has a waiting-time cost. A measured batching policy must include arrival times."
    )


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
