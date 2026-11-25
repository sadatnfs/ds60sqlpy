# go-021: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-021_solution.go` implements all six cases.

## Mechanism

A command-line interface translates external strings into validated application configuration. Defaults, flags, environment and configuration files need an explicit precedence order; silently mixing them creates surprising deployments. Parse configuration once at the boundary and pass a typed value to the program. The browser pad has no arbitrary argument channel, so this lesson uses an isolated flag.FlagSet with synthetic argument slices. This exercises the real parser without changing the process global flags. A production CLI also needs clear help, stable exit codes, redacted diagnostics and a documented distinction between malformed input and runtime failure.

flag.NewFlagSet with ContinueOnError returns parse failures instead of exiting the process. IntVar binds a flag to storage, Parse accepts a []string and Args returns positional leftovers. SetOutput can redirect diagnostics to a buffer for tests. Do not call os.Exit from a library helper, because it prevents its caller from controlling cleanup and testing. Validate ranges after parsing: the parser can accept a negative integer even if the domain forbids it.

## 1. Apply an explicit flag: change one input

Copy worked example 1, change `n, args, err := parseArgs([]string{"-count=3"})` to `n, args, err := parseArgs([]string{"-count=4"})` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
n, args, err := parseArgs([]string{"-count=3"})
check(err == nil && n == 3 && len(args) == 0, "flag")
```

**Expected:** The edited run panics with `flag` because `err == nil && n == 3 && len(args) == 0` no longer holds.

**Verify:** Restoring `n, args, err := parseArgs([]string{"-count=3"})` makes the check pass again with the worked observation: the resulting count is 3.

The synthetic argument slice tests the actual parser while remaining independent of the classroom process arguments.

**Approach.** Run the edited slice through `parseArgs`. The flag set parses `-count=4` into `n`, finds no positional arguments and passes the range check, so it returns 4, an empty slice and nil.

**Why it holds here.** Only `n == 3` changes: `err == nil` and `len(args) == 0` still hold, so the conjunction fails on the count and panics with `flag`.

**A plausible wrong approach.** Writing the argument as one element `"-count 4"` because that is how it looks in a shell. No shell splits a synthetic slice, so the flag package reads the name `count 4` and returns `flag provided but not defined: -count 4`. The space form needs two elements, `"-count", "4"`.

**Verify.** Print `n, args, err` and see `4 [] <nil>` before the panic. Restoring `-count=3` restores the success line.

## 2. Retain a default: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `check(err != nil && n == 1, "default")`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
n, _, err := parseArgs(nil)
check(err == nil && n == 1, "default")
```

**Expected:** The defective run panics with `default`; after restoring `check(err == nil && n == 1, "default")`, the count remains 1.

**Verify:** The edited check fails with message `default` for a state that `err == nil && n == 1` accepts.

A default is an intentional contract, not an accidental zero value. Changing it can alter existing workflows even when parsing code is unchanged.

**Approach.** Call `parseArgs(nil)`. `IntVar` stores the default 1 in `n`, `Parse` succeeds with no arguments and 1 passes the range check, so the results are 1 and nil.

**Why it holds here.** The edited `err != nil` is false for that same state, so the check panics with `default`. The parse and the count are unchanged; only the expectation about the error was inverted.

**A plausible wrong approach.** Changing the `IntVar` default to 0 so that "unset" is visible. The domain check then rejects 0, and the bare command returns `positive count required`, so every existing invocation without `-count` breaks.

**Verify.** Print `n, err` for `parseArgs(nil)` and see `1 <nil>`, then restore the original check and read the success line.

## 3. Reject an unknown option

Parse -mystery=2.

```go
_, _, err := parseArgs([]string{"-mystery=2"})
check(err != nil, "unknown option")
```

**Expected:** Parsing returns an error.

**Verify:** Your solution must keep `err != nil` true. Control: changing `check(err != nil, "unknown option")` to `check(err == nil, "unknown option")` panics with message `unknown option`; revert it.

Unknown-flag rejection catches misspellings. Ignoring them would make users believe a setting was applied when it was not.

**Approach.** Parse `-mystery=2` with a flag set built using `flag.ContinueOnError` and output sent to `io.Discard`, so `Parse` returns an error instead of exiting or printing usage.

**Why it holds here.** No flag named `mystery` is defined, so `Parse` returns `flag provided but not defined: -mystery` and `parseArgs` passes it through, making `err != nil` true.

**A plausible wrong approach.** Building the set with `flag.ExitOnError`. On the unknown flag the package calls `os.Exit(2)`, so the program ends before `check` runs and nothing in the example can observe the error.

**Verify.** Print `err` and see `flag provided but not defined: -mystery`. A defined flag such as `-count=2` returns nil.

## 4. Preserve positional arguments

Parse a count flag followed by a filename.

```go
_, args, err := parseArgs([]string{"-count=2", "input.csv"})
check(err == nil && len(args) == 1 && args[0] == "input.csv", "positionals")
```

**Expected:** The remaining argument is input.csv.

**Verify:** Your solution must keep `err == nil && len(args) == 1 && args[0] == "input.csv"` true. Control: changing `_, args, err := parseArgs([]string{"-count=2", "input.csv"})` to `_, args, err := parseArgs([]string{"-count=2!", "input.csv"})` panics with message `positionals`; revert it.

Flags and positional arguments have distinct roles. Validate their count and interpretation before opening any file.

**Approach.** Parse `-count=2` followed by `input.csv`. Flag parsing stops at the first argument that is not a flag, and `f.Args()` returns the rest.

**Why it holds here.** `-count=2` sets `n`, then `input.csv` ends flag parsing, so `args` is `[input.csv]` and the count of 2 passes the range check.

**A plausible wrong approach.** Putting the filename first: `[]string{"input.csv", "-count=2"}`. Parsing stops at `input.csv`, so `-count=2` stays in `args` as a second positional and `n` keeps the default 1. `len(args) == 1` fails and the check panics with `positionals`.

**Verify.** Print `n, args` and see `2 [input.csv]`; the reversed order prints `1 [input.csv -count=2]`.

## 5. Reject a domain-invalid count

Parse -count=-1 and perform range validation.

```go
_, _, err := parseArgs([]string{"-count=-1"})
check(err != nil, "range")
```

**Expected:** The operation returns a domain error.

**Verify:** Your solution must keep `err != nil` true. Control: changing `check(err != nil, "range")` to `check(err == nil, "range")` panics with message `range`; revert it.

Successful integer parsing does not imply an acceptable concurrency, retry or item-count budget.

**Approach.** Parse `-count=-1`. `IntVar` accepts any signed integer, so parsing succeeds, and the separate check `n < 1` rejects the value.

**Why it holds here.** -1 is a well-formed `int`, so the flag package reports no error; only the domain check returns `positive count required`, which makes `err != nil` true.

**A plausible wrong approach.** Switching to `flag.UintVar` so the parser rejects negatives. That does reject `-1`, but `-count=0` parses as a valid `uint` and slips through, even though zero items is outside the domain.

**Verify.** Print `err` for `-count=-1` and for `-count=0` and see `positive count required` both times, while `-count=1` returns nil.

## 6. Transfer precedence

Apply a flag override of 4 after a default value of 1.

```go
n, _, err := parseArgs([]string{"-count=4"})
check(err == nil && n == 4, "precedence")
```

**Expected:** The explicit setting wins.

**Verify:** Your solution must keep `err == nil && n == 4` true. Control: changing `n, _, err := parseArgs([]string{"-count=4"})` to `n, _, err := parseArgs([]string{"-count=5"})` panics with message `precedence`; revert it.

In a larger program, document whether flags override environment or files. Avoid repeated environment reads deep inside business logic.

**Approach.** Parse `-count=4`. The flag set started with the default 1, and the explicit flag overwrites it during `Parse`.

**Why it holds here.** An explicit value is applied after the default, so `n` is 4 with no error. If the flag repeats, the last occurrence wins: `-count=4 -count=2` gives 2.

**A plausible wrong approach.** Deciding whether the user set the flag by comparing `n` with the default 1. An explicit `-count=1` looks identical to no flag, so a lower-priority environment value would wrongly win. `f.Visit` reports only the flags actually set.

**Verify.** Print `n` for `-count=4` and for `-count=4 -count=2` and see `4` and `2`.

## Transfer after comparison

Write `resolveCount(args []string, env map[string]string) (int, error)` with precedence flag, then `env["COUNT"]`, then the default 1, using `f.Visit` to learn whether `-count` was set. Check no flag and no env gives 1, env 3 gives 3, env 3 with `-count=1` gives 1 and `-count=0` returns an error. Explain why comparing with the default would get the third case wrong.
