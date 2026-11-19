def main():
    allowed = {("apps", "deployments", "hello", "get")}
    assert ("apps", "deployments", "hello", "get") in allowed
    assert ("apps", "deployments", "hello", "list") not in allowed
    assert ("", "namespaces", "new", "create") not in allowed
    receipt = {"namespace": "lesson-a", "uid": "ns-1", "owner": "owner-a"}
    observed = {"namespace": "lesson-a", "uid": "ns-2", "owner": "owner-a"}
    assert receipt["namespace"] == observed["namespace"] and receipt["uid"] != observed["uid"]
    view_rules = {"pods": {"get", "list", "watch"}, "configmaps": {"get", "list", "watch"}}
    binding_namespace = "lesson-a"

    def bound(namespace, resource, verb):
        return namespace == binding_namespace and verb in view_rules.get(resource, set())

    assert bound("lesson-a", "pods", "list")
    assert not bound("lesson-b", "pods", "list")
    assert not bound("lesson-a", "secrets", "list")
    print(
        "k8s-004 synthetic permission, identity and binding-scope checks passed; no API calls made"
    )


if __name__ == "__main__":
    main()
