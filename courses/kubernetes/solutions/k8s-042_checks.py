REQUIRED = (
    "capability",
    "api",
    "authorization",
    "admission",
    "controller",
    "application",
    "data",
    "recovery",
    "cleanup",
)


def accept(packet):
    return all(packet.get(key) == "pass" for key in REQUIRED)


def main():
    complete = {key: "pass" for key in REQUIRED}
    assert accept(complete)
    for key in REQUIRED:
        assert not accept({**complete, key: "unavailable"})
        assert not accept({k: v for k, v in complete.items() if k != key})
    assert not accept({**complete, "data": "wrong-hash", "cleanup": "unknown"})
    print("k8s-042 synthetic all-gates capstone passed; no advanced host operation executed")


if __name__ == "__main__":
    main()
