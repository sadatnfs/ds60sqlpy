# go-032: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Security starts by identifying untrusted inputs and operations carrying authority. Validation defines the accepted domain, while escaping protects the syntax of a particular output context. HTML escaping, URL encoding and SQL parameter binding solve different problems. They are not interchangeable. A string replacement is not an authorization policy. Bound input before expensive parsing, reject ambiguous forms and keep secrets out of diagnostics. These harmless examples expose boundary semantics; they do not establish that the local classroom is safe for hosting arbitrary untrusted tenants. Review authority and ownership before connecting code to real files, networks or services.

html/template escapes according to HTML context; text/template does not supply that protection. url.QueryEscape encodes one query value rather than an entire URL. filepath.IsLocal checks a lexical property but does not resolve symlinks. subtle.ConstantTimeCompare compares equal-length byte sequences without value-dependent comparison time. Protocol design must still handle length, storage and cryptographic choices.

## 1. Escape HTML data

Render script-like text with html/template.

```go
var b bytes.Buffer
t := template.Must(template.New("x").Parse("<p>{{.}}</p>"))
check(t.Execute(&b, "<script>alert(1)</script>") == nil, "render")
check(strings.Contains(b.String(), "&lt;script&gt;"), "escape")
```

**Expected:** Angle brackets become escaped text.

Marking untrusted input as template.HTML would bypass this boundary. Keep data as data.

## 2. Encode a query value

Encode a value containing ampersand and equals characters.

```go
original := "a&role=admin"
encoded := url.QueryEscape(original)
decoded, err := url.QueryUnescape(encoded)
check(err == nil && decoded == original && encoded != original, "query")
```

**Expected:** Decoding recovers the original string.

Encoding prevents data from being interpreted as new query syntax. It does not authorize the resulting request.

## 3. Reject traversal grammar

Compare ../outside with reports/item.txt.

```go
check(!filepath.IsLocal("../outside") && filepath.IsLocal("reports/item.txt"), "local path")
```

**Expected:** Only the second path is lexically local.

Symlinks and concurrent filesystem changes require a stronger access boundary than lexical checks alone.

## 4. Apply a byte budget

Compare three-byte and five-byte values against maximum four.

```go
check(len([]byte("abc")) <= 4 && len([]byte("abcde")) > 4, "budget")
```

**Expected:** Only the smaller value fits.

Byte count matches encoded storage consumption. Rune count answers a different question.

## 5. Compare fixed-size values

Compare equal and unequal four-byte values.

```go
check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abcd")) == 1, "equal")
check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abce")) == 0, "different")
```

**Expected:** The helper returns 1 for equal and 0 for unequal.

This is an API demonstration with synthetic values. It is not a complete authentication design.

## 6. Transfer a reviewed action set

Allow read and list, then inspect read and exec.

```go
allowed := map[string]bool{"read": true, "list": true}
check(allowed["read"] && !allowed["exec"], "allowlist")
```

**Expected:** read is accepted and exec is rejected.

Map accepted names to reviewed behavior. Do not turn input strings into shell commands or arbitrary endpoints.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
