"""Admission capacity is a conservation law, not an unbounded Python queue."""

from collections import deque


class Reservations:
    def __init__(self, slots=3, tokens=180):
        self.slots = slots
        self.tokens = tokens
        self.pending = deque()
        self.owned = {}

    def admit(self, identity, budget):
        if (
            identity in self.owned
            or len(self.owned) >= self.slots
            or sum(self.owned.values()) + budget > self.tokens
        ):
            return False
        self.owned[identity] = budget
        self.pending.append(identity)
        return True

    def release(self, identity):
        self.owned.pop(identity)
        if identity in self.pending:
            self.pending.remove(identity)


def example_one():
    queue = Reservations()
    assert queue.admit("a", 80)
    assert queue.admit("b", 60)
    assert not queue.admit("c", 50)
    queue.release("b")
    assert queue.admit("c", 50)
    assert list(queue.pending) == ["a", "c"]
    assert sum(queue.owned.values()) == 130
    queue.release("a")
    queue.release("c")
    assert not queue.owned
    print("Token and count reservations return to zero after explicit release.")


def example_two():
    arrivals = [0.0, 0.0, 0.0]
    service = [10.0, 1.0, 1.0]
    clock = 0.0
    waiting = []
    for arrival, duration in zip(arrivals, service, strict=True):
        started = max(clock, arrival)
        waiting.append(started - arrival)
        clock = started + duration
    assert waiting == [0.0, 10.0, 11.0]
    print("FIFO waits for long-first requests:", waiting)
    rate, mean_time = 0.5, 4.0
    mean_in_system = rate * mean_time
    assert mean_in_system == 2.0
    print("Little's-law steady-state mean occupancy:", mean_in_system)
    print("This average does not certify a finite queue against bursts.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
