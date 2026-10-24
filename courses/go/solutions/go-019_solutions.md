# go-019: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

JSON is a serialization format, not a complete application schema. A syntactically valid object can still contain unknown fields, missing required values, invalid ranges or extra documents after the first value. Go struct tags define field names and omission rules. The decoder normally tolerates unknown fields, so strict APIs must request a stricter policy. Numeric JSON values decoded into any become floating values unless the decoder uses json.Number; large integers can lose precision. Decode transport syntax, validate domain meaning and reject trailing data as separate steps. Do not use the same structure blindly for external input, internal state and public output.

json:"name" maps a field to its wire name. json.Marshal returns bytes and an error. Decoder.DisallowUnknownFields rejects fields missing from a target struct. A second Decode should return io.EOF when exactly one JSON value is required. omitempty omits zero-like fields during encoding; it does not validate mandatory fields. Use pointers or explicit presence types when absent and zero differ.

## 1. Decode a typed object

Decode a name and count into Config.

```go
var c Config
err := json.Unmarshal([]byte(`{"name":"sample","count":3}`), &c)
check(err == nil && c.Name == "sample" && c.Count == 3, "typed JSON")
```

**Expected:** The fields become sample and 3.

Field names follow tags rather than an accidental presentation format. Parsing success still leaves count-range and name rules to domain validation.

## 2. Reject an unknown property

Use a strict decoder on an object with an unexpected extra field.

```go
var c Config
d := json.NewDecoder(strings.NewReader(`{"name":"x","extra":1}`))
d.DisallowUnknownFields()
check(d.Decode(&c) != nil, "unknown field")
```

**Expected:** Decoding returns an error.

Strict rejection catches misspelled configuration keys instead of silently ignoring a learner or operator mistake.

## 3. Detect a second document

Decode two adjacent JSON objects and check whether another value exists.

```go
d := json.NewDecoder(strings.NewReader(`{} {}`))
var a, b any
check(d.Decode(&a) == nil && d.Decode(&b) == nil, "trailing document")
```

**Expected:** A second value is observable, so the single-document contract fails.

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

Keeping the token avoids an early float64 conversion. The application still needs to choose a numeric range and handle conversion errors.

## 6. Transfer domain validation

Decode a negative count successfully, then reject it as a domain error.

```go
var c Config
err := json.Unmarshal([]byte(`{"name":"x","count":-1}`), &c)
check(err == nil && c.Count < 0, "domain invalid")
```

**Expected:** JSON syntax is valid but count validation fails.

Separating syntax and semantics yields better diagnostics. A decoder cannot infer that this application forbids negative counts.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
