def main():
    grants = {("own", "pods", "get"), ("own", "pods", "list")}
    assert ("own", "pods", "get") in grants
    for request in [
        ("other", "pods", "get"),
        ("own", "secrets", "get"),
        ("own", "roles", "create"),
        ("cluster", "clusterroles", "create"),
    ]:
        assert request not in grants
    workload = {"automountServiceAccountToken": False}
    assert workload["automountServiceAccountToken"] is False

    def lease_covers(remaining, work=60, cleanup=15, margin=5):
        return remaining > work + cleanup + margin

    assert lease_covers(900) and not lease_covers(30)
    print("k8s-018 synthetic RBAC/expiry checks passed; no token or API response exposed")


if __name__ == "__main__":
    main()
