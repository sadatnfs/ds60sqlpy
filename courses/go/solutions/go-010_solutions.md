# go-010: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A method associates behavior with a named type. An interface describes a set of methods, and a concrete type satisfies it implicitly by providing that set. This encourages small interfaces defined by the consumer instead of deep inheritance hierarchies. A value receiver receives a copy; a pointer receiver can mutate its target and has a different method set. An interface value contains both dynamic type information and a dynamic value. It is nil only when both are absent. Therefore an interface holding a typed nil pointer is not a nil interface. This matters especially when returning errors or optional implementations across package boundaries.

func (c Counter) Value() int declares a value receiver. func (c *Counter) Add(n int) uses a pointer receiver. type Valuer interface { Value() int } declares required behavior. A type assertion value, ok := item.(Concrete) checks a dynamic type safely. Prefer the comma-ok form when failure is expected, rather than a panic-producing assertion.

## 1. Dispatch through behavior: change one input

Copy worked example 1 into a scratch pad and change `var v Valuer = Counter{N: 3}` to `var v Valuer = Counter{N: 4}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
var v Valuer = Counter{N: 3}
check(v.Value() == 3, "interface dispatch")
```

**Expected:** The changed run panics with `interface dispatch` because `v.Value() == 3` no longer holds. Restoring the original line brings back the worked observation: calling Value returns 3.

The concrete type satisfies the interface without declaring that relationship. The caller depends only on the method contract.

## 2. Mutate through a method: debug a regression

A regression changed one token in worked example 2, so one line now reads `c := Counter{N: 4}`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
c := Counter{N: 3}
c.Add(2)
check(c.N == 5, "pointer receiver")
```

**Expected:** Before the repair the program panics with `pointer receiver`; after it the line reads `c := Counter{N: 3}` again and its value becomes 5.

The language can take the address of this addressable variable for the method call. The pointer receiver makes the mutation effective on the original value.

## 3. Trace a value receiver

Call a value-receiver helper that increments only its receiver copy.

```go
c := Counter{N: 3}
got := c.Incremented()
check(got == 4 && c.N == 3, "receiver copy")
```

**Expected:** The returned value is 4 but the original remains 3.

Changing a value receiver's scalar field changes the copied receiver. Fields that reference shared storage still require separate ownership reasoning.

## 4. Expose typed nil

Put a nil pointer to Counter inside an empty interface.

```go
var p *Counter
var item any = p
check(item != nil, "typed nil")
```

**Expected:** The interface is not nil.

The interface contains the dynamic type *Counter even though its dynamic pointer is nil. Comparing only the interface to nil does not test target availability.

## 5. Use safe dynamic inspection

Assert that an interface containing a string is an int with comma-ok.

```go
var item any = "three"
_, ok := item.(int)
check(!ok, "type assertion")
```

**Expected:** The assertion reports false without panicking.

A failed dynamic conversion is ordinary evidence when the input type is uncertain. A single-value assertion would turn this expected mismatch into a panic.

## 6. Transfer substitutability

Implement a second Valuer type returning a fixed value and use the same consuming helper.

```go
check(readValue(Counter{N: 2}) == 2 && readValue(Fixed(8)) == 8, "substitution")
```

**Expected:** Both implementations can be read through one contract.

The consumer should not depend on concrete fields or perform a type switch unless its real contract requires different behavior.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
