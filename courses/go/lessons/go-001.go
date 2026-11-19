package main

import "fmt"

func main() {
	// Exercise 1: Predict a first value: change one input: Copy worked example 1 into a scratch pad and change `greeting := "Hello, Go"` to `greeting := "Hello, Go!"`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.
	// Expected: The changed run panics with `greeting` because `greeting == "Hello, Go"` no longer holds. Restoring the original line brings back the worked observation: greeting equals Hello, Go.

	// Exercise 2: Compute before formatting: debug a regression: A regression changed one token in worked example 2, so one line now reads `total := 2 - 3`. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check.
	// Expected: Before the repair the program panics with `format`; after it the line reads `total := 2 + 3` again and the integer is 5 and the text is total=5.

	// Exercise 3: Trace statement order: Start count at 1, add 1, then multiply by 3.
	// Expected: The final count is 6.

	// Exercise 4: Distinguish zero initialization: Declare an int and a bool without explicit values.
	// Expected: The values are 0 and false.

	// Exercise 5: Repair a naming assumption: Bind total and Total to different integers and compare them.
	// Expected: The names refer to distinct variables.

	// Exercise 6: Transfer to a receipt: Format an item count of 4 and unit price of 6 as amount=24.
	// Expected: The checked result is amount=24.

	fmt.Println("Implement the six investigations in your saved pad.")
}
