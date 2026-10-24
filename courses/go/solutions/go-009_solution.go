package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func increment(p *int) { *p = *p + 1 }
func seven() *int      { n := 7; return &n }
func setIfPresent(p *int, v int) bool {
	if p == nil {
		return false
	}
	*p = v
	return true
}

func main() {
	// Mutate through a pointer
	{
		n := 4
		increment(&n)
		check(n == 5, "pointer mutation")
	}

	// Return a live value
	{
		p := seven()
		check(*p == 7, "returned pointer")
	}

	// Guard absence
	{
		var p *int
		check(p == nil, "nil pointer")
	}

	// Allocate a zero target
	{
		p := new(int)
		check(p != nil && *p == 0, "new zero")
	}

	// Separate copy and target
	{
		n := 3
		p := &n
		copied := *p
		*p = 9
		check(copied == 3 && n == 9, "copy target")
	}

	// Transfer an optional update
	{
		check(!setIfPresent(nil, 8), "absent update")
		n := 1
		check(setIfPresent(&n, 8) && n == 8, "present update")
	}
	fmt.Println("All lesson checks passed.")
}
