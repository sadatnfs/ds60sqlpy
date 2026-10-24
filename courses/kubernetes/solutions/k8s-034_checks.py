def selects(selector, labels):
    return all(labels.get(k) == v for k, v in selector.items())


def gate(samples, marker, count=4):
    return len(samples) == count and all(x == marker for x in samples)


def main():
    selector = {"app": "hello", "release": "stable"}
    assert selects(selector, {"app": "hello", "release": "stable"})
    assert not selects(selector, {"app": "hello", "release": "candidate"})
    assert not gate(["reviewer", "reviewer", "ERROR", "reviewer"], "reviewer")
    assert gate(["hello"] * 4, "hello")
    print("k8s-034 synthetic selector and release gates passed; no live traffic changed")


if __name__ == "__main__":
    main()
