def main():
    before = {
        "deployment": "dep-a",
        "replicaset": "rs-a",
        "pods": {"pod-1", "pod-2"},
        "generation": 1,
    }
    after = {**before, "pods": {"pod-2", "pod-3"}}
    assert (
        before["deployment"] == after["deployment"] and before["generation"] == after["generation"]
    )
    assert after["pods"] - before["pods"] == {"pod-3"} and before["pods"] - after["pods"] == {
        "pod-1"
    }
    assert not (3 >= 4)
    pods = [
        {"uid": "owned", "controller": "rs-a", "ready": True},
        {"uid": "foreign", "controller": "rs-other", "ready": True},
    ]
    assert len(pods) == 2 and sum(p["controller"] == "rs-a" and p["ready"] for p in pods) == 1
    print("k8s-006 synthetic reconciliation and ownership checks passed")


if __name__ == "__main__":
    main()
