# python-pandas-03: Explained reference solutions

These answers implement the contracts in [Grouped Transforms, Temporal Windows, and Session Boundaries](../companion-guides/py_pandas_03.md). Compare after an attempt. The [executable reference](py_pandas_03_solution.py) contains the complete implementations and assertions. Each answer explains the mechanism, not just the final value.

## Exercises and reasoning

### Exercise 1: Use transform without changing event grain

For nonmissing customer_id and finite nonnegative amount, return each row amount divided by its customer total, preserving the original index. For an all-zero customer return missing shares rather than dividing zero by zero. Do not mutate frame.

**Expected:** Customers[a, a, b, b] with amounts[1,3,0,0] yield [.25,.75, NaN, NaN]. Duplicate incidental index labels are allowed; a negative amount raises ValueError.

```python
def group_shares(frame: pd.DataFrame) -> pd.Series:
    if frame["customer_id"].isna().any() or not np.isfinite(frame["amount"]).all() or (frame["amount"]<0).any():
        raise ValueError("Expected known customers and finite nonnegative amounts")
    total=frame.groupby("customer_id",sort=False)["amount"].transform("sum")
    return frame["amount"].div(total.where(total.ne(0)))
```

The group total is computed with transform, so it already aligns to each event, including repeated incidental index labels. Replacing zero denominators with missing makes the undefined ratio visible. A zero-total group is not assigned arbitrary equal shares. The nonnegative contract supports the share interpretation; signed accounting adjustments would require a different denominator policy and should not be accepted silently.

```python
f=pd.DataFrame({"customer_id":["a","a","b","b"],"amount":[1.,3.,0.,0.]},index=[0,0,1,1])
r=group_shares(f)
assert np.allclose(r.iloc[:2],[.25,.75]) and r.iloc[2:].isna().all() and r.index.equals(f.index)
bad=f.copy();bad.iloc[0,1]=-1
expect_value_error(lambda:group_shares(bad))
```

### Exercise 2: Lag within customer using a stable tie break

Return event_id and previous_amount for each event, preserving input event order. Sort within customer by at then event_id, and use the previous row only within that customer. Require unique nonmissing event_id, known customer_id and nonmissing UTC timestamps.

**Expected:** For customer a events(id 2, time 10:00, amount 20),(id 1, time 10:00, amount 10),(id 3, time 11:00, amount 30), previous values in original order are 10, missing,20. Another customer starts with missing.

```python
def ordered_lag(events: pd.DataFrame) -> pd.DataFrame:
    if events["event_id"].isna().any() or events["event_id"].duplicated().any() or events["customer_id"].isna().any() or not isinstance(events["at"].dtype,pd.DatetimeTZDtype) or str(events["at"].dt.tz)!="UTC" or events["at"].isna().any():
        raise ValueError("Expected unique event identities, customers and UTC times")
    f=events[["event_id","customer_id","at","amount"]].copy();f["_position"]=np.arange(len(f))
    f=f.sort_values(["customer_id","at","event_id"],kind="stable")
    f["previous_amount"]=f.groupby("customer_id",sort=False)["amount"].shift(1)
    return f.sort_values("_position")[["event_id","previous_amount"]].reset_index(drop=True)
```

Sorting by timestamp alone leaves equal-time event order unspecified. event_id provides a deterministic secondary order for this row-lag question. Grouped shift prevents the final event of one customer from becoming the first event's history for another. The source position column restores the original presentation order after the sequence computation, separating calculation order from output order.

```python
e=pd.DataFrame({"event_id":[2,1,3,4],"customer_id":["a","a","a","b"],"at":pd.to_datetime(["2026-01-01T10:00Z","2026-01-01T10:00Z","2026-01-01T11:00Z","2026-01-01T10:00Z"]),"amount":[20.,10.,30.,99.]})
r=ordered_lag(e)
assert r.event_id.tolist()==[2,1,3,4] and r.loc[0,"previous_amount"]==10 and pd.isna(r.loc[1,"previous_amount"]) and r.loc[2,"previous_amount"]==20 and pd.isna(r.loc[3,"previous_amount"])
```

### Exercise 3: Exclude every current-time event from a prior window

Return event_id and prior_amount for each event over its customer interval[at-window, at). Require unique event IDs, known customers, finite amounts and UTC times; window must be positive. Equal-time events must receive identical prior sums. Empty prior windows have known sum zero.

**Expected:** Customer a amounts at 10:00=1,10:30=2,10:30=3,11:00=4 with a 30-minute window yield prior sums[0,1,1,5]. The lower boundary counts and the current timestamp never counts.

```python
def prior_window_sum(events: pd.DataFrame, window: pd.Timedelta) -> pd.DataFrame:
    ordered_lag(events)
    if pd.isna(window) or window<=pd.Timedelta(0) or not np.isfinite(events["amount"]).all():
        raise ValueError("Expected a positive window and finite amounts")
    by_time=events.groupby(["customer_id","at"],as_index=False,sort=True)["amount"].sum()
    parts=[]
    for customer,group in by_time.groupby("customer_id",sort=False):
        series=group.set_index("at")["amount"]
        prior=series.rolling(window=window,closed="left",min_periods=1).sum().fillna(0)
        part=prior.rename("prior_amount").reset_index();part["customer_id"]=customer;parts.append(part)
    if not parts:
        return pd.DataFrame({"event_id":events["event_id"].copy(),"prior_amount":pd.Series(dtype=float)})
    lookup=pd.concat(parts,ignore_index=True)
    return events[["event_id","customer_id","at"]].merge(lookup,on=["customer_id","at"],how="left",sort=False,validate="many_to_one")[["event_id","prior_amount"]]
```

First aggregating each customer/timestamp instant removes arrival-order ambiguity among tied events. A left-closed time window includes the lower boundary and excludes the current instant. The unique-time result is then joined back with a many-to-one contract, so all events at one instant receive the same historical feature. Filling an empty prior sum with zero is justified here because the fixture is a complete event log, not an unknown measurement stream.

```python
w=pd.DataFrame({"event_id":[1,2,3,4],"customer_id":["a"]*4,"at":pd.to_datetime(["2026-01-01T10:00Z","2026-01-01T10:30Z","2026-01-01T10:30Z","2026-01-01T11:00Z"]),"amount":[1.,2.,3.,4.]})
r=prior_window_sum(w,pd.Timedelta("30min"))
assert r.prior_amount.tolist()==[0,1,1,5] and r.event_id.tolist()==[1,2,3,4]
expect_value_error(lambda:prior_window_sum(w,pd.Timedelta(0)))
```

### Exercise 4: Turn an inactivity rule into session identity

Return event_id and a one-based session_id within each customer, preserving input order. Sort by at, event_id and start a new session only when elapsed gap is strictly greater than the positive threshold. Reuse identity/time validation from ordered_lag.

**Expected:** Times 10:00,10:30,11:01 with 30-minute threshold give sessions 1,1,2. Every other customer starts at 1; zero or negative threshold is rejected.

```python
def session_ids(events: pd.DataFrame, gap: pd.Timedelta) -> pd.DataFrame:
    ordered_lag(events)
    if pd.isna(gap) or gap<=pd.Timedelta(0):
        raise ValueError("Expected a positive inactivity threshold")
    f=events[["event_id","customer_id","at"]].copy();f["_position"]=np.arange(len(f))
    f=f.sort_values(["customer_id","at","event_id"],kind="stable")
    difference=f.groupby("customer_id",sort=False)["at"].diff()
    start=difference.isna()|difference.gt(gap)
    f["session_id"]=start.groupby(f["customer_id"],sort=False).cumsum().astype(int)
    return f.sort_values("_position")[["event_id","session_id"]].reset_index(drop=True)
```

A session is derived from a rule and can change when the threshold changes. Grouped differences expose inactivity, while a cumulative sum of start flags assigns session numbers without a Python counter for each row. The comparison uses greater-than, not greater-than-or-equal, making the exact boundary test essential. Session numbers are local to a customer and must be combined with customer identity when used as a key.

```python
s=pd.DataFrame({"event_id":[1,2,3,4],"customer_id":["a","a","a","b"],"at":pd.to_datetime(["2026-01-01T10:00Z","2026-01-01T10:30Z","2026-01-01T11:01Z","2026-01-01T12:00Z"]),"amount":[1,1,1,1]})
assert session_ids(s,pd.Timedelta("30min")).session_id.tolist()==[1,1,2,1]
expect_value_error(lambda:session_ids(s,pd.Timedelta(0)))
```

### Exercise 5: Choose one final event deterministically

Return one row per customer with customer_id, event_id, at, amount, choosing greatest at then greatest event_id. Sort final rows by customer_id. Validate event/time identity using ordered_lag and preserve the original input.

**Expected:** Two equal-time events for a with IDs 1 and 2 choose 2. Customer b keeps its own last event. Output contains each customer once and sorted customer IDs.

```python
def last_event_per_customer(events: pd.DataFrame) -> pd.DataFrame:
    ordered_lag(events)
    return events.sort_values(["customer_id","at","event_id"],kind="stable").drop_duplicates("customer_id",keep="last")[["customer_id","event_id","at","amount"]].sort_values("customer_id",kind="stable").reset_index(drop=True)
```

The final-row choice is encoded in the sorted key, not whichever event happened to be last in the input. Dropping duplicates after that order preserves exactly the maximal timestamp and ID for each customer. The outer sort states presentation order independently. Groupby.last is not interchangeable when individual columns contain missing values, because it can choose last nonmissing values from different rows and create a record that never existed.

```python
r=last_event_per_customer(e)
assert r.customer_id.tolist()==["a","b"] and r.event_id.tolist()==[3,4]
tied=e[e.event_id.isin([1,2])]
assert last_event_per_customer(tied).event_id.tolist()==[2] and len(e)==4
```

### Exercise 6: Distinguish no rows from no known measurements

Summarize declared unique categories in their declared order with category, row_count, known_count, total. Reject missing/undeclared category labels. Include unobserved categories with row_count0, known_count0, total missing; an observed all-missing category also has missing total.

**Expected:** Rows a:1, a:NA, b:NA and declared [a, b, c] yield counts(2,1),(1,0),(0,0) and totals 1, missing, missing. Unknown category z is rejected.

```python
def category_summary(frame: pd.DataFrame, categories: list[str]) -> pd.DataFrame:
    if len(categories)!=len(set(categories)) or frame["category"].isna().any() or not frame["category"].isin(categories).all():
        raise ValueError("Expected unique declared categories and valid labels")
    f=frame[["category","value"]].copy();f["category"]=pd.Categorical(f["category"],categories=categories,ordered=True)
    result=f.groupby("category",observed=False,sort=True)["value"].agg(row_count="size",known_count="count",total=lambda values:values.sum(min_count=1))
    return result.reset_index()
```

Explicit categorical levels define which absent groups should appear. observed=False retains those levels, and size versus count separates rows from known measurements. min_count=1 prevents an all-missing or empty set from being reported as a measured zero total. The result therefore carries enough evidence to distinguish category b, whose records exist but values are unknown, from c, for which no records were observed.

```python
f=pd.DataFrame({"category":["a","a","b"],"value":pd.Series([1,pd.NA,pd.NA],dtype="Float64")})
r=category_summary(f,["a","b","c"])
assert r.category.tolist()==["a","b","c"] and r.row_count.tolist()==[2,1,0] and r.known_count.tolist()==[1,0,0]
assert r.loc[0,"total"]==1 and pd.isna(r.loc[1,"total"]) and pd.isna(r.loc[2,"total"])
expect_value_error(lambda:category_summary(pd.DataFrame({"category":["z"],"value":[1]}),["a"]))
```

## Verification and interpretation

Run `python python/professional/solutions/py_pandas_03_solution.py` from the repository root with the prepared interpreter. The code checks normal inputs and explicit edge cases before printing its success line. Assertions are the evidence; the printed sentence alone is not. The helper `expect_value_error` requires an actual `ValueError` and fails if a function silently accepts an invalid input. Inspect each function's mutation and ordering behavior as part of its contract.
