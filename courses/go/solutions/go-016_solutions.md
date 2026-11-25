# go-016: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-016_solution.go` implements all six cases.

## Mechanism

A function value can be stored, passed and called like other values. A closure also refers to variables from its surrounding scope. That makes callbacks concise, but it makes lifetime and mutation worth tracing explicitly. Two closures can intentionally share one variable; two independent constructor calls can create separate state. A callback contract should describe when it is called, whether it may stop iteration and whether it can retain supplied values. Iterator-style APIs can avoid allocating intermediate slices, but early termination and cleanup must still be well defined. Do not confuse deferred execution with concurrent execution: a closure is not a goroutine by itself.

func(int) int is a function type. An anonymous func literal creates a function value. Returning a closure from makeCounter retains access to its captured count. A visitor returning bool can stop a traversal when false. Passing a function as a parameter makes selection policy explicit without an interface type when only one operation is needed. The iter package names this visitor shape: iter.Seq[V] is func(yield func(V) bool), and for x := range seq runs the loop body as the yield callback, so break, continue and return keep their ordinary meaning.

## 1. Capture a changing variable: change one input

Copy worked example 1, change `factor = 3` to `factor = 4` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
factor := 2
multiply := func(x int) int { return factor * x }
factor = 3
check(multiply(4) == 12, "capture variable")
```

**Expected:** The edited run panics with `capture variable` because `multiply(4) == 12` no longer holds.

**Verify:** Restoring `factor = 3` makes the check pass again with the worked observation: the closure uses the new factor 3.

The closure refers to the variable rather than freezing its initial value. Explicitly copying a value into a new binding produces a different contract.

## 2. Create independent counters: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(a() != 1 && a() == 2 && b() == 1, "independent closures")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
a, b := makeCounter(), makeCounter()
check(a() == 1 && a() == 2 && b() == 1, "independent closures")
```

**Expected:** The defective run panics with `independent closures`; after restoring `check(a() == 1 && a() == 2 && b() == 1, "independent closures")`, the first returns 1 then 2; the second starts at 1.

**Verify:** The edited check fails with message `independent closures` for a state that `a() == 1 && a() == 2 && b() == 1` accepts.

Each constructor invocation creates its own captured state. Sharing a single returned closure would share that state instead.

## 3. Inject a transformation

Map a doubling callback over 1, 2 and 3.

```go
v := mapInts([]int{1, 2, 3}, func(x int) int { return 2 * x })
check(len(v) == 3 && v[0] == 2 && v[2] == 6, "callback")
```

**Expected:** The result is 2, 4 and 6.

**Verify:** Your solution must keep `len(v) == 3 && v[0] == 2 && v[2] == 6` true. Control: changing `v := mapInts([]int{1, 2, 3}, func(x int) int { return 2 * x })` to `v := mapInts([]int{1, 2, 3}, func(x int) int { return 2 + x })` panics with message `callback`; revert it.

The traversal owns iteration while the callback owns the element transformation. This separation is useful only when both contracts remain simple.

## 4. Stop a visitor early

Visit 1 through 5 and stop after observing 3.

```go
count := 0
visit(5, func(x int) bool { count++; return x < 3 })
check(count == 3, "early stop")
```

**Expected:** Exactly three values are visited.

**Verify:** Your solution must keep `count == 3` true. Control: changing `visit(5, func(x int) bool { count++; return x < 3 })` to `visit(5, func(x int) bool { count++; return x <= 3 })` panics with message `early stop`; revert it.

The stop decision occurs after the third callback. Counting callbacks distinguishes stopping before a value from stopping after observing it.

## 5. Handle an empty traversal

Visit an empty range with a callback that would increment a count.

```go
count := 0
visit(0, func(x int) bool { count++; return true })
check(count == 0, "empty callback")
```

**Expected:** The callback is never invoked.

**Verify:** Your solution must keep `count == 0` true. Control: changing `count := 0` to `count := 1` panics with message `empty callback`; revert it.

A caller should not need a fabricated sentinel callback to learn that there were no values. Empty behavior belongs in the traversal contract.

## 6. Transfer the visitor to a range-over-func iterator

Range over an iter.Seq[int] that yields 1 through 5, append each value, and break after 2.

```go
produced := 0
got := []int{}
for x := range countTo(5, &produced) {
	got = append(got, x)
	if x == 2 {
		break
	}
}
check(len(got) == 2 && got[0] == 1 && got[1] == 2 && produced == 2, "range over func")
```

**Expected:** The loop collects 1 and 2, and the iterator produces exactly two values.

**Verify:** Your solution must keep `len(got) == 2 && got[0] == 1 && got[1] == 2 && produced == 2` true. Control: changing `if x == 2 {` to `if x != 2 {` panics with message `range over func`; revert it.

Since Go 1.23 a for statement can range over a function with the iter.Seq shape func(yield func(int) bool). The loop body becomes the yield callback: break makes yield return false, and the iterator must return at once. Calling yield again after it has returned false makes the program panic. The visit helper above already had this shape, so the same early-termination contract now works with ordinary for, break and continue.

## Transfer after comparison

Ask three questions of every callback API: when is it called, may it stop the traversal and may it retain what it receives? Later lessons pass handlers to HTTP servers, work functions to goroutines and event handlers to Kubernetes informers. Each depends on a documented calling contract, and a captured variable shared across goroutines also needs synchronization, which a closure alone never provides.
