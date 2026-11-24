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

**Approach.** Follow the call through the interface: `v` stores a copy of `Counter{N: 4}`, and `v.Value()` dispatches to `Counter.Value`, which returns the stored field, 4.

**Why it holds here.** The check compares the dispatched result with 3, so it fails and panics with `interface dispatch`. Nothing else in the example changes.

**A plausible wrong approach.** Predicting a compile error because `Counter` never declares that it implements `Valuer`. Go satisfies interfaces implicitly: having a `Value() int` method in the method set is enough, so the program compiles and fails only at the check.

**Verify.** Print `v.Value()` and `fmt.Sprintf("%T", v)`: the edited run shows `4` and `main.Counter` before the panic, and restoring 3 brings back the success line.

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

**Approach.** Trace `c.Add(2)`: Go takes `&c` for the pointer-receiver call, so `c.N += 2` updates the caller's variable. Starting from the regressed 4 gives 6.

**Why it holds here.** The check expects 3 plus 2, so 6 makes it panic with `pointer receiver`. Restoring `Counter{N: 3}` restores 5 without touching the method or the check.

**A plausible wrong approach.** Compensating with `c.Add(1)` so the result is 5 again. The check passes, but the starting state is still wrong and the example no longer demonstrates the intended mutation. Changing `Add` to a value receiver is worse: `c.N` would stay at its start value.

**Verify.** Print `c.N` after the call: 6 with the regression and 5 after the repair. As a control, temporarily give `Add` a value receiver and observe that `c.N` stays at 3.

## 3. Trace a value receiver

Call a value-receiver helper that increments only its receiver copy.

```go
c := Counter{N: 3}
got := c.Incremented()
check(got == 4 && c.N == 3, "receiver copy")
```

**Expected:** The returned value is 4 but the original remains 3.

Changing a value receiver's scalar field changes the copied receiver. Fields that reference shared storage still require separate ownership reasoning.

**Approach.** Call the value-receiver method `Incremented` and inspect both its return value and the caller's field.

**Why it holds here.** The method receives a copy of `c`, increments the copy's `N` to 4 and returns it, while the caller's `c.N` stays 3, so `got == 4 && c.N == 3` holds.

**A plausible wrong approach.** Expecting `c.N` to become 4 by analogy with `Add`, or switching `Incremented` to a pointer receiver to "fix" it. With a pointer receiver the caller's field becomes 4 and the `receiver copy` check panics.

**Verify.** Print `got, c.N` and see `4 3`. Call `c.Incremented()` twice and both calls return 4, which shows each call starts from the same unchanged original.

## 4. Expose typed nil

Put a nil pointer to Counter inside an empty interface.

```go
var p *Counter
var item any = p
check(item != nil, "typed nil")
```

**Expected:** The interface is not nil.

The interface contains the dynamic type *Counter even though its dynamic pointer is nil. Comparing only the interface to nil does not test target availability.

**Approach.** Store a nil `*Counter` in a variable of type `any` and compare the interface itself with nil.

**Why it holds here.** An interface value is nil only when both its dynamic type and value are absent. Here the dynamic type is `*Counter`, so `item != nil` is true even though the pointer inside is nil.

**A plausible wrong approach.** Guarding with `if item == nil { return }` and then calling `item.(*Counter).Add(1)`. The guard does not trigger, and the call dereferences a nil pointer, which panics with an invalid memory address error.

**Verify.** Print `fmt.Printf("%T %v\n", item, item)` to see `*main.Counter <nil>`, and check that `item.(*Counter) == nil` is true while `item == nil` is false.

## 5. Use safe dynamic inspection

Assert that an interface containing a string is an int with comma-ok.

```go
var item any = "three"
_, ok := item.(int)
check(!ok, "type assertion")
```

**Expected:** The assertion reports false without panicking.

A failed dynamic conversion is ordinary evidence when the input type is uncertain. A single-value assertion would turn this expected mismatch into a panic.

**Approach.** Use the two-result assertion `_, ok := item.(int)` on an interface that holds the string `three`.

**Why it holds here.** The dynamic type is `string`, not `int`, so the comma-ok form returns the zero value 0 and `ok == false` instead of panicking, and the check passes.

**A plausible wrong approach.** Writing the single-result form `n := item.(int)`. With a string inside, it panics with `interface conversion: interface {} is string, not int`, turning an expected mismatch into a crash.

**Verify.** Print the zero value and `ok` to see `0 false`, then assert `item.(string)` with comma-ok and see `three true`.

## 6. Transfer substitutability

Implement a second Valuer type returning a fixed value and use the same consuming helper.

```go
check(readValue(Counter{N: 2}) == 2 && readValue(Fixed(8)) == 8, "substitution")
```

**Expected:** Both implementations can be read through one contract.

The consumer should not depend on concrete fields or perform a type switch unless its real contract requires different behavior.

**Approach.** Give the named type `Fixed` its own `Value() int` method with a value receiver and pass both `Counter{N: 2}` and `Fixed(8)` to the unchanged `readValue`.

**Why it holds here.** `readValue` depends only on the `Valuer` method set, and both value types have `Value` in their method sets, so the calls return 2 and 8.

**A plausible wrong approach.** Declaring the method as `func (f *Fixed) Value() int`. Then only `*Fixed` implements `Valuer`, and `readValue(Fixed(8))` fails to compile with a message that `Value` has a pointer receiver.

**Verify.** Run the case and read the success line, then print `%T` for each argument to see `main.Counter` and `main.Fixed` handled by the same helper.

## Transfer after comparison

Add a `Doubled struct{ Base int }` whose value-receiver `Value` returns twice `Base`, and a pointer-receiver `Reset` that sets `Base` to 0. Check that `readValue(Doubled{Base: 4})` is 8, that `Reset` changes an addressable variable, and that `var d *Doubled` stored in a `Valuer` is not nil. Explain why calling `Value` through that nil pointer would panic.
