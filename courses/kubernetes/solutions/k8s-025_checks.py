def review(objects):
    for obj in objects:
        if obj["kind"] not in {"Deployment", "Service", "ConfigMap"}:
            return False
        if "helm.sh/hook" in obj.get("metadata", {}).get("annotations", {}):
            return False
    return True


def main():
    assert review([{"kind": "Deployment", "metadata": {"name": "hello"}}])
    assert not review(
        [{"kind": "Job", "metadata": {"annotations": {"helm.sh/hook": "post-install"}}}]
    )
    assert not review([{"kind": "ClusterRole", "metadata": {"name": "wide"}}])

    def values_ok(values):
        return set(values) <= {"replicas"} and values.get("replicas", 1) in (1, 2)

    assert values_ok({}) and values_ok({"replicas": 2})
    assert not values_ok({"replicas": 3}) and not values_ok({"replicas": 1, "extra": True})
    print("k8s-025 synthetic rendered-object review passed; Helm execution is separate")


if __name__ == "__main__":
    main()
