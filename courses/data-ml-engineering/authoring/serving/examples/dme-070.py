"""Cancellation state and interrupted recovery are not automatic retries."""

from dataclasses import dataclass


@dataclass
class Request:
    state: str = "running"
    reserved: int = 48
    cancel_requested: bool = False

    def cancel(self):
        self.cancel_requested = True

    def kernel_returned(self):
        if self.state == "running" and self.cancel_requested:
            self.state = "cancelled"
            self.reserved = 0


def example_one():
    item = Request()
    item.cancel()
    assert item.state == "running" and item.reserved == 48
    item.kernel_returned()
    assert item.state == "cancelled" and item.reserved == 0
    item.kernel_returned()
    assert item.reserved == 0
    print("Cancellation requested first; reservation released exactly once after compute returns.")


def example_two():
    persisted = {"a": ["queued", "started", "token"], "b": ["queued", "started", "completed"]}
    original_b = tuple(persisted["b"])
    calls = 0
    for events in persisted.values():
        if events[-1] not in {"completed", "cancelled", "error"}:
            events.append("error:interrupted_by_restart")
    assert persisted["a"][-1] == "error:interrupted_by_restart"
    assert tuple(persisted["b"]) == original_b
    assert calls == 0
    print("Recovery records interruption; completed history remains unchanged:", persisted)
    print(
        "A new explicit request needs a new identity. "
        "Never infer missing output by rerunning old source."
    )


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
