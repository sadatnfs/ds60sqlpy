# go-019: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-019_solution.go` implements all six cases.

## Mechanism

JSON is a serialization format, not a complete application schema. A syntactically valid object can still contain unknown fields, missing required values, invalid ranges or extra documents after the first value. Go struct tags define field names and omission rules. The decoder normally tolerates unknown fields, so strict APIs must request a stricter policy. Numeric JSON values decoded into any become floating values unless the decoder uses json.Number; large integers can lose precision. Decode transport syntax, validate domain meaning and reject trailing data as separate steps. Do not use the same structure blindly for external input, internal state and public output.

json:"name" maps a field to its wire name. json.Marshal returns bytes and an error. Decoder.DisallowUnknownFields rejects fields missing from a target struct. A second Decode should return io.EOF when exactly one JSON value is required. omitempty omits zero-like fields during encoding; it does not validate mandatory fields. Use pointers or explicit presence types when absent and zero differ.

## 1. Decode a typed object: change one input

Copy worked example 1, change ``err := json.Unmarshal([]byte(`{"name":"sample","count":3}`), &c)`` to ``err := json.Unmarshal([]byte(`{"name":"sample","count":4}`), &c)`` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
var c Config
err := json.Unmarshal([]byte(`{"name":"sample","count":3}`), &c)
check(err == nil && c.Name == "sample" && c.Count == 3, "typed JSON")
```

**Expected:** The edited run panics with `typed JSON` because `err == nil && c.Name == "sample" && c.Count == 3` no longer holds.

**Verify:** Restoring ``err := json.Unmarshal([]byte(`{"name":"sample","count":3}`), &c)`` makes the check pass again with the worked observation: the fields become sample and 3.

Field names follow tags rather than an accidental presentation format. Parsing success still leaves count-range and name rules to domain validation.

## 2. Reject an unknown property: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(d.Decode(&c) == nil, "unknown field")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
var c Config
d := json.NewDecoder(strings.NewReader(`{"name":"x","extra":1}`))
d.DisallowUnknownFields()
check(d.Decode(&c) != nil, "unknown field")
```

**Expected:** The defective run panics with `unknown field`; after restoring `check(d.Decode(&c) != nil, "unknown field")`, decoding returns an error.

**Verify:** The edited check fails with message `unknown field` for a state that `d.Decode(&c) != nil` accepts.

Strict rejection catches misspelled configuration keys instead of silently ignoring a learner or operator mistake.

## 3. Detect a second document

Decode two adjacent JSON objects and check whether another value exists.

```go
d := json.NewDecoder(strings.NewReader(`{} {}`))
var a, b any
check(d.Decode(&a) == nil && d.Decode(&b) == nil, "trailing document")
```

**Expected:** A second value is observable, so the single-document contract fails.

**Verify:** Your solution must keep `d.Decode(&a) == nil && d.Decode(&b) == nil` true. Control: changing `check(d.Decode(&a) == nil && d.Decode(&b) == nil, "trailing document")` to `check(d.Decode(&a) != nil && d.Decode(&b) == nil, "trailing document")` panics with message `trailing document`; revert it.

One successful Decode consumes one value. It does not prove the entire input contains only that value.

## 4. Confirm exact completion

Decode one object, then require EOF.

```go
d := json.NewDecoder(strings.NewReader(`{"name":"x"}`))
var c Config
check(d.Decode(&c) == nil, "first decode")
var extra any
check(d.Decode(&extra) == io.EOF, "exact end")
```

**Expected:** The second decode returns io.EOF.

**Verify:** Your solution must keep `d.Decode(&extra) == io.EOF` true. Control: changing `check(d.Decode(&extra) == io.EOF, "exact end")` to `check(d.Decode(&extra) != io.EOF, "exact end")` panics with message `exact end`; revert it.

The second read establishes the single-document boundary. Whitespace after the object is allowed by the decoder.

## 5. Preserve a large integer token

Use UseNumber while decoding 9007199254740993 into any.

```go
d := json.NewDecoder(strings.NewReader(`9007199254740993`))
d.UseNumber()
var v any
check(d.Decode(&v) == nil && v.(json.Number).String() == "9007199254740993", "number token")
```

**Expected:** The exact decimal token is retained.

**Verify:** Your solution must keep `d.Decode(&v) == nil && v.(json.Number).String() == "9007199254740993"` true. Control: changing ``d := json.NewDecoder(strings.NewReader(`9007199254740993`))`` to ``d := json.NewDecoder(strings.NewReader(`9007199254740994`))`` panics with message `number token`; revert it.

Keeping the token avoids an early float64 conversion. The application still needs to choose a numeric range and handle conversion errors.

## 6. Transfer domain validation

Decode a negative count successfully, then reject it as a domain error.

```go
var c Config
err := json.Unmarshal([]byte(`{"name":"x","count":-1}`), &c)
check(err == nil && c.Count < 0, "domain invalid")
```

**Expected:** JSON syntax is valid but count validation fails.

**Verify:** Your solution must keep `err == nil && c.Count < 0` true. Control: changing `check(err == nil && c.Count < 0, "domain invalid")` to `check(err != nil && c.Count < 0, "domain invalid")` panics with message `domain invalid`; revert it.

Separating syntax and semantics yields better diagnostics. A decoder cannot infer that this application forbids negative counts.

## Transfer after comparison

Every wire boundary in later lessons has the same layers: syntax, schema shape and domain validity. HTTP handlers decode request bodies, configuration loaders read files and Kubernetes manifests are JSON or YAML checked against a schema. For each, decide which unknown fields are errors, whether trailing data is allowed and which domain rules run after decoding.
