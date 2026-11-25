# go-001: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-001_solution.go` implements all six cases.

## Mechanism

A Go program is source text organized into packages. A runnable executable needs package main and a function named main with no arguments or return values. The compiler checks names and types before any statement executes. A successful build creates machine code for a particular operating system and processor architecture; the source file itself is not the executable. Inside a single goroutine, statements follow the program's control flow. Printing a reassuring message proves only that a print statement ran. A useful reference instead computes a result and checks an independently known expectation. This distinction becomes important when later lessons contain cancellation, partial failure and distributed state.

package declares the compilation unit's package. import makes another package available under a name such as fmt. func main() declares the entrypoint; braces delimit its body. A short declaration with := creates a variable and infers its type. fmt.Sprintf constructs text while fmt.Println writes it. Go inserts many semicolons automatically, so keep an opening brace on the declaration line. The helper check(condition, message) panics on false; its message should identify the broken claim.

## 1. Predict a first value: change one input

Copy worked example 1, change `greeting := "Hello, Go"` to `greeting := "Hello, Go!"` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
greeting := "Hello, Go"
check(greeting == "Hello, Go", "greeting")
```

**Expected:** The edited run panics with `greeting` because `greeting == "Hello, Go"` no longer holds.

**Verify:** Restoring `greeting := "Hello, Go"` makes the check pass again with the worked observation: greeting equals Hello, Go.

The quotes delimit a string literal; they are not part of the stored value. Matching the exact text catches a changed greeting even if printing would still look reasonable.

## 2. Compute before formatting: debug a regression

A one-token regression in worked example 2 makes a line read `total := 2 - 3`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
total := 2 + 3
line := fmt.Sprintf("total=%d", total)
check(total == 5 && line == "total=5", "format")
```

**Expected:** The defective run panics with `format`; after restoring `total := 2 + 3`, the integer is 5 and the text is total=5.

**Verify:** The failing run shows message `format`; after the repair `total == 5 && line == "total=5"` holds again.

The arithmetic result and its presentation are separate values. %d formats a decimal integer, and a wrong formatting verb can produce diagnostic text rather than the intended representation.

## 3. Trace statement order

Start count at 1, add 1, then multiply by 3.

```go
count := 1
count++
count *= 3
check(count == 6, "order")
```

**Expected:** The final count is 6.

**Verify:** Your solution must keep `count == 6` true. Control: changing `count := 1` to `count := 2` panics with message `order`; revert it.

Multiplication observes the already-incremented value. Reversing the last two statements produces 4, so source order is part of the contract.

## 4. Distinguish zero initialization

Declare an int and a bool without explicit values.

```go
var n int
var ready bool
check(n == 0 && !ready, "zero values")
```

**Expected:** The values are 0 and false.

**Verify:** Your solution must keep `n == 0 && !ready` true. Control: changing `check(n == 0 && !ready, "zero values")` to `check(n != 0 && !ready, "zero values")` panics with message `zero values`; revert it.

Every declared Go variable has a defined zero value. That avoids uninitialized numeric storage, but zero may still be an invalid domain value that requires validation.

## 5. Repair a naming assumption

Bind total and Total to different integers and compare them.

```go
total := 3
Total := 7
check(total != Total, "case-sensitive names")
```

**Expected:** The names refer to distinct variables.

**Verify:** Your solution must keep `total != Total` true. Control: changing `check(total != Total, "case-sensitive names")` to `check(total == Total, "case-sensitive names")` panics with message `case-sensitive names`; revert it.

Identifier case matters. Export rules use capitalization across package boundaries; local variables with different case remain separate bindings.

## 6. Transfer to a receipt

Format an item count of 4 and unit price of 6 as amount=24.

```go
items, unit := 4, 6
receipt := fmt.Sprintf("amount=%d", items*unit)
check(receipt == "amount=24", "receipt")
```

**Expected:** The checked result is amount=24.

**Verify:** Your solution must keep `receipt == "amount=24"` true. Control: changing `receipt := fmt.Sprintf("amount=%d", items*unit)` to `receipt := fmt.Sprintf("amount=%d", items+unit)` panics with message `receipt`; revert it.

This combines calculation and representation while keeping the expected result independently inspectable. The example assumes whole units; currency rounding needs a separate policy.

## Transfer after comparison

Carry the separation between computing and presenting into every later lesson. Each case here checked a value first (an integer, a bool, a string) and its formatted text second, so a wrong format verb and a wrong calculation fail differently. When a later lesson decodes JSON or reconciles a cluster object, ask the same two questions: which value is the result, and which check would notice if only its presentation changed?
