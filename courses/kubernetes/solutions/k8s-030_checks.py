def decide(parent_uid, desired, child):
    if child is None:
        return "create"
    if child["owner_uid"] != parent_uid:
        return "refuse"
    return "no-op" if child["replicas"] == desired else "update"


def finish(finalizers, cleanup_ok):
    return [x for x in finalizers if x != "lesson.cleanup"] if cleanup_ok else list(finalizers)


def main():
    assert decide("p1", 1, None) == "create"
    child = {"owner_uid": "p1", "replicas": 1}
    assert [decide("p1", 1, child) for _ in range(2)] == ["no-op", "no-op"]
    assert decide("p1", 2, child) == "update"
    assert decide("p2", 1, child) == "refuse"
    fs = ["lesson.cleanup", "other.cleanup"]
    assert finish(fs, True) == ["other.cleanup"] and finish(fs, False) == fs
    print("k8s-030 decision model passed; no controller or external side effect executed")


if __name__ == "__main__":
    main()
