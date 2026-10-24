def main():
    rows = ["10", "0", "bad", "-2", "25"]
    accepted = [int(x) for x in rows if x.isascii() and x.isdigit()]
    assert accepted == [10, 0, 25] and len(rows) - len(accepted) == 2 and sum(accepted) == 35
    spec = {"completions": 1, "parallelism": 1, "backoffLimit": 0, "activeDeadlineSeconds": 20}
    assert (
        spec["completions"] == spec["parallelism"] == 1 and 5 <= spec["activeDeadlineSeconds"] <= 30
    )
    cron = {"suspend": True, "timeZone": "Etc/UTC", "schedule": "*/5 * * * *"}
    assert cron["suspend"] and cron["timeZone"] == "Etc/UTC"
    print("k8s-011 synthetic task and schedule checks passed; no recurring workload started")


if __name__ == "__main__":
    main()
