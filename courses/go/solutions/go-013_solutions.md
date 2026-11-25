# go-013: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-013_solution.go` implements all six cases.

## Mechanism

A package is a compilation and visibility boundary; a module is a versioned collection of packages described by go.mod. An import path identifies a package, not an operating-system filename. Capitalized declarations are exported to other packages. The main package creates an executable, while reusable packages expose focused APIs. go.sum records module-content checksums but is not a substitute for reviewing dependency changes. An offline classroom pad cannot become a multi-file dependency project by containing a go.mod string. This lesson executes standard-library boundary examples and separately teaches the real project layout. Keep generated outputs, dependency selection and application source under distinct review.

The standard library already contains packages such as path, strings and strconv. An alias in an import declaration changes the local selector name, not the dependency's identity. For a real project, run go mod init example.org/learning/report in a prepared directory, place reusable code under a package folder, and use go test ./... plus go build ./cmd/report. Pin reviewed dependency versions with go get and commit go.mod and go.sum. Dependency retrieval is explicit setup, never a side effect of opening a lesson. A go.mod file starts with the module path, then a go line such as go 1.27 that states the minimum Go version the module needs, and optionally a toolchain line such as toolchain go1.27.3 that names a suggested newer toolchain. The GOTOOLCHAIN environment variable decides whether the go command may switch to another toolchain; local means it never does.

## 1. Use a package boundary: predict an edited check

Copy worked example 1, change `check(path.Join("reports", "daily.json") == "reports/daily.json", "path package")` to `check(path.Join("reports!", "daily.json") == "reports/daily.json", "path package")` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
check(path.Join("reports", "daily.json") == "reports/daily.json", "path package")
```

**Expected:** The edited check panics with `path package` even though `path.Join("reports", "daily.json") == "reports/daily.json"` still holds.

**Verify:** Restoring `check(path.Join("reports", "daily.json") == "reports/daily.json", "path package")` makes the check pass again with the worked observation: the result is reports/daily.json.

path works with slash-separated logical paths. filepath is a different package whose behavior follows the host operating system.

## 2. Compose standard-library APIs: debug a regression

A one-token regression in worked example 2 makes a line read `v, err := strconv.Atoi(strings.TrimSpace(" 13 "))`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
v, err := strconv.Atoi(strings.TrimSpace(" 12 "))
check(err == nil && v == 12, "package composition")
```

**Expected:** The defective run panics with `package composition`; after restoring `v, err := strconv.Atoi(strings.TrimSpace(" 12 "))`, the parsed value is 12.

**Verify:** The failing run shows message `package composition`; after the repair `err == nil && v == 12` holds again.

Each package contributes a small contract. Trimming is an explicit input policy, while numeric parsing remains independently fallible.

## 3. Inspect exported spelling

Classify ParseInt, parseInt and an empty name with one rule: a name is exported when its first rune is an uppercase letter.

```go
exported := func(name string) bool { return name != "" && unicode.IsUpper([]rune(name)[0]) }
check(exported("ParseInt") && !exported("parseInt") && !exported(""), "export convention")
```

**Expected:** Only ParseInt is exported.

**Verify:** Your solution must keep `exported("ParseInt") && !exported("parseInt") && !exported("")` true. Control: changing `exported := func(name string) bool { return name != "" && unicode.IsUpper([]rune(name)[0]) }` to `exported := func(name string) bool { return name == "" && unicode.IsUpper([]rune(name)[0]) }` panics with message `export convention`; revert it.

The rule is applied to three spellings instead of re-reading one literal. Actual visibility is enforced by the compiler across package boundaries: another package can call strconv.ParseInt, while a lower-case declaration stays private to its own package.

## 4. Read the go and toolchain directives

Extract the module, go and toolchain lines from a small go.mod text.

```go
mod := "module example.org/learning/report\n\ngo 1.27\n\ntoolchain go1.27.3\n"
directives := map[string]string{}
for _, line := range strings.Split(mod, "\n") {
	fields := strings.Fields(line)
	if len(fields) == 2 {
		directives[fields[0]] = fields[1]
	}
}
check(directives["module"] == "example.org/learning/report" && directives["go"] == "1.27" && directives["toolchain"] == "go1.27.3", "directives")
```

**Expected:** The module requires Go 1.27 and suggests toolchain go1.27.3.

**Verify:** Your solution must keep `directives["module"] == "example.org/learning/report" && directives["go"] == "1.27" && directives["toolchain"] == "go1.27.3"` true. Control: changing `if len(fields) == 2 {` to `if len(fields) == 3 {` panics with message `directives`; revert it.

The go line is the minimum Go version the module requires. Since Go 1.21 an older go command does not build such a module with its own toolchain: it switches to a newer toolchain when GOTOOLCHAIN allows that, or stops with an error. The toolchain line suggests a specific newer toolchain for work inside this module. The classroom worker sets GOTOOLCHAIN=local, so a module that asks for a newer version fails with an explicit error instead of downloading anything.

## 5. Reject malformed input at an API boundary

Parse a nonnumeric public input after trimming.

```go
_, err := strconv.Atoi(strings.TrimSpace(" none "))
check(err != nil, "boundary error")
```

**Expected:** The numeric error remains non-nil.

**Verify:** Your solution must keep `err != nil` true. Control: changing `check(err != nil, "boundary error")` to `check(err == nil, "boundary error")` panics with message `boundary error`; revert it.

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

**Verify:** Your solution must keep `name == "reports/day-3.json"` true. Control: changing `day, err := strconv.Atoi("3")` to `day, err := strconv.Atoi("4")` panics with message `report name`; revert it.

The boundary validates a domain value before formatting it into a path. Arbitrary user path fragments are not accepted by this contract.

## Transfer after comparison

Every later project in this track is a module with deliberate package boundaries. Before adding a file, decide which package owns it, what it exports and which packages may import it. When the Kubernetes lessons pull in client-go, the same questions apply to a large dependency: which version go.mod selects, what go.sum pins and which internal details your code must not rely on.
