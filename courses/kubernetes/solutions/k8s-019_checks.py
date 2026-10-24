import base64


def main():
    dummy = "DUMMY_LESSON_ONLY"
    encoded = base64.b64encode(dummy.encode()).decode()
    assert base64.b64decode(encoded, validate=True).decode() == dummy
    before = {"environment": "A", "file": "A", "application": "A"}
    projected = {**before, "file": "B"}
    assert (
        projected["environment"] == "A"
        and projected["application"] == "A"
        and projected["file"] == "B"
    )
    print("k8s-019 synthetic encoding/lifetime checks passed; no Secret API access")


if __name__ == "__main__":
    main()
