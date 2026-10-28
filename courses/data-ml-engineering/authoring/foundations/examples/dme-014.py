"""Explicit event/knowledge clocks and retained request-population coverage."""


def select_known(records, cutoff):
    eligible = [
        row for row in records if row["event_hour"] <= cutoff and row["known_hour"] <= cutoff
    ]
    if not eligible:
        return None
    latest = max(eligible, key=lambda row: (row["event_hour"], row["known_hour"]))
    tied = [
        row["value"]
        for row in eligible
        if (row["event_hour"], row["known_hour"]) == (latest["event_hour"], latest["known_hour"])
    ]
    if len(set(tied)) != 1:
        raise ValueError("Conflicting values share the same declared event/version clocks")
    return latest["value"]


def example_one():
    records = [
        {"event_hour": 2, "known_hour": 3, "value": 10},
        {"event_hour": 4, "known_hour": 8, "value": 999},
        {"event_hour": 6, "known_hour": 6, "value": 20},
    ]
    values = [select_known(records, cutoff) for cutoff in (5, 7, 9)]
    assert values == [10, 20, 20]
    event_only = max(
        (row for row in records if row["event_hour"] <= 5), key=lambda row: row["event_hour"]
    )["value"]
    last_arrived = max(records, key=lambda row: row["known_hour"])["value"]
    assert event_only == last_arrived == 999
    return {
        "records": records,
        "cutoffs": [5, 7, 9],
        "eligible_values": values,
        "event_only_leak_at_hour_5": event_only,
        "last_arrival_is_not_latest_event": last_arrived,
    }


def example_two():
    records = [
        {"event_hour": 2, "known_hour": 3, "value": 0},
        {"event_hour": 6, "known_hour": 6, "value": 20},
    ]
    requests = [
        {"request_id": "early", "cutoff": 1},
        {"request_id": "zero", "cutoff": 5},
        {"request_id": "later", "cutoff": 7},
    ]
    result = [
        {**request, "value": select_known(records, request["cutoff"])} for request in requests
    ]
    known = [row for row in result if row["value"] is not None]
    assert [row["value"] for row in result] == [None, 0, 20]
    assert len(result) == 3 and len(known) == 2
    assert [row["request_id"] for row in known] == ["zero", "later"]
    conflicting = [*records, {"event_hour": 6, "known_hour": 6, "value": 99}]
    try:
        select_known(conflicting, 7)
    except ValueError:
        conflict_rejected = True
    else:
        raise AssertionError("Ambiguous same-clock facts must not depend on input order")
    return {
        "requests": result,
        "known_coverage": len(known) / len(result),
        "zero_is_a_known_value": True,
        "same_clock_conflict_rejected": conflict_rejected,
    }


def main():
    import plotly.graph_objects as go

    from ds60sqlpy.plot_artifacts import publish_report

    first, second = example_one(), example_two()
    records = first["records"]
    figure = go.Figure(
        go.Scatter(
            x=[row["event_hour"] for row in records],
            y=[row["known_hour"] for row in records],
            mode="markers+text",
            text=[str(row["value"]) for row in records],
            textposition="top center",
            name="Synthetic observations",
        )
    )
    figure.add_vline(x=5, line_dash="dash")
    figure.add_hline(y=5, line_dash="dash")
    figure.update_layout(
        template=None,
        title="Two clocks at decision hour 5",
        xaxis_title="Event hour",
        yaxis_title="Known hour",
        meta={
            "description": (
                "Only the observation with event hour 2 and known hour "
                "3 is eligible at hour 5; the late-known value 999 is "
                "excluded."
            ),
            "table": {
                "columns": ["event_hour", "known_hour", "value"],
                "rows": [[row["event_hour"], row["known_hour"], row["value"]] for row in records],
            },
        },
    )
    figure.show()
    publish_report(
        second,
        description=(
            "All three prediction requests are retained; unknown and measured zero are distinct."
        ),
    )
    print("Values at decision hours 5, 7, 9:", first["eligible_values"])
    print("Retained request population:", second["requests"])


if __name__ == "__main__":
    main()
