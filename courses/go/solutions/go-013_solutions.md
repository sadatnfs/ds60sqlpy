# go-013: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A package is a compilation and visibility boundary; a module is a versioned collection of packages described by go.mod. An import path identifies a package, not an operating-system filename. Capitalized declarations are exported to other packages. The main package creates an executable, while reusable packages expose focused APIs. go.sum records module-content checksums but is not a substitute for reviewing dependency changes. An offline classroom pad cannot become a multi-file dependency project by containing a go.mod string. This lesson executes standard-library boundary examples and separately teaches the real project layout. Keep generated outputs, dependency selection and application source under distinct review.

The standard library already contains packages such as path, strings and strconv. An alias in an import declaration changes the local selector name, not the dependency's identity. For a real project, run go mod init example.org/learning/report in a prepared directory, place reusable code under a package folder, and use go test ./... plus go build ./cmd/report. Pin reviewed dependency versions with go get and commit go.mod and go.sum. Dependency retrieval is explicit setup, never a side effect of opening a lesson.

## 1. Use a package boundary

Join logical slash-separated path segments with path.Join.

```go
check(path.Join("reports", "daily.json") == "reports/daily.json", "path package")
```

**Expected:** The result is reports/daily.json.

path works with slash-separated logical paths. filepath is a different package whose behavior follows the host operating system.

## 2. Compose standard-library APIs

Trim and parse the text containing spaces around 12.

```go
v, err := strconv.Atoi(strings.TrimSpace(" 12 "))
check(err == nil && v == 12, "package composition")
```

**Expected:** The parsed value is 12.

Each package contributes a small contract. Trimming is an explicit input policy, while numeric parsing remains independently fallible.

## 3. Inspect exported spelling

Compare a public API spelling with its lower-case variant as identifiers in a naming check.

```go
name := "ParseInt"
check(unicode.IsUpper([]rune(name)[0]), "export convention")
```

**Expected:** The public spelling begins with an uppercase rune.

This checks the naming convention rather than trying to access an unexported symbol. Actual visibility is enforced by the compiler across package boundaries.

## 4. Keep logical imports separate

Clean a logical path containing a parent component.

```go
check(path.Clean("reports/tmp/../daily") == "reports/daily", "logical clean")
```

**Expected:** reports/tmp/../daily becomes reports/daily.

Cleaning a path is not authorization to access it. Real filesystem access needs confinement and symlink-aware policy, taught later.

## 5. Reject malformed input at an API boundary

Parse a nonnumeric public input after trimming.

```go
_, err := strconv.Atoi(strings.TrimSpace(" none "))
check(err != nil, "boundary error")
```

**Expected:** The numeric error remains non-nil.

Packaging does not remove the need for validation. The wrapper should preserve a cause rather than return a plausible zero as if parsing succeeded.

## 6. Transfer an API contract

Build a deterministic report name from a validated positive integer.

```go
day, err := strconv.Atoi("3")
check(err == nil && day > 0, "day")
name := path.Join("reports", fmt.Sprintf("day-%d.json", day))
check(name == "reports/day-3.json", "report name")
```

**Expected:** The resulting logical name is reports/day-3.json.

The boundary validates a domain value before formatting it into a path. Arbitrary user path fragments are not accepted by this contract.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
