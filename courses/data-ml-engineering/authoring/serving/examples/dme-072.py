"""Source-bound release decisions require independent functional and operational evidence."""

import hashlib
import json


def decide(evidence):
    required = {
        "same_source",
        "cache_equivalence",
        "bounded_admission",
        "cancellation_release",
        "exact_replay",
        "no_external_downloads",
    }
    missing = sorted(required - evidence.keys())
    failed = sorted(key for key in required & evidence.keys() if evidence[key] is not True)
    return {
        "ship_local_cpu": not missing and not failed,
        "missing": missing,
        "failed": failed,
        "gpu_qualified": evidence.get("actual_gpu_probe") is True,
    }


def example_one():
    evidence = dict.fromkeys(
        [
            "same_source",
            "cache_equivalence",
            "bounded_admission",
            "cancellation_release",
            "exact_replay",
            "no_external_downloads",
        ],
        True,
    )
    decision = decide(evidence)
    assert decision["ship_local_cpu"] and not decision["gpu_qualified"]
    source = b"synthetic locally trained inference workshop"
    memo = {
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "decision": decision,
        "limitations": [
            "synthetic corpus",
            "one CPU slot",
            "no pretrained quality claim",
            "no GPU benchmark",
        ],
    }
    print(json.dumps(memo, indent=2))


def example_two():
    evidence = {
        "same_source": True,
        "cache_equivalence": True,
        "bounded_admission": True,
        "cancellation_release": False,
        "exact_replay": True,
        "no_external_downloads": True,
    }
    decision = decide(evidence)
    assert not decision["ship_local_cpu"] and decision["failed"] == ["cancellation_release"]
    print("Block release:", decision)
    print("Passing model arithmetic cannot compensate for leaked reservations after cancellation.")


def main():
    example_one()
    example_two()


if __name__ == "__main__":
    main()
