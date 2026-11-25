# go-011: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-011_solution.go` implements all six cases.

## Mechanism

Errors describe unsuccessful operations without forcing every failure into panic recovery. A function returning a value and error makes the caller choose what to do next. The error chain should preserve both human context and a machine-inspectable cause. Wrapping with fmt.Errorf and %w adds context while errors.Is and errors.As can inspect underlying identity or type. Comparing formatted text is brittle because wording is presentation, not a stable contract. A nil error means the operation succeeded according to its API; it does not prove every downstream interpretation is valid. Handle failures where you can add useful context, recover deliberately or report them accurately.

errors.New constructs an error value. fmt.Errorf("read: %w", err) wraps an existing cause. errors.Is follows supported wrapping relationships to compare a sentinel; errors.As finds an error assignable to a target type. Return nil for a successful error result, not an interface containing a typed nil pointer. Avoid logging and returning the same error at every layer because repeated messages can obscure the causal chain.

## 1. Preserve a cause: change one input

Copy worked example 1, change `err := fmt.Errorf("read record: %w", ErrMissing)` to `err := fmt.Errorf("read record: %v", ErrMissing)` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
err := fmt.Errorf("read record: %w", ErrMissing)
check(errors.Is(err, ErrMissing), "wrapped cause")
```

**Expected:** The edited run panics with `wrapped cause` because `errors.Is(err, ErrMissing)` no longer holds.

**Verify:** Restoring `err := fmt.Errorf("read record: %w", ErrMissing)` makes the check pass again with the worked observation: errors.Is still recognizes ErrMissing.

%w exposes the cause to the error-inspection protocol. Replacing it with %v would format the cause as text but lose that wrapping relationship.

## 2. Reject text equality: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(errors.Is(a, b), "identity not text")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
a := errors.New("missing")
b := errors.New("missing")
check(!errors.Is(a, b), "identity not text")
```

**Expected:** The defective run panics with `identity not text`; after restoring `check(!errors.Is(a, b), "identity not text")`, their identities differ.

**Verify:** The edited check fails with message `identity not text` for a state that `!errors.Is(a, b)` accepts.

A matching message does not establish the same error contract. Use an exported sentinel or typed error only when callers should rely on that distinction.

## 3. Inspect a typed boundary

Return a LimitError carrying an allowed maximum and inspect it with errors.As.

```go
err := fmt.Errorf("request: %w", &LimitError{Max: 3})
var limit *LimitError
check(errors.As(err, &limit) && limit.Max == 3, "typed error")
```

**Expected:** The extracted limit is 3.

**Verify:** Your solution must keep `errors.As(err, &limit) && limit.Max == 3` true. Control: changing `err := fmt.Errorf("request: %w", &LimitError{Max: 3})` to `err := fmt.Errorf("request: %v", &LimitError{Max: 3})` panics with message `typed error`; revert it.

The type carries structured information without parsing presentation text. The target passed to errors.As is a pointer to the variable that should receive the matching error.

## 4. Handle successful parsing

Parse valid integer text and check error before value use.

```go
v, err := strconv.Atoi("42")
check(err == nil && v == 42, "valid parse")
```

**Expected:** The result is 42 and the error is nil.

**Verify:** Your solution must keep `err == nil && v == 42` true. Control: changing `v, err := strconv.Atoi("42")` to `v, err := strconv.Atoi("43")` panics with message `valid parse`; revert it.

The success branch establishes that the returned value is usable. The ordering prevents an unvalidated value from leaking into a later calculation.

## 5. Classify invalid parsing

Parse malformed integer text and inspect its NumError.

```go
_, err := strconv.Atoi("4x")
var number *strconv.NumError
check(errors.As(err, &number), "parse error")
```

**Expected:** The typed parse error is present.

**Verify:** Your solution must keep `errors.As(err, &number)` true. Control: an input that falsifies it fails with message `parse error`; revert it.

Typed inspection supports a specific response to invalid input. It should not be confused with retrying a transient external outage.

## 6. Transfer joined failures

Join missing and permission errors and inspect both causes.

```go
err := errors.Join(ErrMissing, ErrDenied)
check(errors.Is(err, ErrMissing) && errors.Is(err, ErrDenied), "joined errors")
```

**Expected:** Both sentinels remain discoverable.

**Verify:** Your solution must keep `errors.Is(err, ErrMissing) && errors.Is(err, ErrDenied)` true. Control: an input that falsifies it fails with message `joined errors`; revert it.

Multiple failures can matter during cleanup or validation. Joining retains their identities instead of discarding all but the last failure.

## Transfer after comparison

An error has two audiences: the person reading its message and the program inspecting its identity or type. `%w`, errors.Is, errors.As and errors.Join serve the program; the context text serves the person. Later lessons on HTTP handlers, retries and Kubernetes API conflicts depend on classifying failures correctly, so decide which errors are part of a contract before callers start relying on their wording.
