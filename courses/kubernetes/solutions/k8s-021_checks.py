def allowed(labels, port):
    return labels.get("role") == "lesson-client" and port == 8080


def main():
    assert allowed({"role": "lesson-client"}, 8080)
    assert not allowed({"role": "other"}, 8080) and not allowed({"role": "lesson-client"}, 9999)
    before = {"allowed": True, "other": True}
    after = {"allowed": True, "other": False}
    assert before["other"] and not after["other"] and after["allowed"]
    print("k8s-021 synthetic policy logic passed; CNI enforcement requires live evidence")


if __name__ == "__main__":
    main()
