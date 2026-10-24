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
    assert 900 > 60 + 15 + 5 and 30 < 60 + 15 + 5
    print("k8s-018 synthetic RBAC/expiry checks passed; no token or API response exposed")


if __name__ == "__main__":
    main()
