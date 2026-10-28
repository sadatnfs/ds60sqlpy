"""Constraint-based architecture comparison over declared hypothetical scenarios."""


def proposals():
    return [
        {
            "name": "batch",
            "freshness_minutes": 60,
            "latency_ms": 8000,
            "retention_days": 365,
            "cost_units": 20,
            "qualified": False,
        },
        {
            "name": "online",
            "freshness_minutes": 1,
            "latency_ms": 100,
            "retention_days": 7,
            "cost_units": 50,
            "qualified": False,
        },
        {
            "name": "hybrid",
            "freshness_minutes": 2,
            "latency_ms": 200,
            "retention_days": 365,
            "cost_units": 80,
            "qualified": False,
        },
    ]


def choose(candidates, requirements, require_qualification=False):
    decisions = []
    for candidate in candidates:
        reasons = []
        for field in ["freshness_minutes", "latency_ms", "cost_units"]:
            if candidate[field] > requirements[field]:
                reasons.append(field + " exceeds the constraint")
        if candidate["retention_days"] < requirements["retention_days"]:
            reasons.append("retention_days is below the constraint")
        if require_qualification and not candidate["qualified"]:
            reasons.append("actual qualification evidence is absent")
        decisions.append(
            {
                "name": candidate["name"],
                "feasible": not reasons,
                "reasons": reasons,
                "cost_units": candidate["cost_units"],
            }
        )
    feasible = [row for row in decisions if row["feasible"]]
    selected = (
        min(feasible, key=lambda row: (row["cost_units"], row["name"]))["name"]
        if feasible
        else None
    )
    return {"selected": selected, "decisions": decisions}


def example_one():
    daily = {"freshness_minutes": 60, "latency_ms": 10000, "retention_days": 365, "cost_units": 100}
    interactive = {**daily, "freshness_minutes": 2, "latency_ms": 500}
    first, second = choose(proposals(), daily), choose(proposals(), interactive)
    assert first["selected"] == "batch" and second["selected"] == "hybrid"
    assert next(row for row in second["decisions"] if row["name"] == "online")["reasons"] == [
        "retention_days is below the constraint"
    ]
    return {
        "daily_report_scenario": first,
        "interactive_history_scenario": second,
        "numbers_are_design_assumptions_not_engine_benchmarks": True,
    }


def example_two():
    requirements = {
        "freshness_minutes": 2,
        "latency_ms": 500,
        "retention_days": 365,
        "cost_units": 100,
    }
    changed = [
        {**row, "latency_ms": 800} if row["name"] == "hybrid" else row for row in proposals()
    ]
    revised = choose(changed, requirements)
    publication = choose(proposals(), requirements, require_qualification=True)
    assert revised["selected"] is None and publication["selected"] is None
    return {
        "changed_latency_assumption": revised,
        "production_evidence_gate": publication,
        "next_evidence": (
            "measure native end-to-end latency, freshness and restore behavior "
            "under the declared workload"
        ),
        "no_constraint_was_silently_relaxed": True,
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("The same options serve different explicit requirements:", first)
    print("An unsupported choice remains unaccepted:", second)
    publish_table(
        ["design", "feasible_in_interactive_scenario", "reasons"],
        [
            [row["name"], row["feasible"], "; ".join(row["reasons"])]
            for row in first["interactive_history_scenario"]["decisions"]
        ],
        description=(
            "Hypothetical design constraints admit hybrid only; actual "
            "deployment qualification remains absent."
        ),
    )
    publish_report(
        second,
        description=(
            "A changed latency assumption invalidates the provisional choice, "
            "and the separate production evidence gate rejects unqualified options."
        ),
    )


if __name__ == "__main__":
    main()
