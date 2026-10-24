# go-021: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A command-line interface translates external strings into validated application configuration. Defaults, flags, environment and configuration files need an explicit precedence order; silently mixing them creates surprising deployments. Parse configuration once at the boundary and pass a typed value to the program. The browser pad has no arbitrary argument channel, so this lesson uses an isolated flag.FlagSet with synthetic argument slices. This exercises the real parser without changing the process global flags. A production CLI also needs clear help, stable exit codes, redacted diagnostics and a documented distinction between malformed input and runtime failure.

flag.NewFlagSet with ContinueOnError returns parse failures instead of exiting the process. IntVar binds a flag to storage, Parse accepts a []string and Args returns positional leftovers. SetOutput can redirect diagnostics to a buffer for tests. Do not call os.Exit from a library helper, because it prevents its caller from controlling cleanup and testing. Validate ranges after parsing: the parser can accept a negative integer even if the domain forbids it.

## 1. Apply an explicit flag

Parse -count=3 with a default of 1.

```go
n, args, err := parseArgs([]string{"-count=3"})
check(err == nil && n == 3 && len(args) == 0, "flag")
```

**Expected:** The resulting count is 3.

The synthetic argument slice tests the actual parser while remaining independent of the classroom process arguments.

## 2. Retain a default

Parse no arguments.

```go
n, _, err := parseArgs(nil)
check(err == nil && n == 1, "default")
```

**Expected:** The count remains 1.

A default is an intentional contract, not an accidental zero value. Changing it can alter existing workflows even when parsing code is unchanged.

## 3. Reject an unknown option

Parse -mystery=2.

```go
_, _, err := parseArgs([]string{"-mystery=2"})
check(err != nil, "unknown option")
```

**Expected:** Parsing returns an error.

Unknown-flag rejection catches misspellings. Ignoring them would make users believe a setting was applied when it was not.

## 4. Preserve positional arguments

Parse a count flag followed by a filename.

```go
_, args, err := parseArgs([]string{"-count=2", "input.csv"})
check(err == nil && len(args) == 1 && args[0] == "input.csv", "positionals")
```

**Expected:** The remaining argument is input.csv.

Flags and positional arguments have distinct roles. Validate their count and interpretation before opening any file.

## 5. Reject a domain-invalid count

Parse -count=-1 and perform range validation.

```go
_, _, err := parseArgs([]string{"-count=-1"})
check(err != nil, "range")
```

**Expected:** The operation returns a domain error.

Successful integer parsing does not imply an acceptable concurrency, retry or item-count budget.

## 6. Transfer precedence

Apply a flag override of 4 after a default value of 1.

```go
n, _, err := parseArgs([]string{"-count=4"})
check(err == nil && n == 4, "precedence")
```

**Expected:** The explicit setting wins.

In a larger program, document whether flags override environment or files. Avoid repeated environment reads deep inside business logic.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
