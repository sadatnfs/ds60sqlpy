# go-003: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-003_solution.go` implements all six cases.

## Mechanism

Control flow determines which statements execute. A condition is a boolean expression, not a number used as a truth value. Go's for statement covers counting loops, condition-controlled loops and collection iteration. The safest way to reason about a loop is to name an invariant: a statement true before the first iteration and preserved by every iteration. In a prefix sum, the accumulator contains exactly the elements already visited. Empty input is therefore not an exceptional accident; the initial accumulator already represents its result. Short-circuit operators also affect execution, which makes a guard before a potentially unsafe operation meaningful.

if condition { ... } selects a branch. && skips the right operand when the left is false. for i := 0; i < len(items); i++ visits a half-open index interval. break leaves the innermost loop; continue skips to its next iteration. switch compares one expression against alternatives and does not fall through by default. A boundary using <= instead of < often attempts one extra iteration.

## 1. Trace a prefix sum: change one input

Copy worked example 1, change `items := []int{2, 4, 6}` to `items := []int{3, 4, 6}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
items := []int{2, 4, 6}
sum := 0
for _, x := range items {
	sum += x
}
check(sum == 12 && len(items) == 3, "sum")
```

**Expected:** The edited run panics with `sum` because `sum == 12 && len(items) == 3` no longer holds.

**Verify:** Restoring `items := []int{2, 4, 6}` makes the check pass again with the worked observation: the final sum is 12 and three elements were visited.

The accumulator starts at the additive identity. Each iteration includes exactly one new value; double addition or a skipped element breaks the independently known total.

## 2. Handle empty data: debug a regression

A one-token regression in worked example 2 makes a line read `sum := 1`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
sum := 0
for _, x := range []int{} {
	sum += x
}
check(sum == 0, "empty sum")
```

**Expected:** The defective run panics with `empty sum`; after restoring `sum := 0`, the result is 0 with no special invented element.

**Verify:** The failing run shows message `empty sum`; after the repair `sum == 0` holds again.

The loop body never runs. A correct initial state makes the empty case follow from the same algorithm rather than a separate patch.

## 3. Use a safe guard

Guard access to the first element of an empty slice with a length check.

```go
items := []int{}
positive := len(items) > 0 && items[0] > 0
check(!positive, "guard")
```

**Expected:** The condition is false and no indexing occurs.

**Verify:** Your solution must keep `!positive` true. Control: changing `check(!positive, "guard")` to `check(positive, "guard")` panics with message `guard`; revert it.

Reversing the operands would index before proving a valid position. Short-circuit behavior is part of this safety argument.

## 4. Find the first match

Find the first 8 in 3, 8, 8.

```go
found := -1
for i, x := range []int{3, 8, 8} {
	if x == 8 {
		found = i
		break
	}
}
check(found == 1, "first match")
```

**Expected:** Its index is 1.

**Verify:** Your solution must keep `found == 1` true. Control: changing `if x == 8 {` to `if x != 8 {` panics with message `first match`; revert it.

Without break, the later match replaces the first one. The -1 sentinel distinguishes absence from a valid first index of zero.

## 5. Classify an exact boundary

Classify a score of 60 as pass using a threshold of 60.

```go
score := 60
label := "fail"
if score >= 60 {
	label = "pass"
}
check(label == "pass", "inclusive boundary")
```

**Expected:** The boundary belongs to the passing branch.

**Verify:** Your solution must keep `label == "pass"` true. Control: changing `if score >= 60 {` to `if score > 60 {` panics with message `inclusive boundary`; revert it.

Boundary tests distinguish >= from >. Natural-language requirements should make inclusion explicit rather than leaving it to an arbitrary operator choice.

## 6. Transfer to a filtered count

Count nonnegative values in -2, 0, 4 and -1.

```go
count := 0
for _, x := range []int{-2, 0, 4, -1} {
	if x < 0 {
		continue
	}
	count++
}
check(count == 2, "filtered count")
```

**Expected:** Exactly 2 values satisfy the predicate.

**Verify:** Your solution must keep `count == 2` true. Control: changing `if x < 0 {` to `if x <= 0 {` panics with message `filtered count`; revert it.

continue avoids the increment for negative inputs. Zero is included deliberately, so the boundary case rejects a mistakenly positive-only predicate.

## Transfer after comparison

The habit to keep is naming the invariant before writing the loop. A prefix sum, a first-match search and a filtered count all start from a state that is already correct for zero elements, and each iteration preserves it. When later lessons loop over channels, informer events or retry attempts, state what is true before the first iteration and after each one, then test the empty and exact-boundary inputs first.
