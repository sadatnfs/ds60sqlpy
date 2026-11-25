# go-020: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-020_solution.go` implements all six cases.

## Mechanism

A CSV record is a sequence of fields with quoting rules. Splitting text on commas fails when a field itself contains a comma, newline or escaped quote. encoding/csv handles this syntax and can enforce a consistent field count. Parsing a record still does not establish its schema: headers, data types, missing values, duplicate keys and row grain need explicit validation. Streaming records supports bounded memory, but one record can be large, so upstream input budgets still matter. Keep original row numbers and field names in diagnostics without printing sensitive full records. An empty numeric field is not automatically zero.

csv.NewReader accepts an io.Reader. Read returns one record or an error; ReadAll is convenient only for explicitly bounded fixtures. FieldsPerRecord enforces shape, and a value of zero lets the first record establish the expected width. csv.Writer buffers output, so call Flush and inspect Error. Quoted commas remain part of one field rather than creating extra columns.

## 1. Parse a quoted comma: predict an edited check

Copy worked example 1, change `check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")` to `check(err == nil && len(v) == 3 && v[1] == "Springfield, West", "quoted comma")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
r := csv.NewReader(strings.NewReader("Ada,\"Springfield, West\"\n"))
v, err := r.Read()
check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")
```

**Expected:** The edited check panics with `quoted comma` even though `err == nil && len(v) == 2 && v[1] == "Springfield, West"` still holds.

**Verify:** Restoring `check(err == nil && len(v) == 2 && v[1] == "Springfield, West", "quoted comma")` makes the check pass again with the worked observation: the record contains two fields.

A comma inside quotes belongs to the field. strings.Split would incorrectly create three fields.

## 2. Reject a ragged row: debug a regression

A one-token regression in worked example 2 makes a line read `r.FieldsPerRecord = 3`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
r := csv.NewReader(strings.NewReader("a,b,c\n"))
r.FieldsPerRecord = 2
_, err := r.Read()
check(err != nil, "ragged row")
```

**Expected:** The defective run panics with `ragged row`; after restoring `r.FieldsPerRecord = 2`, the reader reports a field-count error.

**Verify:** The failing run shows message `ragged row`; after the repair `err != nil` holds again.

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

**Verify:** Your solution must keep `err == nil && n == 12` true. Control: changing `r := csv.NewReader(strings.NewReader("item,12\n"))` to `r := csv.NewReader(strings.NewReader("item,13\n"))` panics with message `numeric field`; revert it.

CSV parsing returns strings. Numeric conversion is a separate fallible schema operation.

## 4. Reject blank numeric content

Attempt integer parsing of an empty field.

```go
_, err := strconv.Atoi("")
check(err != nil, "blank number")
```

**Expected:** The conversion fails rather than becoming zero.

**Verify:** Your solution must keep `err != nil` true. Control: changing `check(err != nil, "blank number")` to `check(err == nil, "blank number")` panics with message `blank number`; revert it.

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

**Verify:** Your solution must keep `err == nil && v[0] == "a,b"` true. Control: changing `check(err == nil && v[0] == "a,b", "round trip")` to `check(err == nil && v[1] == "a,b", "round trip")` panics with message `round trip`; revert it.

The writer chooses correct quoting. Hand-joining fields with commas cannot preserve this contract for arbitrary text.

## 6. Transfer header validation

Read the header `name,count` and compare its exact order.

```go
v, err := csv.NewReader(strings.NewReader("name,count\n")).Read()
check(err == nil && len(v) == 2 && v[0] == "name" && v[1] == "count", "header contract")
```

**Expected:** The schema order is name then count.

**Verify:** Your solution must keep `err == nil && len(v) == 2 && v[0] == "name" && v[1] == "count"` true. Control: changing `check(err == nil && len(v) == 2 && v[0] == "name" && v[1] == "count", "header contract")` to `check(err == nil && len(v) == 2 && v[1] == "name" && v[1] == "count", "header contract")` panics with message `header contract`; revert it.

Matching a set of names is insufficient when later code indexes by position. Either validate order or construct an explicit name-to-index map.

## Transfer after comparison

CSV is the first data format here where syntax, shape and meaning are clearly separate layers. The same layering applies to log lines, metric exports and configuration tables later: a parser handles quoting, a shape rule rejects ragged records and domain validation checks types and ranges. Report errors with enough context, such as a row number, for a person to fix the data.
