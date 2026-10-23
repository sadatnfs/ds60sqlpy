# python-pandas-02: Explained reference solutions

These answers implement the contracts in [Join Contracts and Point-in-Time Feature Lookup](../companion-guides/py_pandas_02.md). Compare after an attempt. The [executable reference](py_pandas_02_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Require one real identity per dimension row

Validate that key exists, contains no missing values and is unique. Raise ValueError for a missing column, null key or repeated key. An empty frame with the key column is a valid empty dimension.

**Expected:** Keys[a, b] pass; [a, a], [a, None] and a frame without key fail. An empty customer_id column passes.

```python
def validate_dimension(frame: pd.DataFrame, key: str) -> None:
    if key not in frame or frame[key].isna().any() or frame[key].duplicated().any():
        raise ValueError("Dimension keys must exist, be nonmissing and be unique")
```

Uniqueness alone would permit one missing key, but that missing value is not a trustworthy entity identity. Rejecting it prevents pandas null-to-null merge behavior from manufacturing a relationship between unknown entities. An empty dimension has no conflicting identities and is allowed so coverage can be reported downstream. The function checks a structural prerequisite; it does not prove that the chosen key corresponds to the correct business entity.

```python
validate_dimension(pd.DataFrame({"customer_id":["a","b"]}),"customer_id")
validate_dimension(pd.DataFrame({"customer_id":[]}),"customer_id")
expect_value_error(lambda:validate_dimension(pd.DataFrame({"customer_id":["a","a"]}),"customer_id"))
expect_value_error(lambda:validate_dimension(pd.DataFrame({"customer_id":[None]}),"customer_id"))
expect_value_error(lambda:validate_dimension(pd.DataFrame({"x":[1]}),"customer_id"))
```

### Exercise 2: Preserve event grain during enrichment

Require unique nonmissing event_id and a valid customer_id dimension. Left-join dimension segment onto event_id, customer_id, amount events with many-to-one validation and a match indicator. Preserve input event order and do not mutate either frame.

**Expected:** Events for customers a, c, b keep all three event_id values in input order; c has missing segment and left_only status. Duplicate dimension a raises ValueError.

```python
def enrich_events(events: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(events,"event_id");validate_dimension(dimension,"customer_id")
    if not {"customer_id","amount"}.issubset(events.columns) or "segment" not in dimension:
        raise ValueError("Expected event amount and dimension segment")
    return events[["event_id","customer_id","amount"]].merge(dimension[["customer_id","segment"]],on="customer_id",how="left",sort=False,validate="many_to_one",indicator="dimension_status")
```

The merge selects only the declared input columns to avoid accidental suffix collisions with unrelated fields. many_to_one permits multiple events for a customer while requiring one dimension record. A left join preserves event population, and the indicator retains coverage evidence. The output row count and event order are checked independently of segment values, because correct-looking attributes do not prove that events were preserved exactly once.

```python
e=pd.DataFrame({"event_id":[3,1,2],"customer_id":["a","c","b"],"amount":[10,20,30]});d=pd.DataFrame({"customer_id":["a","b"],"segment":["x","y"]})
r=enrich_events(e,d)
assert r.event_id.tolist()==[3,1,2] and r.dimension_status.astype(str).tolist()==["both","left_only","both"]
assert len(r)==len(e) and "segment" not in e
expect_value_error(lambda:enrich_events(e,pd.concat([d,d.iloc[:1]])))
```

### Exercise 3: Separate absent identifiers from unknown identifiers

Return one diagnostic row per unmatched event with columns event_id and reason, sorted by event_id. Label null customer identifiers missing_key and nonnull identifiers absent from the dimension unknown_key. Validate event and dimension identities first.

**Expected:** Events 1:a,2:None,3:z with dimension[a] yield (2, missing_key),(3, unknown_key). A fully matched event yields an empty frame with both output columns.

```python
def missing_key_report(events: pd.DataFrame, dimension: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(events,"event_id");validate_dimension(dimension,"customer_id")
    events=events.reset_index(drop=True)
    missing=events["customer_id"].isna()
    unknown=~events["customer_id"].isin(dimension["customer_id"]) & ~missing
    result=events.loc[missing|unknown,["event_id"]].copy()
    result["reason"]=np.where(missing.loc[result.index],"missing_key","unknown_key")
    return result.sort_values("event_id",kind="stable").reset_index(drop=True)
```

The two reasons lead to different repairs. A missing identifier may require source correction, while an unknown identifier may indicate a late dimension update or a population mismatch. Testing membership alone collapses both into unmatched, so the missing mask is evaluated separately. Sorting by the durable event_id makes diagnostics reproducible without assuming that the DataFrame index is the event identity.

```python
e=pd.DataFrame({"event_id":[3,1,2],"customer_id":["z","a",None]});d=pd.DataFrame({"customer_id":["a"]})
r=missing_key_report(e,d)
assert list(r.itertuples(index=False,name=None))==[(2,"missing_key"),(3,"unknown_key")]
e.index=[0,0,0]
assert list(missing_key_report(e,d).itertuples(index=False,name=None))==[(2,"missing_key"),(3,"unknown_key")]
assert missing_key_report(e[e.event_id==1],d).columns.tolist()==["event_id","reason"]
```

### Exercise 4: Look backward within a freshness limit

For a single history, attach the latest available_at, value no later than each request at time, within a nonnegative tolerance. Require unique request_id and unique history available_at, with nonmissing timezone-aware UTC time columns. Return original request order and preserve unmatched values as missing.

**Expected:** Requests at 10:30 and 15:00 with history at 10:00, value 10 and 12:00, value 20, tolerance 2 hours, yield 10 andmissing. Unsorted requests are restored to their original order; naive times fail.

```python
def latest_available(requests: pd.DataFrame, history: pd.DataFrame, tolerance: pd.Timedelta) -> pd.DataFrame:
    validate_dimension(requests,"request_id");validate_dimension(history,"available_at")
    for series in [requests["at"],history["available_at"]]:
        if not isinstance(series.dtype,pd.DatetimeTZDtype) or str(series.dt.tz)!="UTC" or series.isna().any():
            raise ValueError("Expected nonmissing timezone-aware UTC times")
    if pd.isna(tolerance) or tolerance<pd.Timedelta(0):
        raise ValueError("Expected a nonnegative freshness tolerance")
    left=requests[["request_id","at"]].copy();left["_position"]=np.arange(len(left))
    right=history[["available_at","value"]].sort_values("available_at")
    joined=pd.merge_asof(left.sort_values("at"),right,left_on="at",right_on="available_at",direction="backward",tolerance=tolerance)
    return joined.sort_values("_position").drop(columns="_position").reset_index(drop=True)
```

Sorting is necessary for the temporal algorithm but is not the output identity policy, so an explicit source position restores request order. Backward direction prevents future availability from entering a prediction; tolerance separately enforces freshness. UTC dtype checks refuse silent timezone interpretation. This single-history function must not be applied to several entities without a grouped key, because timestamps alone do not identify whose feature is being retrieved.

```python
r=pd.DataFrame({"request_id":[2,1],"at":pd.to_datetime(["2026-01-01T15:00Z","2026-01-01T10:30Z"])});h=pd.DataFrame({"available_at":pd.to_datetime(["2026-01-01T12:00Z","2026-01-01T10:00Z"]),"value":[20.,10.]})
x=latest_available(r,h,pd.Timedelta("2h"))
assert x.request_id.tolist()==[2,1] and pd.isna(x.loc[0,"value"]) and x.loc[1,"value"]==10
naive=r.copy();naive["at"]=naive["at"].dt.tz_localize(None)
expect_value_error(lambda:latest_available(naive,h,pd.Timedelta("2h")))
```

### Exercise 5: Reject overlapping validity versions

Validate a single version history with unique version_id and finite UTC start, end times satisfying start<end. Return it sorted by start. Reject any overlap, while permitting adjacent intervals where one end equals the next start.

**Expected:** Versions[10:00,11:00) and [11:00,12:00) pass; changing the second start to 10:59 raises ValueError. A zero-width interval also fails.

```python
def validate_intervals(history: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(history,"version_id")
    for series in [history["start"],history["end"]]:
        if not isinstance(series.dtype,pd.DatetimeTZDtype) or str(series.dt.tz)!="UTC" or series.isna().any():
            raise ValueError("Expected finite UTC interval endpoints")
    ordered=history.sort_values("start",kind="stable").copy()
    if (ordered["start"]>=ordered["end"]).any() or (ordered["start"].iloc[1:].to_numpy()<ordered["end"].iloc[:-1].to_numpy()).any():
        raise ValueError("Intervals must be positive and nonoverlapping")
    return ordered
```

After sorting positive intervals by start, any overlap must appear when a later start precedes the preceding interval's end; earlier invalid overlaps are already detected at their adjacent boundary. Equality is permitted because half-open intervals do not both own that instant. Rejecting ambiguity before lookup prevents a last-row-wins rule from silently choosing a version based on storage order. The returned copy allows inspection without mutating the supplied history.

```python
h=pd.DataFrame({"version_id":[1,2],"start":pd.to_datetime(["2026-01-01T10:00Z","2026-01-01T11:00Z"]),"end":pd.to_datetime(["2026-01-01T11:00Z","2026-01-01T12:00Z"]),"value":[10,20]})
assert len(validate_intervals(h))==2
bad=h.copy();bad.loc[1,"start"]=pd.Timestamp("2026-01-01T10:59Z")
expect_value_error(lambda:validate_intervals(bad))
bad=h.copy();bad.loc[0,"end"]=bad.loc[0,"start"]
expect_value_error(lambda:validate_intervals(bad))
```

### Exercise 6: Assign an instant to at most one version

Use validated single-history half-open intervals to attach version_id, value to uniquely identified events at UTC instants. Return event_id, version_id, value in input event order. Preserve uncovered events with missing version/value and reject ambiguous histories.

**Expected:** Events at 10:00,11:00,12:00 against adjacent hourly versions 1,2 yield version 1, version 2, missing. The exact final end is excluded; gaps are not filled by nearest lookup.

```python
def validity_lookup(events: pd.DataFrame, history: pd.DataFrame) -> pd.DataFrame:
    validate_dimension(events,"event_id");ordered=validate_intervals(history)
    if not isinstance(events["at"].dtype,pd.DatetimeTZDtype) or str(events["at"].dt.tz)!="UTC" or events["at"].isna().any():
        raise ValueError("Expected UTC event instants")
    rows=[]
    for event in events[["event_id","at"]].itertuples(index=False):
        match=ordered.loc[(ordered["start"]<=event.at)&(event.at<ordered["end"])]
        if match.empty:
            rows.append((event.event_id,pd.NA,np.nan))
        else:
            rows.append((event.event_id,match.iloc[0]["version_id"],match.iloc[0]["value"]))
    return pd.DataFrame(rows,columns=["event_id","version_id","value"])
```

The lookup expresses both inequalities explicitly, making endpoint ownership visible. Validated nonoverlap ensures that taking the sole matching row is legitimate rather than an arbitrary tie break. Uncovered events remain in the result so absence can be reviewed. The simple row loop is intentional for a tiny fixture; scaling it requires an algorithm preserving the same interval semantics, not replacing the condition with unrestricted nearest-time matching.

```python
e=pd.DataFrame({"event_id":[1,2,3],"at":pd.to_datetime(["2026-01-01T10:00Z","2026-01-01T11:00Z","2026-01-01T12:00Z"])})
r=validity_lookup(e,h)
assert r.event_id.tolist()==[1,2,3] and r.loc[0,"version_id"]==1 and r.loc[1,"version_id"]==2 and pd.isna(r.loc[2,"version_id"])
assert pd.isna(r.loc[2,"value"])
```

## Verification and interpretation

Run `python python/professional/solutions/py_pandas_02_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
