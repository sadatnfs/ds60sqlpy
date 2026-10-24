package main

import (
	"fmt"
	"math"
	"strconv"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Compare two divisions
	{
		a := 7 / 2
		b := float64(7) / 2
		check(a == 3 && b == 3.5, "division")
	}

	// Expose narrowing
	{
		n := 260
		small := uint8(n)
		check(small == 4, "narrowing")
	}

	// Preserve a wide product
	{
		a, b := int64(50000), int64(50000)
		check(a*b == 2500000000, "wide product")
	}

	// Check approximate arithmetic
	{
		a, b := 0.1, 0.2
		check(math.Abs((a+b)-0.3) < 1e-15, "rounding")
	}

	// Reject invalid numeric text
	{
		_, err := strconv.ParseInt("12x", 10, 64)
		check(err != nil, "invalid number")
	}

	// Transfer signed division
	{
		q, r := -7/2, -7%2
		check(q == -3 && r == -1 && q*2+r == -7, "signed division")
	}
	fmt.Println("All lesson checks passed.")
}
