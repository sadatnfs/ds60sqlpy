# go-031: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Logs describe events; stable fields let operators inspect them without parsing prose. A correlation ID connects related work, a level indicates severity and numeric counts support diagnosis. Logging does not replace returning an error or checking an invariant. Avoid credentials, raw tokens, complete user payloads and unbounded identifiers. Structured output can still leak data if its fields are chosen badly. Tests should control timestamps and parse records instead of comparing incidental field order. Metrics describe aggregates, logs describe events and traces connect distributed spans. Choose which evidence answers the question rather than emitting everything indiscriminately.

log/slog builds records from key/value attributes. JSONHandler writes to an io.Writer. HandlerOptions.ReplaceAttr can remove timestamps in deterministic tests. Logger.With attaches common attributes to a derived logger. A logged status is a report, while the actual operation and durable receipt remain separate evidence.

## 1. Emit a structured event: change one input

Copy worked example 1 into a scratch pad and change `v := logRecord("processed", "count", 3)` to `v := logRecord("processed", "count", 4)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
v := logRecord("processed", "count", 3)
check(v["msg"] == "processed" && v["count"] == float64(3), "fields")
```

**Expected:** The changed run panics with `fields` because `v["msg"] == "processed" && v["count"] == float64(3)` no longer holds. Restoring the original line brings back the worked observation: the record has message processed and numeric count 3.

The check inspects meaning rather than serialized field order.

**Approach.** Follow the edited value through the JSON handler: `count` is written as the number 4, and `json.Unmarshal` into `map[string]any` decodes it as `float64(4)`.

**Why it holds here.** `msg` is still `processed`, so only `v["count"] == float64(3)` fails and the check panics with `fields`.

**A plausible wrong approach.** Writing the comparison as `v["count"] == 3`. The constant 3 becomes `int(3)` when compared with an `any`, and an interface holding `float64` never equals one holding `int`, so even the original record would fail.

**Verify.** Print `v` and see `map[count:4 level:INFO msg:processed]` before the panic.

## 2. Retain correlation: debug a regression

A regression changed one token in worked example 2, so one line now reads `v := logRecord("read", "request_id!", "lesson-7")`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
v := logRecord("read", "request_id", "lesson-7")
check(v["request_id"] == "lesson-7", "correlation")
```

**Expected:** Before the repair the program panics with `correlation`; after it the line reads `v := logRecord("read", "request_id", "lesson-7")` again and the ID is retained exactly.

A bounded synthetic ID is sufficient. Secrets and complete payloads are inappropriate correlation fields.

**Approach.** Inspect the decoded record from the regression: the attribute key is `request_id!`, so the map has that key and `v["request_id"]` is nil.

**Why it holds here.** The check looks up the exact key `request_id`, and nil never equals `lesson-7`, so it panics with `correlation`. Restoring the key name restores the lookup without touching the value.

**A plausible wrong approach.** Passing the pair as one string, `logRecord("read", "request_id=lesson-7")`. A lone string argument with no value becomes an attribute under the key `!BADKEY`, so `request_id` is still missing and the check panics.

**Verify.** Print `v` and see `request_id!:lesson-7` for the regression and `request_id:lesson-7` after the repair.

## 3. Control variable time

Inspect the deterministic fixture record.

```go
v := logRecord("stable")
_, present := v["time"]
check(!present, "time")
```

**Expected:** The time attribute is absent.

Production logs generally need time. The fixture deliberately controls a variable field instead of asserting the current clock.

**Approach.** Rely on the handler's `ReplaceAttr`, which returns an empty `slog.Attr` for `slog.TimeKey`; the handler omits empty attributes.

**Why it holds here.** The time attribute is dropped before encoding, so the decoded map has no `time` key and `present` is false.

**A plausible wrong approach.** Creating the handler with `slog.NewJSONHandler(&b, nil)`. The record then includes the current time, `present` is true and the check panics with `time`; asserting the exact time instead would be flaky.

**Verify.** Print `v` and see `map[level:INFO msg:stable]` with no time field.

## 4. Keep status structured

Log a failed status separately from its message.

```go
v := logRecord("read finished", "status", "failed")
check(v["status"] == "failed", "status")
```

**Expected:** status equals failed.

Filtering a structured status is more reliable than searching for a particular sentence.

**Approach.** Pass `status` as its own key and value instead of placing it in the message text.

**Why it holds here.** The handler writes `status` as a separate JSON field, so the decoded map has `status` equal to `failed` while `msg` stays `read finished`.

**A plausible wrong approach.** Folding it into the message with `fmt.Sprintf("read finished: status=%s", "failed")` and no attributes. The map then has no `status` key, `v["status"]` is nil and the check panics with `status`.

**Verify.** Print `v["msg"], v["status"]` and see `read finished failed`.

## 5. Redact before logging

Replace a credential value with a fixed marker.

```go
v := logRecord("configuration", "credential", "[redacted]")
check(v["credential"] == "[redacted]", "redaction")
```

**Expected:** Only [redacted] is present.

Redaction at the producer boundary is easier to review than attempting to remove secrets after serialization.

**Approach.** Replace the credential with the fixed marker before calling the logger, so the secret never reaches the handler or the buffer.

**Why it holds here.** The handler only ever sees `[redacted]`, so the decoded `credential` field equals the marker.

**A plausible wrong approach.** Logging the real value and relying on a `ReplaceAttr` rule that redacts a key named `password`. This call uses the key `credential`, so the rule never fires and the secret is written into the buffer.

**Verify.** Print `v` and see `map[credential:[redacted] level:INFO msg:configuration]`, and confirm `strings.Contains(fmt.Sprint(v), secret)` is false for the real value.

## 6. Transfer numeric evidence

Log a byte count of 12.

```go
v := logRecord("read", "bytes", 12)
check(v["bytes"] == float64(12), "numeric")
```

**Expected:** The parsed field remains numeric 12.

Numbers should remain numbers for aggregation. The test decoder represents JSON numbers as float64 by default.

**Approach.** Log the byte count as the integer 12 so the handler writes a JSON number.

**Why it holds here.** A JSON number decoded into `any` becomes `float64`, so `v["bytes"]` is `float64(12)` and the comparison holds.

**A plausible wrong approach.** Logging `strconv.Itoa(12)`. The field becomes the JSON string `"12"`, the decoded value is a `string`, the check panics with `numeric`, and a log query that sums bytes would skip it.

**Verify.** Print `fmt.Printf("%T %v\n", v["bytes"], v["bytes"])` and see `float64 12`.

## Transfer after comparison

Log `upload` with `request_id` `lesson-9`, `bytes` 2048 and `status` `ok`, decode the buffer with a `json.Decoder` that calls `UseNumber`, and check `bytes` is `json.Number("2048")`, `status` is `ok`, `msg` is `upload` and `time` is absent. Explain which checks a message like `upload ok 2048 bytes` with no attributes would fail.
