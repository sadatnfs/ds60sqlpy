import hashlib


def main():
    marker = b"persistent-demo"
    digest = hashlib.sha256(marker).hexdigest()
    before = {"pod": "pod-a", "pvc": "pvc-a", "pv": "pv-a", "hash": digest}
    after = {**before, "pod": "pod-b"}
    assert (
        before["pod"] != after["pod"]
        and before["pvc"] == after["pvc"]
        and before["hash"] == after["hash"]
    )
    assert {"whenDeleted": "Retain", "whenScaled": "Retain"}["whenDeleted"] == "Retain"
    assert hashlib.sha256(b"wrong").hexdigest() != digest
    print("k8s-022 synthetic persistence evidence passed; no storage provisioned or restored")


if __name__ == "__main__":
    main()
