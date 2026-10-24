package main

import (
	"fmt"
	"sync"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func main() {
	// Join a produced result
	{
		result := make(chan int)
		go func() { result <- 6 * 7 }()
		check(<-result == 42, "goroutine result")
	}

	// Wait for several tasks
	{
		done := make(chan struct{}, 3)
		var wg sync.WaitGroup
		for i := 0; i < 3; i++ {
			wg.Add(1)
			go func() { defer wg.Done(); done <- struct{}{} }()
		}
		wg.Wait()
		check(len(done) == 3, "joined tasks")
	}

	// Keep state task-local
	{
		out := make(chan int, 2)
		for _, n := range []int{2, 3} {
			go func(x int) { out <- x * x }(n)
		}
		a, b := <-out, <-out
		check(a+b == 13, "local inputs")
	}

	// Establish a start boundary
	{
		start := make(chan struct{})
		out := make(chan string)
		go func() { <-start; out <- "ready" }()
		close(start)
		check(<-out == "ready", "start boundary")
	}

	// Reject premature completion
	{
		start := make(chan struct{})
		out := make(chan int)
		go func() { <-start; out <- 1 }()
		premature := false
		select {
		case <-out:
			premature = true
		default:
		}
		check(!premature, "premature completion")
		close(start)
		check(<-out == 1, "released result")
	}

	// Transfer deterministic aggregation
	{
		out := make(chan int, 4)
		for _, n := range []int{1, 2, 3, 4} {
			go func(x int) { out <- x * x }(n)
		}
		sum := 0
		for i := 0; i < 4; i++ {
			sum += <-out
		}
		check(sum == 30, "aggregation")
	}
	fmt.Println("All lesson checks passed.")
}
