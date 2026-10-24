package main

import (
	"context"
	"fmt"
	"time"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func contextValue(ctx context.Context, x int) (int, error) {
	if err := ctx.Err(); err != nil {
		return 0, err
	}
	return 2 * x, nil
}

func main() {
	// Cancel a child
	{
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		check(ctx.Err() == context.Canceled, "cancel")
	}

	// Propagate parent cancellation
	{
		parent, cancel := context.WithCancel(context.Background())
		child, stop := context.WithCancel(parent)
		defer stop()
		cancel()
		check(parent.Err() == context.Canceled && child.Err() == context.Canceled, "tree")
	}

	// Keep child cancellation local
	{
		parent := context.Background()
		child, cancel := context.WithCancel(parent)
		cancel()
		check(child.Err() != nil && parent.Err() == nil, "child")
	}

	// Test an expired deadline
	{
		ctx, cancel := context.WithDeadline(context.Background(), time.Unix(0, 0))
		defer cancel()
		check(ctx.Err() == context.DeadlineExceeded, "deadline")
	}

	// Refuse already canceled work
	{
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		v, err := contextValue(ctx, 4)
		check(v == 0 && err == context.Canceled, "refusal")
	}

	// Transfer successful work
	{
		v, err := contextValue(context.Background(), 4)
		check(err == nil && v == 8, "live")
	}
	fmt.Println("All lesson checks passed.")
}
