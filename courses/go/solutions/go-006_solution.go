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
	// Distinguish zero from missing
	{
		m := map[string]int{"zero": 0}
		a, okA := m["zero"]
		b, okB := m["missing"]
		check(a == b && okA && !okB, "presence")
	}

	// Build a frequency table
	{
		m := map[string]int{}
		for _, v := range []string{"red", "blue", "red"} {
			m[v]++
		}
		check(m["red"] == 2 && m["blue"] == 1, "counts")
	}

	// Sort report keys
	{
		m := map[string]int{"beta": 2, "alpha": 1}
		keys := []string{}
		for k := range m {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		check(keys[0] == "alpha" && keys[1] == "beta", "sorted keys")
	}

	// Observe assigned map aliasing
	{
		a := map[string]int{"x": 1}
		b := a
		b["x"] = 2
		check(a["x"] == 2, "map alias")
	}

	// Remove an absent key safely
	{
		m := map[string]int{"x": 1}
		delete(m, "absent")
		delete(m, "x")
		check(len(m) == 0, "delete")
	}

	// Transfer nil read behavior
	{
		var m map[string]int
		v, ok := m["x"]
		check(v == 0 && !ok, "nil read")
	}
	fmt.Println("All lesson checks passed.")
}
