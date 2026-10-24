import copy


def differences(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        result = []
        for key in sorted(set(a) | set(b)):
            result += differences(a.get(key), b.get(key), path + "." + key)
        return result
    return [] if a == b else [path.lstrip(".")]


def main():
    dev = {"metadata": {"name": "hello"}, "spec": {"replicas": 1, "image": "fixed"}}
    test = copy.deepcopy(dev)
    test["spec"]["replicas"] = 2
    assert differences(dev, test) == ["spec.replicas"]
    owners = {"spec.replicas": "teacher-controller"}
    assert owners["spec.replicas"] != "lesson-review"
    print("k8s-024 synthetic overlay/ownership checks passed; no renderer or apply inferred")


if __name__ == "__main__":
    main()
