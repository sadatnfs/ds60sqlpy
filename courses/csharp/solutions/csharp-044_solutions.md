# csharp-044: explanation and comparison

Reference program: [csharp-044_solution.cs](csharp-044_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Emit a safe result record:** Named fields retain meaning without depending on a fragile formatted sentence. The serialized event contains an explicit rejected outcome.

**Keep outcome counts consistent:** The counts come from the emitted events, so a record that was never classified would make the first check fail. The denominator is stated explicitly; changing it changes the metric meaning. The accepted and rejected events account for all five submitted records, and the rejection rate is 0.4.

## Task answers

### Task 1: Predict and explain

Identify safe fields and the event population.

**Written answer.** The `Event` record carries four fields: `OperationId` correlates events from one run, `Stage` says where in the pipeline it happened, `Outcome` is a fixed vocabulary such as accepted or rejected, and `Count` is how many records share that outcome. All four are safe because none contains raw input. The event population is one event per operation, stage and outcome, so in Example B the accepted and rejected events for `op-7` together describe all five submitted records.

**Why it is correct.** Knowing the population lets a reader sum events correctly; knowing the fields are safe lets the events be retained and shared without exposing data.

**Plausible wrong approach.** Treating each event as one record would make `Count` 3 look like a single item, and adding the rejected line text would put user content into telemetry.

**How to verify.** Sum `Count` over the events of one operation and confirm it equals the submitted count, and list each field with a reason it is safe.

### Task 2: Guided modification

Add a stage value without adding raw input content.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
string raw = "pear,-1,secret-note";
var evt = new Event("fixture-1", "parse", "rejected", 1);
string json = JsonSerializer.Serialize(evt);
using var parsed = JsonDocument.Parse(json);
var root = parsed.RootElement;
Check(root.GetProperty("Stage").GetString() == "parse", "stage recorded");
Check(!json.Contains(raw, StringComparison.Ordinal), "raw line absent");
bool leaked = json.Contains("secret", StringComparison.Ordinal);
Check(!leaked, "input content absent");
Check(root.EnumerateObject().Count() == 4, "no extra fields");
```

**Observe:** The event records stage `parse` with outcome `rejected`, and neither the raw line nor any part of its content appears in the JSON.

The new stage value is a fixed label that says where the rejection happened, which is useful operational evidence on its own. The raw line is deliberately not passed to the event, so the serialized JSON contains only the four declared fields. The last check guards that shape, so adding a `Line` field later fails visibly instead of quietly leaking input.

**Plausible wrong approach.** Including the rejected line `for debugging` turns telemetry into a copy of user data, with all the retention and access obligations that come with it.

**How to verify.** Serialize an event with a fifth, raw-content field in an anonymous object and confirm the content check fails.

### Task 3: Independent construction

Instrument your import project with submitted, accepted and rejected counts.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
int[] quantities = { 3, -1, 4, -2, 5 };
int submitted = quantities.Length;
int accepted = quantities.Count(quantity => quantity >= 0);
int rejected = quantities.Count(quantity => quantity < 0);
Check(submitted == 5 && accepted == 3 && rejected == 2, "counts");
Check(accepted + rejected == submitted, "every record accounted for");
```

**Observe:** 5 submitted records split into 3 accepted and 2 rejected.

All three counts come from the same input, so the accounting check would fail if a record were dropped or counted twice.

### Task 4: Diagnose a defect

Diagnose a success metric incremented before persistence completes.

**Written answer.** If the handler runs `accepted++` and then `await store.SaveAsync(items)`, a failed or cancelled save still leaves the success metric incremented. The dashboard then reports records as accepted that were never persisted, and the accepted plus rejected events no longer reconcile with what is in storage. Increment the metric after the save completes, or record the outcome from the result of the save, and emit a failed outcome if it throws.

**Why it is correct.** An outcome metric must describe what happened, not what was attempted. Recording it after the effect it claims is what makes it evidence.

**Plausible wrong approach.** Decrementing the counter in a catch block is fragile: a cancellation or a crash between the two steps still leaves the wrong value.

**How to verify.** Make the save throw for one batch and confirm the accepted count does not change while a failure event for that operation appears.

### Task 5: Boundary evidence

Test zero submitted records and choose a no-data rate representation.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
string Rate(int rejected, int submitted) {
  if (submitted == 0)
    return "no data";
  double rate = (double)rejected / submitted;
  return rate.ToString("0.##", CultureInfo.InvariantCulture);
}
Check(Rate(0, 0) == "no data", "no data, not 0 and not NaN");
Check(Rate(0, 5) == "0", "zero rejections is a real 0");
Check(Rate(2, 5) == "0.4", "rate with data");
Check(double.IsNaN(0.0 / 0), "naive division gives NaN");
Event[] none = Array.Empty<Event>();
Check(none.Sum(e => e.Count) == 0, "no events account for 0 records");
```

**Observe:** With zero submitted records the rate reads `no data`, while zero rejections out of five is a real 0 and two out of five is 0.4.

With no submitted records, a rejection rate is undefined. `0.0 / 0` gives NaN, which serializes poorly and poisons averages, and reporting 0 would claim a perfect run that never happened. Checking `submitted == 0` before dividing keeps no data separate from a measured zero, so the report shows `no data` for the first case and `0` for the second. A `double?` that is null for no data is an equivalent choice when the value feeds code instead of a report.

**Plausible wrong approach.** Returning 0 for an empty run hides outages: a pipeline that received nothing looks identical to one that rejected nothing.

**How to verify.** Serialize `0.0 / 0` with `JsonSerializer` and observe that the default serializer refuses to write NaN, which is another reason to represent no data explicitly.

### Task 6: Transfer and justify

Design a latency report that includes percentiles, sample count and measurement boundaries.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Diagnostics should explain an operation without leaking its inputs or creating an overwhelming stream of unrelated messages. A structured event has stable fields such as operation identity, stage and outcome. These fields let a reader connect the beginning and end of one operation and distinguish a retry from a different request.

Latency, throughput and failure rate describe different aspects of a service. A low average latency can hide a bad tail. A successful process exit does not imply every record was accepted. Define observable counters from the domain contract, and ensure cancelled or unknown work is not misclassified as success. Deterministic fixtures can verify event structure while production measurements need real workloads.

Use a record for a stable event schema and serialize explicit safe fields. Stopwatch is appropriate for elapsed duration, but tests should not assert a narrow timing threshold. Keep correlation identity separate from user secrets.

Correlation identifiers should not contain credentials or private payloads. High-cardinality dimensions can overwhelm metric systems. Missing observations must not be silently counted as successful operations.

## Review before continuing

Run the reference and confirm it prints `csharp-044: passed`, then rerun the guide's counterexample.
