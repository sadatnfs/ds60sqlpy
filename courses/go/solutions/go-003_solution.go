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
	// Trace a prefix sum
	{
		items := []int{2, 4, 6}
		sum := 0
		for _, x := range items {
			sum += x
		}
		check(sum == 12 && len(items) == 3, "sum")
	}

	// Handle empty data
	{
		sum := 0
		for _, x := range []int{} {
			sum += x
		}
		check(sum == 0, "empty sum")
	}

	// Use a safe guard
	{
		items := []int{}
		positive := len(items) > 0 && items[0] > 0
		check(!positive, "guard")
	}

	// Find the first match
	{
		found := -1
		for i, x := range []int{3, 8, 8} {
			if x == 8 {
				found = i
				break
			}
		}
		check(found == 1, "first match")
	}

	// Classify an exact boundary
	{
		score := 60
		label := "fail"
		if score >= 60 {
			label = "pass"
		}
		check(label == "pass", "inclusive boundary")
	}

	// Transfer to a filtered count
	{
		count := 0
		for _, x := range []int{-2, 0, 4, -1} {
			if x < 0 {
				continue
			}
			count++
		}
		check(count == 2, "filtered count")
	}
	fmt.Println("All lesson checks passed.")
}
