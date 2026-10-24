import hashlib


def digest(value):
    return hashlib.sha256(value).hexdigest()


def recovered(api_objects, marker, expected):
    return {"Deployment/hello", "PVC/data-store-0"} <= set(api_objects) and digest(
        marker
    ) == expected


def main():
    expected = digest(b"synthetic-v1")
    objects = ["Deployment/hello", "PVC/data-store-0"]
    assert not recovered(objects, b"empty-replacement", expected)
    assert not recovered([], b"synthetic-v1", expected)
    assert recovered(objects, b"synthetic-v1", expected)
    print("k8s-036 independent synthetic API/data gates passed; no snapshot or restore executed")


if __name__ == "__main__":
    main()
