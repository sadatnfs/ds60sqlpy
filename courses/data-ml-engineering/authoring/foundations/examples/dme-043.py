"""Request-based SLO arithmetic over declared observations, not a live monitoring service."""

from fractions import Fraction


def indicators(requests, latency_limit=200):
    eligible = [row for row in requests if row["eligible"]]
    if not eligible:
        raise ValueError("An empty eligible population has no observed service rate")
    available = sum(200 <= row["status"] < 400 for row in eligible)
    timely_success = sum(
        200 <= row["status"] < 400 and row["latency_ms"] <= latency_limit for row in eligible
    )
    return {
        "eligible": len(eligible),
        "excluded": len(requests) - len(eligible),
        "available": available,
        "timely_success": timely_success,
        "bad": len(eligible) - timely_success,
    }


def burn(summary, target=Fraction(995, 1000)):
    if not 0 < target < 1:
        raise ValueError("The target must leave a positive error budget")
    return Fraction(summary["bad"], summary["eligible"]) / (1 - target)


def example_one():
    rows = [
        {
            "time": i,
            "eligible": True,
            "status": 503 if i < 5 else 200,
            "latency_ms": 300 if 5 <= i < 25 else 100,
        }
        for i in range(1000)
    ]
    rows.extend(
        [
            {"time": 1000, "eligible": False, "status": 200, "latency_ms": 10},
            {"time": 1000, "eligible": False, "status": 400, "latency_ms": 10},
        ]
    )
    result = indicators(rows)
    assert result == {
        "eligible": 1000,
        "excluded": 2,
        "available": 995,
        "timely_success": 975,
        "bad": 25,
    }
    assert burn(result) == 5
    allowed = Fraction(result["eligible"]) * (1 - Fraction(995, 1000))
    assert allowed == 5
    return {
        "observations": result,
        "availability_rate": 0.995,
        "timely_success_rate": 0.975,
        "allowed_bad_requests_at_target": int(allowed),
        "latency_and_success_burn": float(burn(result)),
        "policy": (
            "health and invalid-input fixture requests excluded; service overload remains eligible"
        ),
    }


def example_two():
    bad = {810, 820, 830, 840, 850, 860, 982, 987, 992, 997}
    rows = [
        {"time": i, "eligible": True, "status": 503 if i in bad else 200, "latency_ms": 100}
        for i in range(1000)
    ]
    whole = indicators(rows)
    slow = indicators([row for row in rows if row["time"] >= 800])
    fast = indicators([row for row in rows if row["time"] >= 980])
    assert (whole["bad"], slow["bad"], fast["bad"]) == (10, 10, 4)
    rates = {
        "whole": float(burn(whole)),
        "last_200": float(burn(slow)),
        "last_20": float(burn(fast)),
    }
    assert rates == {"whole": 2.0, "last_200": 10.0, "last_20": 40.0}
    alert = (
        fast["eligible"] >= 20 and slow["eligible"] >= 200 and burn(fast) > 14 and burn(slow) > 6
    )
    assert alert
    return {
        "burn_by_window": rates,
        "both_windows_pass_declared_alert_rule": alert,
        "thresholds_are_illustrative_not_a_universal_paging_policy": True,
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Separate availability from timely success:", first)
    print("A recent burst needs shorter windows:", second)
    publish_table(
        ["window", "burn_ratio"],
        [[key, value] for key, value in second["burn_by_window"].items()],
        description=(
            "Declared synthetic observation windows burn the 0.5 percent "
            "bad-request budget at 2, 10 and 40 times the target rate."
        ),
    )
    publish_report(
        first,
        description=(
            "Explicit eligible denominators, separate availability and "
            "latency success, and error-budget arithmetic."
        ),
    )


if __name__ == "__main__":
    main()
