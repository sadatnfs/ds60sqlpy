"""python-pandas-06: complete time-zone, DST and calendar references.

Only small original event fixtures are used. A local calendar date is not a
fixed-duration UTC window, and duplicate wall times need an explicit policy.
"""

from __future__ import annotations

import re
from datetime import date

import pandas as pd  # type: ignore[import-untyped]

_AWARE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?(?:Z|[+-]\d{2}:\d{2})\Z"
)
_LOCAL = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d{1,9})?)?\Z")


def _zone_name(zone: str) -> None:
    if not isinstance(zone, str) or not zone:
        raise ValueError("Expected an explicit nonempty time-zone name")


def _aware_index(instants: pd.DatetimeIndex) -> None:
    if not isinstance(instants, pd.DatetimeIndex) or instants.tz is None or instants.hasnans:
        raise ValueError("Expected a timezone-aware DatetimeIndex without NaT")


def _calendar_date(text: str) -> date:
    if not isinstance(text, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) is None:
        raise ValueError("Expected an ISO calendar date YYYY-MM-DD")
    return date.fromisoformat(text)


# Exercise 1: Require explicit offset evidence.
def parse_instants(texts: list[str]) -> pd.DatetimeIndex:
    """Parse explicit-offset ISO timestamps, preserve order, and normalize to UTC."""
    if not isinstance(texts, list) or any(
        not isinstance(text, str) or _AWARE.fullmatch(text) is None for text in texts
    ):
        raise ValueError("Each timestamp needs an explicit Z or numeric UTC offset")
    values = [pd.Timestamp(text).tz_convert("UTC") for text in texts]
    return pd.DatetimeIndex(values, tz="UTC")


# Exercise 2: Resolve repeated and nonexistent wall clocks.
def localize_wall_times(
    texts: list[str],
    zone: str,
    choices: list[bool] | None = None,
    gap: str = "raise",
) -> pd.DatetimeIndex:
    """Interpret naive wall times under explicit ambiguous/nonexistent policies.

    choices follows pandas' ambiguous Boolean rule: True selects a DST
    occurrence. In the New York fall fixture that is the earlier occurrence.
    shift_forward changes a nonexistent input, which must be disclosed.
    """
    _zone_name(zone)
    if (
        not isinstance(texts, list)
        or any(not isinstance(text, str) or _LOCAL.fullmatch(text) is None for text in texts)
        or not isinstance(gap, str)
        or gap not in {"raise", "shift_forward"}
        or (
            choices is not None
            and (
                not isinstance(choices, list)
                or len(choices) != len(texts)
                or any(type(choice) is not bool for choice in choices)
            )
        )
    ):
        raise ValueError("Expected naive ISO wall times and one explicit Boolean per decision")
    naive = pd.DatetimeIndex([pd.Timestamp(text) for text in texts])
    try:
        return naive.tz_localize(
            zone, ambiguous="raise" if choices is None else choices, nonexistent=gap
        )
    except Exception as error:
        # pandas' timezone providers expose different exception classes. Keep
        # their original cause, while this exercise exposes one ValueError API.
        raise ValueError("Wall time cannot be localized under the selected policy") from error


# Exercise 3: Change display without moving events.
def convert_instants(instants: pd.DatetimeIndex, zone: str) -> pd.DatetimeIndex:
    """Change display timezone while preserving absolute instants and row order."""
    _aware_index(instants)
    _zone_name(zone)
    return instants.tz_convert(zone)


# Exercise 4: Build half-open calendar-day membership and coverage.
def daily_summary(
    instants: pd.DatetimeIndex, values: list[int | None], zone: str, day: str
) -> dict[str, object]:
    """Summarize a complete tiny fixture inside one half-open local calendar day.

    Values are positional integer-cent measurements, not an independently
    indexed Series. Unknown amounts remain unknown in the accepted total.
    """
    _aware_index(instants)
    _zone_name(zone)
    current = _calendar_date(day)
    if (
        not isinstance(values, list)
        or len(values) != len(instants)
        or any(value is not None and type(value) is not int for value in values)
    ):
        raise ValueError("Expected one integer-cent or None measurement per instant")
    start = pd.Timestamp(current).tz_localize(zone, ambiguous="raise", nonexistent="raise")
    # Advance the naive local calendar first, then localize. Adding 24 elapsed
    # hours to an aware midnight would not select the next local midnight.
    end = (pd.Timestamp(current) + pd.DateOffset(days=1)).tz_localize(
        zone, ambiguous="raise", nonexistent="raise"
    )
    selected = (instants >= start) & (instants < end)
    amounts = [value for value, keep in zip(values, selected, strict=True) if keep]
    known = [value for value in amounts if value is not None]
    known_sum = sum(known)
    return {
        "local_day": day,
        "start_utc": start.tz_convert("UTC").isoformat(),
        "end_utc": end.tz_convert("UTC").isoformat(),
        "elapsed_hours": (end - start).total_seconds() / 3600,
        "event_count": len(amounts),
        "known_count": len(known),
        "known_sum": known_sum,
        "accepted_total": known_sum if len(known) == len(amounts) else None,
    }


# Exercise 5: Distinguish timeline duration from displayed clock difference.
def elapsed_and_wall(start: str, end: str, zone: str) -> tuple[pd.Timedelta, pd.Timedelta]:
    """Compare elapsed duration with the difference between displayed wall clocks."""
    instants = parse_instants([start, end])
    if instants[1] < instants[0]:
        raise ValueError("Expected an interval whose end is not before its start")
    local = convert_instants(instants, zone).tz_localize(None)
    return instants[1] - instants[0], local[1] - local[0]


# Exercise 6: Resample a complete explicit local date window.
def daily_event_counts(
    instants: pd.DatetimeIndex, zone: str, first_day: str, end_day: str
) -> pd.DataFrame:
    """Count all local days in an explicit complete-fixture date window.

    first_day is inclusive, end_day exclusive; allow 1 through 366 calendar
    days. Counts retain zero days and never assume 24 elapsed hours per day.
    """
    _aware_index(instants)
    _zone_name(zone)
    first = _calendar_date(first_day)
    end = _calendar_date(end_day)
    if not 1 <= (end - first).days <= 366:
        raise ValueError("Expected a positive calendar window of at most 366 days")
    boundaries = pd.date_range(first, end, freq="D").tz_localize(
        zone, ambiguous="raise", nonexistent="raise"
    )
    local = instants.tz_convert(zone)
    selected = local[(local >= boundaries[0]) & (local < boundaries[-1])]
    counts = (
        pd.Series(1, index=selected, dtype="int64")
        .resample("D", closed="left", label="left")
        .sum()
        .reindex(boundaries[:-1], fill_value=0)
    )
    return pd.DataFrame(
        {
            "local_day": [stamp.date().isoformat() for stamp in boundaries[:-1]],
            "start_utc": [stamp.tz_convert("UTC").isoformat() for stamp in boundaries[:-1]],
            "end_utc": [stamp.tz_convert("UTC").isoformat() for stamp in boundaries[1:]],
            "elapsed_hours": [
                (b - a).total_seconds() / 3600
                for a, b in zip(boundaries[:-1], boundaries[1:], strict=True)
            ],
            "event_count": counts.to_numpy(),
        }
    )


def verify_examples() -> None:
    zone = "America/New_York"
    repeated = parse_instants(["2026-11-01T01:30:00-04:00", "2026-11-01T01:30:00-05:00"])
    assert [stamp.hour for stamp in repeated] == [5, 6]
    resolved = localize_wall_times(
        ["2026-11-01T01:30:00", "2026-11-01T01:30:00"], zone, [True, False]
    )
    assert resolved.tz_convert("UTC").equals(repeated)
    for texts in (["2026-11-01T01:30:00"], ["2026-03-08T02:30:00"]):
        try:
            localize_wall_times(texts, zone)
        except ValueError:
            pass
        else:
            raise AssertionError("An unresolved wall clock must be rejected")
    shifted = localize_wall_times(["2026-03-08T02:30:00"], zone, gap="shift_forward")
    assert shifted[0].hour == 3 and shifted[0].minute == 0
    converted = convert_instants(repeated, zone)
    assert converted.asi8.tolist() == repeated.asi8.tolist()
    assert [stamp.hour for stamp in converted] == [1, 1]
    events = parse_instants(
        [
            "2026-03-08T04:59:59Z",
            "2026-03-08T05:00:00Z",
            "2026-03-09T03:59:59Z",
            "2026-03-09T04:00:00Z",
        ]
    )
    spring = daily_summary(events, [99, 10, None, 88], zone, "2026-03-08")
    assert spring["elapsed_hours"] == 23 and spring["event_count"] == 2
    assert spring["known_sum"] == 10 and spring["accepted_total"] is None
    fall = daily_summary(repeated, [2, 3], zone, "2026-11-01")
    assert fall["elapsed_hours"] == 25 and fall["accepted_total"] == 5
    elapsed, wall = elapsed_and_wall("2026-03-08T06:30:00Z", "2026-03-08T07:30:00Z", zone)
    assert elapsed == pd.Timedelta(hours=1) and wall == pd.Timedelta(hours=2)
    elapsed, wall = elapsed_and_wall("2026-11-01T05:30:00Z", "2026-11-01T06:30:00Z", zone)
    assert elapsed == pd.Timedelta(hours=1) and wall == pd.Timedelta(0)
    table = daily_event_counts(events, zone, "2026-03-07", "2026-03-10")
    assert table.event_count.tolist() == [1, 2, 1]
    assert table.elapsed_hours.tolist() == [24, 23, 24]
    assert daily_event_counts(
        parse_instants([]), zone, "2026-11-01", "2026-11-03"
    ).event_count.tolist() == [0, 0]
    print("python-pandas-06: all six time-zone and calendar contracts passed")


if __name__ == "__main__":
    verify_examples()
