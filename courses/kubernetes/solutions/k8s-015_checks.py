def main():
    readiness = {"uid": "pod-a", "ready": False, "restarts": 0, "eligible": False}
    liveness = {"uid": "pod-a", "ready": False, "restarts": 1, "eligible": False}
    assert readiness["uid"] == liveness["uid"] and liveness["restarts"] > readiness["restarts"]
    assert not readiness["eligible"] and readiness["restarts"] == 0
    startup = {"delay_seconds": 3, "periodSeconds": 1, "failureThreshold": 10}
    assert startup["delay_seconds"] < startup["periodSeconds"] * startup["failureThreshold"]
    print("k8s-015 synthetic probe-policy checks passed; timing is not a live receipt")


if __name__ == "__main__":
    main()
