package main

import "fmt"

func main() {
	// Exercise 1: Use a package boundary: predict an edited check: Copy worked example 1 into a scratch pad and change `check(path.Join("reports", "daily.json") == "reports/daily.json", "path package")` to `check(path.Join("reports!", "daily.json") == "reports/daily.json", "path package")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.
	// Expected: The changed run panics with `path package` because the edited check no longer holds. Restoring the original line brings back the worked observation: the result is reports/daily.json.

	// Exercise 2: Compose standard-library APIs: debug a regression: A regression changed one token in worked example 2, so one line now reads `v, err := strconv.Atoi(strings.TrimSpace(" 13 "))`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `package composition`; after it the line reads `v, err := strconv.Atoi(strings.TrimSpace(" 12 "))` again and the parsed value is 12.

	// Exercise 3: Inspect exported spelling: Classify ParseInt, parseInt and an empty name with one rule: a name is exported when its first rune is an uppercase letter.
	// Expected: Only ParseInt is exported.

	// Exercise 4: Read the go and toolchain directives: Extract the module, go and toolchain lines from a small go.mod text.
	// Expected: The module requires Go 1.27 and suggests toolchain go1.27.3.

	// Exercise 5: Reject malformed input at an API boundary: Parse a nonnumeric public input after trimming.
	// Expected: The numeric error remains non-nil.

	// Exercise 6: Transfer an API contract: Build a deterministic report name from a validated positive integer.
	// Expected: The resulting logical name is reports/day-3.json.

	fmt.Println("Implement the six investigations in your saved pad.")
}
