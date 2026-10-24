package main

import (
	"fmt"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func deferOrder() (result string) {
	values := []string{}
	defer func() { result = strings.Join(values, ",") }()
	defer func() { values = append(values, "first") }()
	defer func() { values = append(values, "second") }()
	return
}
func deferArgument() (result int) { x := 1; defer func(v int) { result = v }(x); x = 2; return }
func deferClosure() (result int)  { x := 1; defer func() { result = x }(); x = 2; return }
func recoverKnown() (result string) {
	defer func() {
		if v := recover(); v != nil {
			result = fmt.Sprint(v)
		}
	}()
	panic("broken")
}
func cleanedAfterPanic() (cleaned bool) {
	defer func() { recover() }()
	defer func() { cleaned = true }()
	panic("fixture")
}
func scopedCleanup(count *int) { defer func() { *count = *count + 1 }() }

func main() {
	// Trace cleanup order
	{
		check(deferOrder() == "second,first", "defer order")
	}

	// Compare captured arguments
	{
		check(deferArgument() == 1, "argument evaluation")
	}

	// Compare a closure read
	{
		check(deferClosure() == 2, "closure read")
	}

	// Contain a deliberate panic
	{
		check(recoverKnown() == "broken", "recovered value")
	}

	// Preserve cleanup during failure
	{
		check(cleanedAfterPanic(), "cleanup on panic")
	}

	// Transfer function-scoped cleanup
	{
		count := 0
		for i := 0; i < 3; i++ {
			scopedCleanup(&count)
		}
		check(count == 3, "iteration cleanup")
	}
	fmt.Println("All lesson checks passed.")
}
