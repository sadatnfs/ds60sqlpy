"""A bounded event-time mechanism model, not an executed streaming engine."""

from dataclasses import dataclass, field


@dataclass
class WindowState:
    total: int = 0
    emitted: bool = False
    revision: int = 0


@dataclass
class Windows:
    width: int = 5
    grace: int = 2
    watermark: int = 0
    states: dict[int, WindowState] = field(default_factory=dict)
    changes: list[tuple[int, int, int]] = field(default_factory=list)
    late: list[tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        if (
            type(self.width) is not int
            or self.width < 1
            or type(self.grace) is not int
            or self.grace < 0
        ):
            raise ValueError("Width must be positive and grace nonnegative integer time units")

    def emit(self, start, state):
        state.emitted = True
        state.revision += 1
        self.changes.append((start, state.revision, state.total))

    def event(self, timestamp, value):
        if type(timestamp) is not int or timestamp < 0 or type(value) is not int:
            raise ValueError("Use nonnegative integer event times and integer values")
        start = timestamp // self.width * self.width
        end = start + self.width
        if self.watermark >= end + self.grace:
            self.late.append((timestamp, value))
            return "late-side-output"
        state = self.states.setdefault(start, WindowState())
        state.total += value
        if self.watermark >= end:
            self.emit(start, state)
        return "accepted"

    def advance(self, watermark):
        if type(watermark) is not int or watermark < self.watermark:
            raise ValueError("Watermarks are monotone integer progress assertions")
        self.watermark = watermark
        for start, state in list(self.states.items()):
            end = start + self.width
            if watermark >= end and not state.emitted:
                self.emit(start, state)
            if watermark >= end + self.grace:
                del self.states[start]


def materialize(changes):
    accepted = {}
    for start, revision, total in changes:
        prior = accepted.get(start)
        if prior is None or revision > prior[0]:
            accepted[start] = (revision, total)
        elif revision == prior[0] and total != prior[1]:
            raise ValueError("One window revision cannot name two values")
    return {start: total for start, (_, total) in sorted(accepted.items())}


def example_one():
    windows = Windows()
    windows.event(2, 3)
    windows.event(1, 2)
    windows.advance(5)
    windows.event(6, 1)
    windows.advance(10)
    windows.advance(12)
    result = materialize(windows.changes)
    assert result == {0: 5, 5: 1} and windows.states == {} and windows.late == []
    return {"accepted_windows": result, "change_log": windows.changes, "retained_state": 0}


def example_two():
    windows = Windows()
    windows.event(1, 2)
    windows.event(2, 3)
    windows.advance(5)
    windows.event(3, 4)
    assert windows.changes == [(0, 1, 5), (0, 2, 9)]
    windows.advance(7)
    assert windows.event(4, 100) == "late-side-output"
    assert materialize(windows.changes) == {0: 9} and windows.late == [(4, 100)]
    assert sum(total for _, _, total in windows.changes) == 14
    return {
        "upserted_result": materialize(windows.changes),
        "wrong_append_sum": 14,
        "late_side_output": windows.late,
        "retained_state": len(windows.states),
    }


def main():
    print("Event time and explicit progress:", example_one())
    print("Revision-aware sink and expired state:", example_two())


if __name__ == "__main__":
    main()
