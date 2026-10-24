# go-031: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Logs describe events; stable fields let operators inspect them without parsing prose. A correlation ID connects related work, a level indicates severity and numeric counts support diagnosis. Logging does not replace returning an error or checking an invariant. Avoid credentials, raw tokens, complete user payloads and unbounded identifiers. Structured output can still leak data if its fields are chosen badly. Tests should control timestamps and parse records instead of comparing incidental field order. Metrics describe aggregates, logs describe events and traces connect distributed spans. Choose which evidence answers the question rather than emitting everything indiscriminately.

log/slog builds records from key/value attributes. JSONHandler writes to an io.Writer. HandlerOptions.ReplaceAttr can remove timestamps in deterministic tests. Logger.With attaches common attributes to a derived logger. A logged status is a report, while the actual operation and durable receipt remain separate evidence.

## 1. Emit a structured event

Log processed with count 3 and parse its JSON.

```go
v := logRecord("processed", "count", 3)
check(v["msg"] == "processed" && v["count"] == float64(3), "fields")
```

**Expected:** The record has message processed and numeric count 3.

The check inspects meaning rather than serialized field order.

## 2. Retain correlation

Log request_id lesson-7.

```go
v := logRecord("read", "request_id", "lesson-7")
check(v["request_id"] == "lesson-7", "correlation")
```

**Expected:** The ID is retained exactly.

A bounded synthetic ID is sufficient. Secrets and complete payloads are inappropriate correlation fields.

## 3. Control variable time

Inspect the deterministic fixture record.

```go
v := logRecord("stable")
_, present := v["time"]
check(!present, "time")
```

**Expected:** The time attribute is absent.

Production logs generally need time. The fixture deliberately controls a variable field instead of asserting the current clock.

## 4. Keep status structured

Log a failed status separately from its message.

```go
v := logRecord("read finished", "status", "failed")
check(v["status"] == "failed", "status")
```

**Expected:** status equals failed.

Filtering a structured status is more reliable than searching for a particular sentence.

## 5. Redact before logging

Replace a credential value with a fixed marker.

```go
v := logRecord("configuration", "credential", "[redacted]")
check(v["credential"] == "[redacted]", "redaction")
```

**Expected:** Only [redacted] is present.

Redaction at the producer boundary is easier to review than attempting to remove secrets after serialization.

## 6. Transfer numeric evidence

Log a byte count of 12.

```go
v := logRecord("read", "bytes", 12)
check(v["bytes"] == float64(12), "numeric")
```

**Expected:** The parsed field remains numeric 12.

Numbers should remain numbers for aggregation. The test decoder represents JSON numbers as float64 by default.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
