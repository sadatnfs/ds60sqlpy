package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Counter struct{ N int }

func (c Counter) Value() int       { return c.N }
func (c *Counter) Add(n int)       { c.N += n }
func (c Counter) Incremented() int { c.N++; return c.N }

type Valuer interface{ Value() int }
type Fixed int

func (f Fixed) Value() int   { return int(f) }
func readValue(v Valuer) int { return v.Value() }

func main() {
	// Dispatch through behavior
	{
		var v Valuer = Counter{N: 3}
		check(v.Value() == 3, "interface dispatch")
	}

	// Mutate through a method
	{
		c := Counter{N: 3}
		c.Add(2)
		check(c.N == 5, "pointer receiver")
	}

	// Trace a value receiver
	{
		c := Counter{N: 3}
		got := c.Incremented()
		check(got == 4 && c.N == 3, "receiver copy")
	}

	// Expose typed nil
	{
		var p *Counter
		var item any = p
		check(item != nil, "typed nil")
	}

	// Use safe dynamic inspection
	{
		var item any = "three"
		_, ok := item.(int)
		check(!ok, "type assertion")
	}

	// Transfer substitutability
	{
		check(readValue(Counter{N: 2}) == 2 && readValue(Fixed(8)) == 8, "substitution")
	}
	fmt.Println("All lesson checks passed.")
}
