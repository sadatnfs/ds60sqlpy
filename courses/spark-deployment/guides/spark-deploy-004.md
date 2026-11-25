# spark-deploy-004: Submit a bounded distributed fit

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-003`, `spark-022`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Fit from summaries without collecting observations

The first application generates 100,000 integer inputs inside Spark and eight partitions. Each executor computes count, sum of x, sum of squared x, sum of y and sum of xy for the deterministic relation \(y = 3 + 2x\). Only eight small records return to the driver. The driver solves the two-parameter least-squares normal equations and checks intercept 3 and slope 2 independently.

This is a real distributed fitting calculation with a deliberately simple analytic solution. It is not the independent modeling package and does not exercise its numerical optimizers or native backend. Future inputs 100000 and 100001 yield 200003 and 200005. These are deterministic future-covariate extrapolations, not conditional-history forecasts or uncertainty intervals.

## Key terms

- **Submission:** Sending an application to the cluster manager with spark-submit from the driver container.
- **Partition summary:** The count, sum of x, sum of x squared, sum of y and sum of xy that one partition returns instead of its rows.
- **Normal equations:** The two-parameter least-squares system the driver solves from the partition summaries.
- **Correctness oracle:** The independently known values, intercept 3 and slope 2, that the fitted coefficients must match.
- **Future-covariate extrapolation:** A deterministic prediction at a new input such as 100000, which is not a conditional-history forecast or an interval.

## Worked case A: submit and inspect the bounded fit

```sh
python3 lab.py submit --hold-seconds 60
```

Each partition reduces its rows to five sufficient statistics before anything
returns to the driver:

From [`projects/cluster-lab/app/bounded_job.py`](../projects/cluster-lab/app/bounded_job.py):

```python
def partition_summary(rows, pause_seconds):
    context = TaskContext.get()
    n = sx = sxx = sy = sxy = 0
    for row in rows:
        x = int(row.id)
        y = 3 + 2 * x
        n += 1
        sx += x
        sxx += x * x
        sy += y
        sxy += x * y
    time.sleep(pause_seconds)
    yield {
        "partition": context.partitionId(),
        "attempt": context.attemptNumber(),
        "host": socket.gethostname(),
        "python_pid": os.getpid(),
        "n": n,
        "sx": sx,
        "sxx": sxx,
        "sy": sy,
        "sxy": sxy,
    }
```

The driver adds the per-partition `n`, `sx`, `sxx`, `sy` and `sxy` values and solves
the least-squares line from those totals, so only one small dictionary per
partition crosses the network. `TaskContext` records which partition and attempt
produced each summary.

During the hold interval, use `lab.py urls` in another terminal to inspect the live driver UI. The script verifies eight distinct partition IDs, exact count and integer moments, both named worker hosts and bounded executor metadata. The report is written under `.workshop/results` before the hold. Spark stops in `finally` even if the numerical assertion fails.

For inputs 0 through n minus one, the independent sum oracle is \(n(n-1)/2\). With n=100000 that is 4999950000. The squared-input oracle is \(n(n-1)(2n-1)/6\). Neither oracle requires collecting the original rows. The receipt's Python PIDs identify task processes; its separate executor inventory identifies JVM executors. Compare both to the actual container identities from the host.

## Worked case B: reason about a rejected collection

```python fragment
# Deliberately unsafe idea for a large dataset; do not replace the real job with it.
all_rows = spark.range(10_000_000).collect()
```

The driver has `spark.driver.maxResultSize=1m`. A sufficiently large serialized task-result set must fail instead of being accepted as a successful computation. That setting is a result-size guard, not a complete driver-memory limit: Python objects and optimizer state can consume more memory than their serialized representation. This worksheet describes the negative control; the source-only qualification ledger does not claim it was executed.

Compare the proposed collection with the real `.mapPartitions(...).collect()`: the latter collects one bounded summary per partition, with a fixed partition budget and a final 32 KiB report limit. Increasing partition count without revisiting that contract would also increase driver results. The safe property comes from bounded structure, not from avoiding the spelling `collect` entirely.

## Observed local qualification

The retained native ARM64 workshop run used two separate worker containers and two executor JVMs. All eight partition IDs covered 100000 inputs; the fitted coefficients were exactly intercept 3 and slope 2 for this fixture, with predictions 200003 and 200005. Its live UI and completed history were inspected. The raw-collection negative control remains not run. These are single-host infrastructure observations, not package-specific or cloud acceptance.

## Worked example: combining eight partition summaries into the fitted line

```python
n_total, parts = 100_000, 8
size = n_total // parts
summaries = []
for p in range(parts):
    xs = range(p * size, (p + 1) * size)
    summaries.append(
        {
            "n": len(xs),
            "sx": sum(xs),
            "sxx": sum(x * x for x in xs),
            "sy": sum(3 + 2 * x for x in xs),
            "sxy": sum(x * (3 + 2 * x) for x in xs),
        }
    )
t = {k: sum(s[k] for s in summaries) for k in summaries[0]}
n = t["n"]
assert t["sx"] == n * (n - 1) // 2 and t["sxx"] == n * (n - 1) * (2 * n - 1) // 6
slope = (n * t["sxy"] - t["sx"] * t["sy"]) / (n * t["sxx"] - t["sx"] ** 2)
intercept = (t["sy"] - slope * t["sx"]) / n
print("sx", t["sx"], "sxx", t["sxx"])
print("intercept", intercept, "slope", slope)
print("predictions", [intercept + slope * x for x in (100_000, 100_001)])
```

Output from running the block above:

```text
sx 4999950000 sxx 333328333350000
intercept 3.0 slope 2.0
predictions [200003.0, 200005.0]
```

The loop reproduces the bounded job's five sufficient statistics over eight equal partitions of the integers 0 to 99999, using plain Python instead of Spark, and then combines them on the driver side. The totals match both closed form oracles, 4999950000 for the sum and 333328333350000 for the sum of squares, before any coefficient is computed. The normal equations then give intercept exactly 3.0 and slope exactly 2.0, and the two future covariates 100000 and 100001 map to 200003 and 200005, the same values reported by the retained ARM64 workshop run. Only eight dictionaries of five integers each cross into the final computation, which is why the job fits within the 1m driver result limit regardless of the input size. Python integers do not overflow here; in a JVM aggregation with long values the sum of squares is still far below the long limit.

## Worked example: detecting a missing or duplicated partition summary

```python
def coverage(records, expected=8):
    ids = sorted(r["partition"] for r in records)
    missing = sorted(set(range(expected)) - set(ids))
    duplicated = sorted({i for i in ids if ids.count(i) > 1})
    return missing, duplicated, sum(r["n"] for r in records)


good = [{"partition": p, "n": 12_500} for p in range(8)]
lost = good[:7]
doubled = good + [{"partition": 3, "n": 12_500}]
for name, records in (("complete", good), ("one lost", lost), ("one doubled", doubled)):
    missing, duplicated, n = coverage(records)
    print(f"{name:11} n={n:>6} missing={missing} duplicated={duplicated}")
```

Output from running the block above:

```text
complete    n=100000 missing=[] duplicated=[]
one lost    n= 87500 missing=[7] duplicated=[]
one doubled n=112500 missing=[] duplicated=[3]
```

Coverage is checked by partition ID, not by row count alone. A complete run reports 100000 rows with nothing missing or duplicated. Losing partition 7 drops the total to 87500 and names the gap. The doubled case is the dangerous one for a sum based estimator: partition 3 appears twice, the total rises to 112500, and the fitted line would still look nearly correct because the duplicated rows obey the same relation. That is why the bounded job asserts that sorted partition IDs equal range(8) before trusting any coefficient. Spark itself returns only the successful attempt for each partition of an RDD collect, so a duplicate here would point to a bug in how records were merged or to an external write repeated by a retried task, which needs its own idempotency design.

## Diagnose and transfer

Missing or duplicate partition IDs invalidate the aggregate even when a final coefficient looks plausible. An empty partition must return its zero-count summary. A failed task attempt may be retried, but only the successful partition result contributes to the RDD result. External writes performed inside a task need a separate idempotency design.

For nonlinear likelihood fitting, the same data-placement principle can apply to bounded objective/gradient summaries, but sufficient statistics and decomposability must be proved for the actual model. Use the independent package's contract instead of assuming every loss has this linear closed form.

## Primary references

- [Spark configuration and driver result limits](https://spark.apache.org/docs/4.0.1/configuration.html)
- [RDD programming model](https://spark.apache.org/docs/4.0.1/rdd-programming-guide.html)
