# go-017: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

io.Reader and io.Writer describe data movement independently of where bytes are stored. A reader can return some bytes and an error together; process the bytes before deciding whether the error ends the stream. One Read call is not guaranteed to fill a buffer. io.ReadFull expresses a different contract: obtain exactly the requested length or report why that was impossible. Streaming avoids loading an entire input into memory, but it is only bounded when the caller limits input, buffering and output. A limit reached is not automatically valid end-of-document evidence. Keep transport completion separate from format validation.

Read receives a byte slice and returns n and err. Only the first n bytes contain this call's data. io.EOF means the stream has ended; io.ErrUnexpectedEOF means a fixed-size request ended after partial data. io.Copy repeatedly transfers data and returns a count plus error. io.LimitReader caps visible bytes. bytes.Buffer provides an in-memory reader/writer useful for deterministic tests.

## 1. Copy a stream

Copy alpha from a strings.Reader into bytes.Buffer.

```go
var out bytes.Buffer
n, err := io.Copy(&out, strings.NewReader("alpha"))
check(err == nil && n == 5 && out.String() == "alpha", "copy")
```

**Expected:** Five bytes are copied and output is alpha.

The consumer depends on Reader and Writer behavior rather than a particular file or socket implementation.

## 2. Require a full record

Read exactly four bytes from a two-byte source.

```go
buf := make([]byte, 4)
n, err := io.ReadFull(strings.NewReader("ab"), buf)
check(n == 2 && err == io.ErrUnexpectedEOF, "partial record")
```

**Expected:** Two bytes arrive and ErrUnexpectedEOF is returned.

Partial data is useful evidence, but it is not a complete fixed-width record. Treating any positive n as completion would accept truncation.

## 3. Bound visible input

Read at most three bytes from abcdef.

```go
v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcdef"), 3))
check(err == nil && string(v) == "abc", "limit")
```

**Expected:** The visible result is abc.

The limit controls resource use. It does not establish that the original source had only three bytes, so a format checker may need one extra byte to detect excess input.

## 4. Detect excess data

Read a four-byte budget for a three-byte maximum.

```go
v, err := io.ReadAll(io.LimitReader(strings.NewReader("abcd"), 4))
check(err == nil && len(v) > 3, "excess input")
```

**Expected:** A four-byte result proves the maximum was exceeded.

Reading maximum plus one distinguishes exactly-at-limit data from truncated over-limit input without unbounded allocation.

## 5. Preserve an empty stream

Copy an empty reader to a buffer.

```go
var out bytes.Buffer
n, err := io.Copy(&out, strings.NewReader(""))
check(err == nil && n == 0 && out.Len() == 0, "empty copy")
```

**Expected:** The count is zero and there is no error.

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

Explicit frame lengths prevent a reader from guessing where one logical object ends. Real formats also validate lengths before allocating.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
