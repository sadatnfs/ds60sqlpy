# go-014: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Tests are executable claims about behavior. A test should distinguish the intended implementation from a plausible wrong one. Table-driven testing records input and expectation as data, then applies the same assertion logic to each case. Normal cases show use, boundary cases define edges, and invalid cases define failure behavior. A reference example in a single pad uses explicit checks; a real Go test lives in a file ending _test.go and receives *testing.T. Tests must not depend on global ordering, current time or a network service unless those dependencies are deliberately controlled. Coverage describes executed code, not the strength of the assertions.

A test table is often a slice of anonymous structs with name, input and want fields. In a prepared project, func TestName(t *testing.T) is discovered by go test, and t.Run creates named subtests. Compare actual and expected values directly; include the case name in failure messages. Fuzz tests describe invariants across generated inputs, but they need a bounded execution budget and persistent regression seeds. Do not treat successful compilation as a behavior test.

## 1. Build a named table

Test clamp with values below, inside and above the range 0 to 10.

```go
cases := []struct{ in, want int }{{-2, 0}, {4, 4}, {12, 10}}
for _, tc := range cases {
	check(clamp(tc.in) == tc.want, "clamp table")
}
```

**Expected:** The outputs are 0, 4 and 10.

A wrong implementation that only returns its input fails the outside cases; one that always returns an endpoint fails the interior case.

## 2. Include exact endpoints

Test clamp at 0 and 10.

```go
check(clamp(0) == 0 && clamp(10) == 10, "endpoints")
```

**Expected:** Both endpoints are preserved.

Endpoint tests distinguish inclusive boundaries from off-by-one policies. They should be named in the API contract.

## 3. Check idempotence

Apply clamp twice to values -2, 4 and 12.

```go
for _, x := range []int{-2, 4, 12} {
	check(clamp(clamp(x)) == clamp(x), "idempotence")
}
```

**Expected:** Applying it twice gives the same result as once.

This is a property rather than a single expected output. It complements concrete cases but would not reject every wrong constant function on its own.

## 4. Reject a plausible mutant

Compare the correct clamp with a mutant that incorrectly caps at 9.

```go
check(clamp(10) != mutantClamp(10), "mutant rejected")
```

**Expected:** Input 10 distinguishes them.

A test's value is visible when it rejects a realistic defect. Merely executing both functions without comparing them provides no such evidence.

## 5. Cover a range invariant

Check all integer inputs from -20 through 20.

```go
for x := -20; x <= 20; x++ {
	v := clamp(x)
	check(v >= 0 && v <= 10, "range invariant")
}
```

**Expected:** Every result lies between 0 and 10.

This bounded exhaustive set supports the invariant for its chosen domain. It is not a proof about every possible integer or an excuse to remove exact cases.

## 6. Transfer a fresh regression

Retain input 11 as a regression for an implementation that forgets the upper cap.

```go
check(clamp(11) == 10, "upper regression")
```

**Expected:** The result is 10.

The smallest counterexample just beyond the boundary often explains the defect better than a large random value. Keep it after the fix.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
