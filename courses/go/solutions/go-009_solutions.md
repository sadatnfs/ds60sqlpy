# go-009: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-009_solution.go` implements all six cases.

## Mechanism

A pointer contains the address of a value. Passing a pointer still copies the pointer value, but both copies identify the same target. This is useful when mutation is the intended contract and dangerous when callers expect isolation. Go's garbage collector keeps reachable objects alive, so returning a pointer to a local variable is valid; the compiler decides where storage must live. That does not make every pointer safe to use: nil has no target and dereferencing it panics. Ordinary Go pointers do not support arithmetic. Use a value receiver or an independent copy when shared mutation is unnecessary, and make optional pointer semantics explicit.

&value obtains an address and *pointer dereferences it. In a type, *Point means a pointer to Point. new(T) returns a pointer to a zero T; it does not initialize maps or channels stored inside T. Selectors automatically follow a pointer to a struct, so p.X is convenient syntax for field access through p. A nil check guards dereference only when no unsynchronized writer can change the state between those operations.

## 1. Mutate through a pointer: change one input

Copy worked example 1, change `n := 4` to `n := 5` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
n := 4
increment(&n)
check(n == 5, "pointer mutation")
```

**Expected:** The edited run panics with `pointer mutation` because `n == 5` no longer holds.

**Verify:** Restoring `n := 4` makes the check pass again with the worked observation: the caller value becomes 5.

The helper changes the shared target, not the caller variable that stores the pointer. The mutation contract must be visible at the call site.

## 2. Return a live value: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(*p != 7, "returned pointer")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
p := seven()
check(*p == 7, "returned pointer")
```

**Expected:** The defective run panics with `returned pointer`; after restoring `check(*p == 7, "returned pointer")`, the returned pointer remains valid and reads 7.

**Verify:** The edited check fails with message `returned pointer` for a state that `*p == 7` accepts.

Go extends storage lifetime as needed. Stack-versus-heap placement is an implementation decision and should not be guessed from the lexical block alone.

## 3. Guard absence

Represent an optional integer with a nil pointer and inspect it without dereferencing.

```go
var p *int
check(p == nil, "nil pointer")
```

**Expected:** The pointer is absent.

**Verify:** Your solution must keep `p == nil` true. Control: changing `check(p == nil, "nil pointer")` to `check(p != nil, "nil pointer")` panics with message `nil pointer`; revert it.

Nil is a useful absence marker only when callers check it. It is different from a pointer to an integer whose value is zero.

## 4. Allocate a zero target

Use new(int) and compare pointer presence with its stored value.

```go
p := new(int)
check(p != nil && *p == 0, "new zero")
```

**Expected:** The pointer is non-nil and its target is 0.

**Verify:** Your solution must keep `p != nil && *p == 0` true. Control: changing `check(p != nil && *p == 0, "new zero")` to `check(p == nil && *p == 0, "new zero")` panics with message `new zero`; revert it.

Allocation and initialization are separate questions. A target can exist while carrying its type zero value.

## 5. Separate copy and target

Copy the integer behind a pointer, then change the original target.

```go
n := 3
p := &n
copied := *p
*p = 9
check(copied == 3 && n == 9, "copy target")
```

**Expected:** The copied integer remains 3 while the target becomes 9.

**Verify:** Your solution must keep `copied == 3 && n == 9` true. Control: changing `n := 3` to `n := 4` panics with message `copy target`; revert it.

Dereferencing to obtain a scalar value copies that scalar. Retaining a pointer would instead retain access to the changing target.

## 6. Transfer an optional update

Implement setIfPresent so a nil pointer is a harmless no-op and a present pointer changes.

```go
check(!setIfPresent(nil, 8), "absent update")
n := 1
check(setIfPresent(&n, 8) && n == 8, "present update")
```

**Expected:** The absent call returns false; the present value becomes 8.

**Verify:** Your solution must keep `setIfPresent(&n, 8) && n == 8` true. Control: changing `check(setIfPresent(&n, 8) && n == 8, "present update")` to `check(setIfPresent(&n, 9) && n == 8, "present update")` panics with message `present update`; revert it.

An explicit boolean tells the caller whether the update happened. Silently treating absent and updated states as identical would hide useful information.

## Transfer after comparison

A pointer is a deliberate sharing decision. Each case here asked whether a change should be visible through another name: increment wants it, the copied scalar does not, and setIfPresent reports whether it happened. Later lessons use pointer receivers, optional fields in decoded JSON and errors.As targets; for each one, state who owns the target, who may write it and how absence is represented.
