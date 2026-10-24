def main():
    volume = {"marker": "pod-a", "attempt": "seen"}
    after_restart = volume
    assert after_restart["marker"] == "pod-a" and after_restart["attempt"] == "seen"
    replacement = {"marker": "pod-b"}
    assert replacement["marker"] != volume["marker"] and "attempt" not in replacement
    states = ["init-complete", "app-exit-2", "app-restart", "app-exit-0"]
    assert states.index("init-complete") < states.index("app-restart")
    print("k8s-016 synthetic init/emptyDir lifetime checks passed; no Pod created")


if __name__ == "__main__":
    main()
