# go-032: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-032_solution.go` implements all six cases.

## Mechanism

Security starts by identifying untrusted inputs and operations carrying authority. Validation defines the accepted domain, while escaping protects the syntax of a particular output context. HTML escaping, URL encoding and SQL parameter binding solve different problems. They are not interchangeable. A string replacement is not an authorization policy. Bound input before expensive parsing, reject ambiguous forms and keep secrets out of diagnostics. These harmless examples expose boundary semantics; they do not establish that the local classroom is safe for hosting arbitrary untrusted tenants. Review authority and ownership before connecting code to real files, networks or services.

html/template escapes according to HTML context; text/template does not supply that protection. url.QueryEscape encodes one query value rather than an entire URL. filepath.IsLocal checks a lexical property but does not resolve symlinks. subtle.ConstantTimeCompare compares equal-length byte sequences without value-dependent comparison time. Protocol design must still handle length, storage and cryptographic choices.

## 1. Escape HTML data: predict an edited check

Copy worked example 1, change `check(t.Execute(&b, "<script>alert(1)</script>") == nil, "render")` to `check(t.Execute(&b, "<script>alert(1)</script>") != nil, "render")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
var b bytes.Buffer
t := template.Must(template.New("x").Parse("<p>{{.}}</p>"))
check(t.Execute(&b, "<script>alert(1)</script>") == nil, "render")
check(strings.Contains(b.String(), "&lt;script&gt;"), "escape")
```

**Expected:** The edited check panics with `render` even though `t.Execute(&b, "<script>alert(1)</script>") == nil` still holds.

**Verify:** Restoring `check(t.Execute(&b, "<script>alert(1)</script>") == nil, "render")` makes the check pass again with the worked observation: angle brackets become escaped text.

Marking untrusted input as template.HTML would bypass this boundary. Keep data as data.

**Approach.** Execute the template with the script text as data; `html/template` escapes it for the HTML text context and returns nil.

**Why it holds here.** Escaping is how the package handles dangerous data; it does not refuse it. `Execute` therefore returns nil, the edited `!= nil` is false and the check panics with `render`.

**A plausible wrong approach.** Predicting that `Execute` rejects the script with an error, so the edited check would pass. The package never treats data as an error; it renders it as inert text.

**Verify.** Print `b.String()` and see `<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>`. Changing the import to `text/template` prints the raw tags and fails the `escape` check.

## 2. Encode a query value: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(err != nil && decoded == original && encoded != original, "query")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
original := "a&role=admin"
encoded := url.QueryEscape(original)
decoded, err := url.QueryUnescape(encoded)
check(err == nil && decoded == original && encoded != original, "query")
```

**Expected:** The defective run panics with `query`; after restoring `check(err == nil && decoded == original && encoded != original, "query")`, decoding recovers the original string.

**Verify:** The edited check fails with message `query` for a state that `err == nil && decoded == original && encoded != original` accepts.

Encoding prevents data from being interpreted as new query syntax. It does not authorize the resulting request.

**Approach.** Encode `a&role=admin` with `url.QueryEscape`, giving `a%26role%3Dadmin`, then decode it with `url.QueryUnescape`.

**Why it holds here.** Escaping and unescaping round-trip, so `decoded` equals the original with a nil error and the encoded form differs. The edited `err != nil` is false and the check panics with `query`.

**A plausible wrong approach.** Building the URL as `"?q=" + original`. Parsing that query yields `q=a` and a separate `role=admin` parameter, so the input added a field it was never allowed to set.

**Verify.** Print `encoded` and see `a%26role%3Dadmin`, and `url.Values{"q": {original}}.Encode()` prints `q=a%26role%3Dadmin`.

## 3. Reject traversal grammar

Compare ../outside with reports/item.txt.

```go
check(!filepath.IsLocal("../outside") && filepath.IsLocal("reports/item.txt"), "local path")
```

**Expected:** Only the second path is lexically local.

**Verify:** Your solution must keep `!filepath.IsLocal("../outside") && filepath.IsLocal("reports/item.txt")` true. Control: changing `check(!filepath.IsLocal("../outside") && filepath.IsLocal("reports/item.txt"), "local path")` to `check(filepath.IsLocal("../outside") && filepath.IsLocal("reports/item.txt"), "local path")` panics with message `local path`; revert it.

Symlinks and concurrent filesystem changes require a stronger access boundary than lexical checks alone.

**Approach.** Ask `filepath.IsLocal` about each path; it rejects empty, absolute and parent-escaping paths after lexical cleaning.

**Why it holds here.** `../outside` starts by leaving the base directory, so it is not local, while `reports/item.txt` stays inside it, so only the second returns true.

**A plausible wrong approach.** Rejecting only paths that start with `..`. That allows `reports/../../outside`, which cleans to `../outside`, and absolute paths such as `/etc/passwd`; `IsLocal` returns false for both.

**Verify.** Print `filepath.IsLocal` for `reports/../../outside`, `/etc/passwd` and the empty string and see `false` three times.

## 4. Apply a byte budget

Compare three-byte and five-byte values against maximum four.

```go
check(len([]byte("abc")) <= 4 && len([]byte("abcde")) > 4, "budget")
```

**Expected:** Only the smaller value fits.

**Verify:** Your solution must keep `len([]byte("abc")) <= 4 && len([]byte("abcde")) > 4` true. Control: changing `check(len([]byte("abc")) <= 4 && len([]byte("abcde")) > 4, "budget")` to `check(len([]byte("abc")) <= 4 && len([]byte("abcde")) > 5, "budget")` panics with message `budget`; revert it.

Byte count matches encoded storage consumption. Rune count answers a different question.

**Approach.** Measure each value in bytes, the unit storage and network budgets are charged in, and compare with the inclusive limit 4.

**Why it holds here.** `abc` is 3 bytes and fits, `abcde` is 5 and does not, so both sides of the check hold.

**A plausible wrong approach.** Counting runes with `utf8.RuneCountInString`. For ASCII the answers match, but `ééé` is 3 runes and 6 bytes, so a rune budget of 4 accepts it while it exceeds the byte limit.

**Verify.** Print `len("abc"), len("abcde"), len("ééé")` and see `3 5 6`; `len` of a string already counts bytes, without the conversion.

## 5. Compare fixed-size values

Compare equal and unequal four-byte values.

```go
check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abcd")) == 1, "equal")
check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abce")) == 0, "different")
```

**Expected:** The helper returns 1 for equal and 0 for unequal.

**Verify:** Your solution must keep `subtle.ConstantTimeCompare([]byte("abcd"), []byte("abcd")) == 1` true. Control: changing `check(subtle.ConstantTimeCompare([]byte("abcd"), []byte("abcd")) == 1, "equal")` to `check(subtle.ConstantTimeCompare([]byte("abcd!"), []byte("abcd")) == 1, "equal")` panics with message `equal`; revert it.

This is an API demonstration with synthetic values. It is not a complete authentication design.

**Approach.** Compare the equal and the unequal four-byte values with `subtle.ConstantTimeCompare`, which returns an `int`.

**Why it holds here.** For equal-length inputs it inspects every byte before answering, returning 1 for `abcd` and `abcd` and 0 for `abcd` and `abce`.

**A plausible wrong approach.** Writing `check(subtle.ConstantTimeCompare(a, b), "equal")` as if the result were a `bool`. Go does not convert `int` to `bool`, so it fails to compile with a message that an `int` value cannot be used as `bool`.

**Verify.** Print both results and see `1 0`. Comparing `abc` with `abcd` also returns 0, immediately, because differing lengths are reported without a byte scan.

## 6. Transfer a reviewed action set

Allow read and list, then inspect read and exec.

```go
allowed := map[string]bool{"read": true, "list": true}
check(allowed["read"] && !allowed["exec"], "allowlist")
```

**Expected:** read is accepted and exec is rejected.

**Verify:** Your solution must keep `allowed["read"] && !allowed["exec"]` true. Control: changing `allowed := map[string]bool{"read": true, "list": true}` to `allowed := map[string]bool{"read": false, "list": true}` panics with message `allowlist`; revert it.

Map accepted names to reviewed behavior. Do not turn input strings into shell commands or arbitrary endpoints.

**Approach.** Accept an action only when it is a key in the reviewed `allowed` map; a missing key reads as false.

**Why it holds here.** `read` was reviewed and maps to true, while `exec` was never listed, so the lookup returns false and the check holds.

**A plausible wrong approach.** Keeping a denylist such as `blocked := map[string]bool{"exec": true}` and accepting anything not blocked. `Exec`, `shell` or any new name passes because missing keys read as false, so unreviewed actions are accepted.

**Verify.** Print `allowed["read"], allowed["exec"], allowed["Read"]` and see `true false false`.

## Transfer after comparison

Write `searchURL(base, q string) (string, error)` that accepts only `/search` and `/docs` as `base` and appends `?q=` plus `url.QueryEscape(q)`. Check `a&b` gives `/search?q=a%26b`, `/admin` is refused and a 300-byte `q` is rejected by a 256-byte budget. Explain which check plain concatenation or a denylist of bases would fail.
