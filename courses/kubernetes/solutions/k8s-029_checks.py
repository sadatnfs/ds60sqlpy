def valid(spec):
    return (
        isinstance(spec, dict)
        and set(spec) == {"message", "replicas"}
        and spec["message"] in ("hello", "reviewer")
        and type(spec["replicas"]) is int
        and 1 <= spec["replicas"] <= 2
    )


def main():
    assert valid({"message": "hello", "replicas": 1})
    for value in ("2", 3, True):
        assert not valid({"message": "hello", "replicas": value})
    assert not valid({"replicas": 1})
    assert not valid({"message": "hello", "replicas": 1, "replcias": 2})
    assert 6 != 7
    print("k8s-029 strict synthetic subset passed; server pruning and admission are not simulated")


if __name__ == "__main__":
    main()
