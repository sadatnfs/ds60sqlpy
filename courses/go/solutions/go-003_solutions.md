# go-003: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Control flow determines which statements execute. A condition is a boolean expression, not a number used as a truth value. Go's for statement covers counting loops, condition-controlled loops and collection iteration. The safest way to reason about a loop is to name an invariant: a statement true before the first iteration and preserved by every iteration. In a prefix sum, the accumulator contains exactly the elements already visited. Empty input is therefore not an exceptional accident; the initial accumulator already represents its result. Short-circuit operators also affect execution, which makes a guard before a potentially unsafe operation meaningful.

if condition { ... } selects a branch. && skips the right operand when the left is false. for i := 0; i < len(items); i++ visits a half-open index interval. break leaves the innermost loop; continue skips to its next iteration. switch compares one expression against alternatives and does not fall through by default. A boundary using <= instead of < often attempts one extra iteration.

## 1. Trace a prefix sum: change one input

Copy worked example 1 into a scratch pad and change `items := []int{2, 4, 6}` to `items := []int{3, 4, 6}`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
items := []int{2, 4, 6}
sum := 0
for _, x := range items {
	sum += x
}
check(sum == 12 && len(items) == 3, "sum")
```

**Expected:** The changed run panics with `sum` because `sum == 12 && len(items) == 3` no longer holds. Restoring the original line brings back the worked observation: the final sum is 12 and three elements were visited.

The accumulator starts at the additive identity. Each iteration includes exactly one new value; double addition or a skipped element breaks the independently known total.

## 2. Handle empty data: debug a regression

A regression changed one token in worked example 2, so one line now reads `sum := 1`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.

The unchanged code is worked example 2:

```go
sum := 0
for _, x := range []int{} {
	sum += x
}
check(sum == 0, "empty sum")
```

**Expected:** Before the repair the program panics with `empty sum`; after it the line reads `sum := 0` again and the result is 0 with no special invented element.

The loop body never runs. A correct initial state makes the empty case follow from the same algorithm rather than a separate patch.

## 3. Use a safe guard

Guard access to the first element of an empty slice with a length check.

```go
items := []int{}
positive := len(items) > 0 && items[0] > 0
check(!positive, "guard")
```

**Expected:** The condition is false and no indexing occurs.

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

continue avoids the increment for negative inputs. Zero is included deliberately, so the boundary case rejects a mistakenly positive-only predicate.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
