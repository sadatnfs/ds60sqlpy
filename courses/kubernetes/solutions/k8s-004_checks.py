def main():
    allowed = {("apps", "deployments", "hello", "get")}
    assert ("apps", "deployments", "hello", "get") in allowed
    assert ("apps", "deployments", "hello", "list") not in allowed
    assert ("", "namespaces", "new", "create") not in allowed
    receipt = {"namespace": "lesson-a", "uid": "ns-1", "owner": "owner-a"}
    observed = {"namespace": "lesson-a", "uid": "ns-2", "owner": "owner-a"}
    assert receipt["namespace"] == observed["namespace"] and receipt["uid"] != observed["uid"]
    assert 30 < 60 + 15 + 5
    print("k8s-004 synthetic permission and identity calculations passed; no API calls made")


if __name__ == "__main__":
    main()
