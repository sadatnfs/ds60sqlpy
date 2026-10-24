package main

import (
	"errors"
	"fmt"
	"slices"
	"sync"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type squareTask struct{ Index, Value int }

func parallelSquares(items []int, workers int) ([]int, error) {
	if workers < 1 || workers > 8 {
		return nil, errors.New("workers must be 1 through 8")
	}
	jobs := make(chan squareTask)
	results := make(chan squareTask)
	var wg sync.WaitGroup
	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for task := range jobs {
				task.Value *= task.Value
				results <- task
			}
		}()
	}
	go func() {
		for i, v := range items {
			jobs <- squareTask{i, v}
		}
		close(jobs)
	}()
	go func() { wg.Wait(); close(results) }()
	out := make([]int, len(items))
	for result := range results {
		out[result.Index] = result.Value
	}
	return out, nil
}

func main() {
	// Preserve input order
	{
		v, err := parallelSquares([]int{3, 1, 2}, 2)
		check(err == nil && len(v) == 3 && v[0] == 9 && v[1] == 1 && v[2] == 4, "order")
	}

	// Handle empty input
	{
		v, err := parallelSquares(nil, 2)
		check(err == nil && len(v) == 0, "empty")
	}

	// Reject absent capacity
	{
		_, err := parallelSquares([]int{1}, 0)
		check(err != nil, "zero workers")
	}

	// Compare serial semantics
	{
		a, e1 := parallelSquares([]int{1, 2, 3}, 1)
		b, e2 := parallelSquares([]int{1, 2, 3}, 3)
		check(e1 == nil && e2 == nil && slices.Equal(a, b), "same semantics")
	}

	// Retain duplicate tasks
	{
		v, err := parallelSquares([]int{2, 2, 2}, 2)
		check(err == nil && len(v) == 3 && v[2] == 4, "duplicates")
	}

	// Transfer idle-worker cleanup
	{
		v, err := parallelSquares([]int{5}, 4)
		check(err == nil && len(v) == 1 && v[0] == 25, "idle workers")
	}
	fmt.Println("All lesson checks passed.")
}
