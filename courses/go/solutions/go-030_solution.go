package main

import (
	"fmt"
	"sort"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Find a lower boundary
	{
		items := []int{2, 4, 6, 8}
		i := sort.Search(len(items), func(i int) bool { return items[i] >= 5 })
		check(i == 2, "boundary")
	}

	// Represent no match
	{
		items := []int{2, 4, 6, 8}
		i := sort.Search(len(items), func(i int) bool { return items[i] >= 9 })
		check(i == len(items), "not found")
	}

	// Separate length and capacity
	{
		items := make([]int, 0, 4)
		items = append(items, 7)
		check(len(items) == 1 && cap(items) == 4 && items[0] == 7, "capacity")
	}

	// Count linear work
	{
		visits, sum := 0, 0
		for _, v := range []int{1, 2, 3, 4, 5} {
			visits++
			sum += v
		}
		check(visits == 5 && sum == 15, "work")
	}

	// Handle empty search
	{
		calls := 0
		i := sort.Search(0, func(i int) bool { calls++; return true })
		check(i == 0 && calls == 0, "empty")
	}

	// Transfer duplicate boundaries
	{
		items := []int{1, 3, 3, 5}
		i := sort.Search(len(items), func(i int) bool { return items[i] >= 3 })
		check(i == 1, "duplicates")
	}
	fmt.Println("All lesson checks passed.")
}
