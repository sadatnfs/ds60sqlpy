# go-022: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

HTTP separates method, target, headers, status and body. A handler implements a protocol boundary, not merely a function that returns text. Validate the method and path before applying domain behavior. WriteHeader chooses a response status before the first body write; once a response starts, changing status may be too late. An in-process recorder can test routing and output without opening a socket. This is excellent unit evidence but does not establish real TLS, proxy, timeout or network behavior. Production servers also need bounded request bodies, explicit timeouts, graceful shutdown and safe logging.

http.HandlerFunc adapts a function with ResponseWriter and *Request parameters. httptest.NewRequest creates an inbound request, and httptest.NewRecorder captures status, headers and body. Header().Set changes response metadata before writing. http.Error writes an error response. A handler should return after rejecting a request so it does not accidentally continue into a success path.

## 1. Serve a health request: change one input

Copy worked example 1 into a scratch pad and change `health(r, httptest.NewRequest("GET", "/health", nil))` to `health(r, httptest.NewRequest("GET!", "/health", nil))`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
r := httptest.NewRecorder()
health(r, httptest.NewRequest("GET", "/health", nil))
check(r.Code == 200 && r.Body.String() == "ok\n", "health")
```

**Expected:** The changed run panics with `health` because `r.Code == 200 && r.Body.String() == "ok\n"` no longer holds. Restoring the original line brings back the worked observation: the status is 200 and the body is ok plus a newline.

The recorder runs the handler directly. This proves the handler contract without making any network availability claim.

## 2. Reject an unsupported method: debug a regression

A regression changed one token in worked example 2, so one line now reads `health(r, httptest.NewRequest("POST", "/health!", nil))`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
r := httptest.NewRecorder()
health(r, httptest.NewRequest("POST", "/health", nil))
check(r.Code == 405 && r.Header().Get("Allow") == "GET", "method")
```

**Expected:** Before the repair the program panics with `method`; after it the line reads `health(r, httptest.NewRequest("POST", "/health", nil))` again and the status is 405 and Allow is GET.

The method boundary is explicit. Returning after the error prevents success text from being appended to an already rejected response.

## 3. Reject an unknown route

Send GET /missing.

```go
r := httptest.NewRecorder()
health(r, httptest.NewRequest("GET", "/missing", nil))
check(r.Code == 404, "route")
```

**Expected:** The status is 404.

A catch-all success handler can conceal path mistakes and break monitoring assumptions.

## 4. Check content metadata

Inspect the successful response content type.

```go
r := httptest.NewRecorder()
health(r, httptest.NewRequest("GET", "/health", nil))
check(r.Header().Get("Content-Type") == "text/plain; charset=utf-8", "content type")
```

**Expected:** The response declares text/plain with UTF-8.

Representation metadata belongs to the response contract. The body alone does not describe how a client should interpret it.

## 5. Repeat without shared mutation

Run two independent health requests.

```go
for i := 0; i < 2; i++ {
	r := httptest.NewRecorder()
	health(r, httptest.NewRequest("GET", "/health", nil))
	check(r.Code == 200 && r.Body.String() == "ok\n", "repeat")
}
```

**Expected:** Both responses succeed identically.

The handler has no mutable request-global state. More complex handlers should keep per-request data separate from explicitly synchronized shared state.

## 6. Transfer query independence

Call /health with an unrelated query parameter.

```go
r := httptest.NewRecorder()
health(r, httptest.NewRequest("GET", "/health?probe=1", nil))
check(r.Code == 200, "query separation")
```

**Expected:** The path still matches and returns 200.

URL.Path excludes the query string. If query parameters influence behavior, validate them separately instead of matching the entire raw target.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
