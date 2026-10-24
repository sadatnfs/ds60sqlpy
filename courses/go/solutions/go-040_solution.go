package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func delay(attempt int) int {
	if attempt < 0 {
		return 1
	}
	if attempt >= 3 {
		return 8
	}
	return 1 << attempt
}
func retryable(class string) bool { return class == "transient" }

func main() {
	// Calculate increasing delay
	{
		check(delay(0) == 1 && delay(1) == 2 && delay(2) == 4, "growth")
	}

	// Cap the delay
	{
		check(delay(3) == 8 && delay(10) == 8, "cap")
	}

	// Coalesce duplicate keys
	{
		pending := map[string]bool{}
		for _, key := range []string{"alpha", "alpha", "beta"} {
			pending[key] = true
		}
		check(len(pending) == 2, "coalesce")
	}

	// Separate invalid from transient
	{
		check(!retryable("invalid") && retryable("transient"), "classification")
	}

	// Reset successful history
	{
		attempts := map[string]int{"demo": 3}
		delete(attempts, "demo")
		check(delay(attempts["demo"]) == 1, "reset")
	}

	// Transfer a total budget
	{
		admitted := 0
		for attempt := 0; attempt < 5; attempt++ {
			if attempt < 3 {
				admitted++
			}
		}
		check(admitted == 3, "budget")
	}
	fmt.Println("All lesson checks passed.")
}
