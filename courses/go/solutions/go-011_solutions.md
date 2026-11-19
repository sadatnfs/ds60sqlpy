# go-011: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Errors describe unsuccessful operations without forcing every failure into panic recovery. A function returning a value and error makes the caller choose what to do next. The error chain should preserve both human context and a machine-inspectable cause. Wrapping with fmt.Errorf and %w adds context while errors.Is and errors.As can inspect underlying identity or type. Comparing formatted text is brittle because wording is presentation, not a stable contract. A nil error means the operation succeeded according to its API; it does not prove every downstream interpretation is valid. Handle failures where you can add useful context, recover deliberately or report them accurately.

errors.New constructs an error value. fmt.Errorf("read: %w", err) wraps an existing cause. errors.Is follows supported wrapping relationships to compare a sentinel; errors.As finds an error assignable to a target type. Return nil for a successful error result, not an interface containing a typed nil pointer. Avoid logging and returning the same error at every layer because repeated messages can obscure the causal chain.

## 1. Preserve a cause: change one input

Copy worked example 1 into a scratch pad and change `err := fmt.Errorf("read record: %w", ErrMissing)` to `err := fmt.Errorf("read record: %v", ErrMissing)`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
err := fmt.Errorf("read record: %w", ErrMissing)
check(errors.Is(err, ErrMissing), "wrapped cause")
```

**Expected:** The changed run panics with `wrapped cause` because `errors.Is(err, ErrMissing)` no longer holds. Restoring the original line brings back the worked observation: errors.Is still recognizes ErrMissing.

%w exposes the cause to the error-inspection protocol. Replacing it with %v would format the cause as text but lose that wrapping relationship.

## 2. Reject text equality: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(errors.Is(a, b), "identity not text")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
a := errors.New("missing")
b := errors.New("missing")
check(!errors.Is(a, b), "identity not text")
```

**Expected:** Before the repair the program panics with `identity not text`; after it the line reads `check(!errors.Is(a, b), "identity not text")` again and their identities differ.

A matching message does not establish the same error contract. Use an exported sentinel or typed error only when callers should rely on that distinction.

## 3. Inspect a typed boundary

Return a LimitError carrying an allowed maximum and inspect it with errors.As.

```go
err := fmt.Errorf("request: %w", &LimitError{Max: 3})
var limit *LimitError
check(errors.As(err, &limit) && limit.Max == 3, "typed error")
```

**Expected:** The extracted limit is 3.

The type carries structured information without parsing presentation text. The target passed to errors.As is a pointer to the variable that should receive the matching error.

## 4. Handle successful parsing

Parse valid integer text and check error before value use.

```go
v, err := strconv.Atoi("42")
check(err == nil && v == 42, "valid parse")
```

**Expected:** The result is 42 and the error is nil.

The success branch establishes that the returned value is usable. The ordering prevents an unvalidated value from leaking into a later calculation.

## 5. Classify invalid parsing

Parse malformed integer text and inspect its NumError.

```go
_, err := strconv.Atoi("4x")
var number *strconv.NumError
check(errors.As(err, &number), "parse error")
```

**Expected:** The typed parse error is present.

Typed inspection supports a specific response to invalid input. It should not be confused with retrying a transient external outage.

## 6. Transfer joined failures

Join missing and permission errors and inspect both causes.

```go
err := errors.Join(ErrMissing, ErrDenied)
check(errors.Is(err, ErrMissing) && errors.Is(err, ErrDenied), "joined errors")
```

**Expected:** Both sentinels remain discoverable.

Multiple failures can matter during cleanup or validation. Joining retains their identities instead of discarding all but the last failure.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
