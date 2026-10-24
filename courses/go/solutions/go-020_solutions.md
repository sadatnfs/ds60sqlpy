# go-020: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A CSV record is a sequence of fields with quoting rules. Splitting text on commas fails when a field itself contains a comma, newline or escaped quote. encoding/csv handles this syntax and can enforce a consistent field count. Parsing a record still does not establish its schema: headers, data types, missing values, duplicate keys and row grain need explicit validation. Streaming records supports bounded memory, but one record can be large, so upstream input budgets still matter. Keep original row numbers and field names in diagnostics without printing sensitive full records. An empty numeric field is not automatically zero.

csv.NewReader accepts an io.Reader. Read returns one record or an error; ReadAll is convenient only for explicitly bounded fixtures. FieldsPerRecord enforces shape, and a value of zero lets the first record establish the expected width. csv.Writer buffers output, so call Flush and inspect Error. Quoted commas remain part of one field rather than creating extra columns.

## 1. Parse a quoted comma

Read name and city where the city is Springfield, West.

```go
r := csv.NewReader(strings.NewReader("Ada,\"Springfield, West\"\n"))
v, err := r.Read()
check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")
```

**Expected:** The record contains two fields.

A comma inside quotes belongs to the field. strings.Split would incorrectly create three fields.

## 2. Reject a ragged row

Require two fields and read a three-field row.

```go
r := csv.NewReader(strings.NewReader("a,b,c\n"))
r.FieldsPerRecord = 2
_, err := r.Read()
check(err != nil, "ragged row")
```

**Expected:** The reader reports a field-count error.

Rejecting inconsistent shape prevents silent column shifts that can corrupt downstream type interpretation.

## 3. Decode a numeric field

Parse the second field of item,12 as an integer.

```go
r := csv.NewReader(strings.NewReader("item,12\n"))
v, err := r.Read()
check(err == nil, "record")
n, err := strconv.Atoi(v[1])
check(err == nil && n == 12, "numeric field")
```

**Expected:** The numeric value is 12.

CSV parsing returns strings. Numeric conversion is a separate fallible schema operation.

## 4. Reject blank numeric content

Attempt integer parsing of an empty field.

```go
_, err := strconv.Atoi("")
check(err != nil, "blank number")
```

**Expected:** The conversion fails rather than becoming zero.

Missingness requires a policy. Replacing every parse error with zero changes the data and hides the distinction between missing and measured zero.

## 5. Round-trip a delimiter field

Write a field containing a comma, flush, then read it back.

```go
var b bytes.Buffer
w := csv.NewWriter(&b)
check(w.Write([]string{"a,b", "3"}) == nil, "write")
w.Flush()
check(w.Error() == nil, "flush")
v, err := csv.NewReader(&b).Read()
check(err == nil && v[0] == "a,b", "round trip")
```

**Expected:** The original field survives exactly.

The writer chooses correct quoting. Hand-joining fields with commas cannot preserve this contract for arbitrary text.

## 6. Transfer header validation

Read the header name,count and compare its exact order.

```go
v, err := csv.NewReader(strings.NewReader("name,count\n")).Read()
check(err == nil && len(v) == 2 && v[0] == "name" && v[1] == "count", "header contract")
```

**Expected:** The schema order is name then count.

Matching a set of names is insufficient when later code indexes by position. Either validate order or construct an explicit name-to-index map.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
