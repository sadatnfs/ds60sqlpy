# go-017: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-017_solution.go` implements all six cases.

## Mechanism

io.Reader and io.Writer describe data movement independently of where bytes are stored. A reader can return some bytes and an error together; process the bytes before deciding whether the error ends the stream. One Read call is not guaranteed to fill a buffer. io.ReadFull expresses a different contract: obtain exactly the requested length or report why that was impossible. Streaming avoids loading an entire input into memory, but it is only bounded when the caller limits input, buffering and output. A limit reached is not automatically valid end-of-document evidence. Keep transport completion separate from format validation.

Read receives a byte slice and returns n and err. Only the first n bytes contain this call's data. io.EOF means the stream has ended; io.ErrUnexpectedEOF means a fixed-size request ended after partial data. io.Copy repeatedly transfers data and returns a count plus error. io.LimitReader caps visible bytes. bytes.Buffer provides an in-memory reader/writer useful for deterministic tests.

## 1. Copy a stream: change one input

Copy worked example 1, change `n, err := io.Copy(&out, strings.NewReader("alpha"))` to `n, err := io.Copy(&out, strings.NewReader("alpha!"))` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
var out bytes.Buffer
n, err := io.Copy(&out, strings.NewReader("alpha"))
check(err == nil && n == 5 && out.String() == "alpha", "copy")
```

**Expected:** The edited run panics with `copy` because `err == nil && n == 5 && out.String() == "alpha"` no longer holds.

**Verify:** Restoring `n, err := io.Copy(&out, strings.NewReader("alpha"))` makes the check pass again with the worked observation: five bytes are copied and output is alpha.

The consumer depends on Reader and Writer behavior rather than a particular file or socket implementation.

## 2. Require a full record: debug a regression

A one-token regression in worked example 2 makes a line read `n, err := io.ReadFull(strings.NewReader("ab!"), buf)`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
buf := make([]byte, 4)
n, err := io.ReadFull(strings.NewReader("ab"), buf)
check(n == 2 && err == io.ErrUnexpectedEOF, "partial record")
```

**Expected:** The defective run panics with `partial record`; after restoring `n, err := io.ReadFull(strings.NewReader("ab"), buf)`, two bytes arrive and ErrUnexpectedEOF is returned.

**Verify:** The failing run shows message `partial record`; after the repair `n == 2 && err == io.ErrUnexpectedEOF` holds again.

Partial data is useful evidence, but it is not a complete fixed-width record. Treating any positive n as completion would accept truncation.

## 3. Bound visible input

Read at most three bytes from abcdef.

```go
v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcdef"), 3))
check(err == nil && string(v) == "abc", "limit")
```

**Expected:** The visible result is abc.

**Verify:** Your solution must keep `err == nil && string(v) == "abc"` true. Control: changing `v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcdef"), 3))` to `v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcdef"), 4))` panics with message `limit`; revert it.

The limit controls resource use. It does not establish that the original source had only three bytes, so a format checker may need one extra byte to detect excess input.

## 4. Detect excess data

Read a four-byte budget for a three-byte maximum.

```go
v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcd"), 4))
check(err == nil && len(v) > 3, "excess input")
```

**Expected:** A four-byte result proves the maximum was exceeded.

**Verify:** Your solution must keep `err == nil && len(v) > 3` true. Control: changing `check(err == nil && len(v) > 3, "excess input")` to `check(err != nil && len(v) > 3, "excess input")` panics with message `excess input`; revert it.

Reading maximum plus one distinguishes exactly-at-limit data from truncated over-limit input without unbounded allocation.

## 5. Preserve an empty stream

Copy an empty reader to a buffer.

```go
var out bytes.Buffer
n, err := io.Copy(&out, strings.NewReader(""))
check(err == nil && n == 0 && out.Len() == 0, "empty copy")
```

**Expected:** The count is zero and there is no error.

**Verify:** Your solution must keep `err == nil && n == 0 && out.Len() == 0` true. Control: changing `check(err == nil && n == 0 && out.Len() == 0, "empty copy")` to `check(err != nil && n == 0 && out.Len() == 0, "empty copy")` panics with message `empty copy`; revert it.

An empty stream can be valid transport input even when an application later requires at least one record.

## 6. Transfer exact framing

Read a two-byte header followed by a three-byte payload.

```go
r := strings.NewReader("ABxyz")
h := make([]byte, 2)
p := make([]byte, 3)
_, e1 := io.ReadFull(r, h)
_, e2 := io.ReadFull(r, p)
check(e1 == nil && e2 == nil && string(h) == "AB" && string(p) == "xyz", "framing")
```

**Expected:** The header is AB and payload is xyz.

**Verify:** Your solution must keep `e1 == nil && e2 == nil && string(h) == "AB" && string(p) == "xyz"` true. Control: changing `h := make([]byte, 2)` to `h := make([]byte, 3)` panics with message `framing`; revert it.

Explicit frame lengths prevent a reader from guessing where one logical object ends. Real formats also validate lengths before allocating.

## Transfer after comparison

The Reader and Writer contracts reappear in every I/O lesson that follows. JSON and CSV decoders consume readers, HTTP request and response bodies are readers that must be bounded and closed, and container logs arrive as streams. For each, decide the input budget, how truncation is detected and who closes the source before writing any parsing code.
