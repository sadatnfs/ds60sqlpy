# polars-014: As-of joins and knowledge available at prediction time

## Level and prerequisites

Advanced. Direct prerequisites: `polars-006`, `polars-007`, `polars-009`

**Outcome:** Reconstruct features using only information eligible at each prediction time.

## Question and mechanism

An as-of join matches a record to a nearby key value rather than requiring exact equality. For historical features, a backward match can select the latest recorded feature at or before a request time. A forward match can select future information. The direction is therefore a scientific and deployment assumption, not a cosmetic option.

A time key must be ordered within the relevant entity. A tolerance can prevent an old feature from being used beyond its permitted age. These controls still do not automatically establish what information was available when the prediction was made. A record may describe an old event but arrive much later. Reconstructing past decisions requires both event time and known/available time when late data or revisions are possible.

The second case uses a deliberately small candidate join to demonstrate the two-clock rule. It is inspectable, but a large unrestricted join can be expensive. The goal is to establish correct semantics first, then design an indexed or versioned implementation that preserves them. A feature-store product must be evaluated against this contract rather than assumed to solve every form of historical leakage.

## Syntax and data contract

join_asof uses sorted keys, a strategy and optional tolerance. For a backward lookup, verify that the matched feature time does not exceed the request cutoff. For bitemporal selection, filter candidates by both event<=cutoff and known<=cutoff, then choose the latest eligible version using a complete tie-break rule. Preserve requests with no eligible feature under an explicit missing-value policy.

## Mathematical interpretation

Eligibility at prediction time \(t\) requires \(t_{\mathrm{event}}\le t\) and \(t_{\mathrm{known}}\le t\) under this policy. A freshness requirement additionally bounds \(t-t_{\mathrm{feature}}\). The latest eligible record is selected only after these conditions are applied.

## Run the lesson

Open this subject in `/classroom`, then show its code and notes. The prepared `data-engineering` worker runs `main.py` in a fresh temporary directory. The examples use installed packages and synthetic local fixtures; no account, cloud service, network request or package download is required. Save source and notes before switching lessons. Temporary databases, project files and tracking artifacts are recreated by each complete program and removed after the job. The classroom retains the submitted source and bounded output, not an indefinitely running external service. The guide distinguishes this local execution from the deployment decisions that need an owned production environment.



## Worked case 1: Observe backward and forward matching

The first case uses integer times so every match can be checked by inspection. Backward matching selects the most recent eligible value; forward matching demonstrates the lookahead values that a prediction must not receive.

**Expected evidence:** Backward values are [10,20,30]; forward values are [20,30,null].

```python
import polars as pl


def example_one():
    requests = pl.DataFrame({"id": [1, 2, 3], "time": [2, 5, 9]}).sort("time")
    features = pl.DataFrame({"time": [1, 4, 8], "value": [10, 20, 30]}).sort("time")
    past = requests.join_asof(features, on="time", strategy="backward", tolerance=2)
    future = requests.join_asof(features, on="time", strategy="forward")
    assert past["value"].to_list() == [10, 20, 30]
    assert future["value"].to_list() == [20, 30, None]
    return {"past_only": past.to_dicts(), "lookahead_counterexample": future.to_dicts()}


if __name__ == "__main__":
    print(example_one())
```


## Worked case 2: Reject a late-known revision

At cutoff 5, the feature with event time 4 has not become known until 7. An event-time-only pipeline selects 999, while the two-clock policy correctly retains 10. At cutoff 9, value 30 is eligible under both clocks.

**Expected evidence:** Available values are [10,30]; the leaking event-only result is [999,30].

```python
import polars as pl


def example_two():
    requests = pl.DataFrame({"request": [1, 2], "customer": [10, 10], "cutoff": [5, 9]})
    features = pl.DataFrame(
        {"customer": [10, 10, 10], "event": [2, 4, 8], "known": [3, 7, 8], "value": [10, 999, 30]}
    )
    candidates = requests.join(features, on="customer").filter(
        (pl.col("event") <= pl.col("cutoff")) & (pl.col("known") <= pl.col("cutoff"))
    )
    correct = (
        candidates.sort("request", "event", "known").group_by("request", maintain_order=True).last()
    )
    assert correct["value"].to_list() == [10, 30]
    leaking = (
        requests.join(features, on="customer")
        .filter(pl.col("event") <= pl.col("cutoff"))
        .sort("request", "event")
        .group_by("request", maintain_order=True)
        .last()
    )
    assert leaking["value"].to_list() == [999, 30]
    return {"available_values": [10, 30], "event_time_only_values": [999, 30]}


if __name__ == "__main__":
    print(example_two())
```


## Practice

Make each requested change in a saved copy. Compare both the expected result and the deliberately changed assumption. The separate reference explains the answers.


### 1. Tighten freshness

Change tolerance from 2 to 0 in the first case.

**Check:** No unequal-time feature is matched.

**Hint:** A zero tolerance requires equal keys.


### 2. Add an entity key

Create two customers with overlapping timestamps.

**Check:** No match crosses customer identity.

**Hint:** Temporal closeness alone is insufficient.


### 3. Change availability

Move the late revision known time from 7 to 4.

**Check:** It becomes eligible at cutoff 5.

**Hint:** Apply the same inequality to both clocks.


### 4. Test exact boundaries

Set a feature known time equal to the prediction cutoff.

**Check:** It is included only under the stated inclusive policy.

**Hint:** Boundary conventions must be explicit.


### 5. Preserve unmatched requests

Add a request before every available feature.

**Check:** The request remains identifiable with a missing-feature reason.

**Hint:** An inner candidate join can drop it.


### 6. Review a feature store

State the two temporal questions you would test in a real store.

**Check:** They concern event validity and historical availability.

**Hint:** A point-in-time API name is not complete evidence.


## Diagnose errors and misleading results

A perfectly sorted as-of result can still leak late-known information. Diagnose direction, tolerance, entity keys and revision selection independently. Large candidate joins can also multiply rows; reduce only after applying the full eligibility rule, and verify one result per request before publication.

## Transfer to independent work

Reconstruct features using only information eligible at each prediction time. Test a late arrival, a stale feature, a timestamp tie and an unmatched request. Carry those semantics into the later Feast and ML engineering lessons, where library behavior is checked against explicit temporal fixtures.

## Primary references

- [Polars documentation: As-of joins and knowledge available at prediction time](https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.join_asof.html)
- [Polars Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)

## Tutor guidance

Use the repository learning-companion skill for `polars-014`. Inspect the learner's own source and observations, ask for an explanation of the relevant data or state contract, and give a focused hint. Separate an assertion on this fixture from a claim about an external dataset or deployed service.
