import json
from pathlib import Path


def main():
    events = json.loads(
        (Path(__file__).resolve().parents[1] / "fixtures/k8s-040-timeline.json").read_text()
    )
    assert [e["seconds"] for e in events] == sorted(e["seconds"] for e in events)
    assert len({e["service_uid"] for e in events}) == 1
    assert events[0]["response"] == "expected" and events[1]["response"] == "timeout"
    assert events[2]["ready_pods"] == 1 and events[2]["endpoints"] == 0
    assert events[-1]["endpoints"] == 1 and events[-1]["response"] == "expected"
    print("k8s-040 synthetic selector incident trace passed; no fault injected")


if __name__ == "__main__":
    main()
