# go-001: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A Go program is source text organized into packages. A runnable executable needs package main and a function named main with no arguments or return values. The compiler checks names and types before any statement executes. A successful build creates machine code for a particular operating system and processor architecture; the source file itself is not the executable. Inside a single goroutine, statements follow the program's control flow. Printing a reassuring message proves only that a print statement ran. A useful reference instead computes a result and checks an independently known expectation. This distinction becomes important when later lessons contain cancellation, partial failure and distributed state.

package declares the compilation unit's package. import makes another package available under a name such as fmt. func main() declares the entrypoint; braces delimit its body. A short declaration with := creates a variable and infers its type. fmt.Sprintf constructs text while fmt.Println writes it. Go inserts many semicolons automatically, so keep an opening brace on the declaration line. The helper check(condition, message) panics on false; its message should identify the broken claim.

## 1. Predict a first value

Bind greeting to Hello, Go and check its exact text.

```go
greeting := "Hello, Go"
check(greeting == "Hello, Go", "greeting")
```

**Expected:** greeting equals Hello, Go.

The quotes delimit a string literal; they are not part of the stored value. Matching the exact text catches a changed greeting even if printing would still look reasonable.

## 2. Compute before formatting

Add 2 and 3, then format total=5.

```go
total := 2 + 3
line := fmt.Sprintf("total=%d", total)
check(total == 5 && line == "total=5", "format")
```

**Expected:** The integer is 5 and the text is total=5.

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

Multiplication observes the already-incremented value. Reversing the last two statements produces 4, so source order is part of the contract.

## 4. Distinguish zero initialization

Declare an int and a bool without explicit values.

```go
var n int
var ready bool
check(n == 0 && !ready, "zero values")
```

**Expected:** The values are 0 and false.

Every declared Go variable has a defined zero value. That avoids uninitialized numeric storage, but zero may still be an invalid domain value that requires validation.

## 5. Repair a naming assumption

Bind total and Total to different integers and compare them.

```go
total := 3
Total := 7
check(total != Total, "case-sensitive names")
```

**Expected:** The names refer to distinct variables.

Identifier case matters. Export rules use capitalization across package boundaries; local variables with different case remain separate bindings.

## 6. Transfer to a receipt

Format an item count of 4 and unit price of 6 as amount=24.

```go
items, unit := 4, 6
receipt := fmt.Sprintf("amount=%d", items*unit)
check(receipt == "amount=24", "receipt")
```

**Expected:** The checked result is amount=24.

This combines calculation and representation while keeping the expected result independently inspectable. The example assumes whole units; currency rounding needs a separate policy.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
