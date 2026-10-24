package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Predict a first value
	{
		greeting := "Hello, Go"
		check(greeting == "Hello, Go", "greeting")
	}

	// Compute before formatting
	{
		total := 2 + 3
		line := fmt.Sprintf("total=%d", total)
		check(total == 5 && line == "total=5", "format")
	}

	// Trace statement order
	{
		count := 1
		count++
		count *= 3
		check(count == 6, "order")
	}

	// Distinguish zero initialization
	{
		var n int
		var ready bool
		check(n == 0 && !ready, "zero values")
	}

	// Repair a naming assumption
	{
		total := 3
		Total := 7
		check(total != Total, "case-sensitive names")
	}

	// Transfer to a receipt
	{
		items, unit := 4, 6
		receipt := fmt.Sprintf("amount=%d", items*unit)
		check(receipt == "amount=24", "receipt")
	}
	fmt.Println("All lesson checks passed.")
}
