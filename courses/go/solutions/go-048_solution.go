package main

import (
	"context"
	"errors"
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type CapState struct {
	UID             string
	Current, Writes int
}

func reconcileCap(ctx context.Context, s *CapState, expectedUID string, wanted int) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	if s.UID != expectedUID {
		return errors.New("ownership mismatch")
	}
	if wanted < 0 {
		return errors.New("invalid count")
	}
	if s.Current != wanted {
		s.Current = wanted
		s.Writes++
	}
	return nil
}

func main() {
	// Converge from a different state
	{
		s := CapState{UID: "u1", Current: 1}
		err := reconcileCap(context.Background(), &s, "u1", 3)
		check(err == nil && s.Current == 3 && s.Writes == 1, "converge")
	}

	// Repeat without duplicate writes
	{
		s := CapState{UID: "u1", Current: 1}
		check(reconcileCap(context.Background(), &s, "u1", 3) == nil, "first")
		check(reconcileCap(context.Background(), &s, "u1", 3) == nil && s.Writes == 1, "idempotent")
	}

	// Refuse a replacement object
	{
		s := CapState{UID: "new", Current: 1}
		err := reconcileCap(context.Background(), &s, "old", 3)
		check(err != nil && s.Current == 1 && s.Writes == 0, "ownership")
	}

	// Preserve state on invalid intent
	{
		s := CapState{UID: "u1", Current: 1}
		err := reconcileCap(context.Background(), &s, "u1", -1)
		check(err != nil && s.Current == 1 && s.Writes == 0, "invalid")
	}

	// Cancel before new work
	{
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		s := CapState{UID: "u1", Current: 1}
		err := reconcileCap(ctx, &s, "u1", 3)
		check(errors.Is(err, context.Canceled) && s.Writes == 0, "cancel")
	}

	// Transfer restart reasoning
	{
		s := CapState{UID: "u1", Current: 3, Writes: 1}
		restored := s
		check(reconcileCap(context.Background(), &restored, "u1", 3) == nil && restored.Writes == 1, "restart")
	}
	fmt.Println("All lesson checks passed.")
}
