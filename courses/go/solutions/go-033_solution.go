package main

import (
	"errors"
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Balances struct{ A, B int }

func transact(s *Balances, f func(*Balances) error) error {
	copy := *s
	if err := f(&copy); err != nil {
		return err
	}
	*s = copy
	return nil
}

func main() {
	// Commit a valid change
	{
		s := Balances{A: 5, B: 5}
		err := transact(&s, func(t *Balances) error { t.A -= 3; t.B += 3; return nil })
		check(err == nil && s.A == 2 && s.B == 8, "commit")
	}

	// Rollback an explicit failure
	{
		s := Balances{A: 5, B: 5}
		err := transact(&s, func(t *Balances) error { t.A = 0; return errors.New("reject") })
		check(err != nil && s.A == 5, "rollback")
	}

	// Reject invalid funds
	{
		s := Balances{A: 5, B: 5}
		err := transact(&s, func(t *Balances) error {
			if t.A < 8 {
				return errors.New("insufficient")
			}
			t.A -= 8
			t.B += 8
			return nil
		})
		check(err != nil && s.A == 5 && s.B == 5, "funds")
	}

	// Preserve total value
	{
		s := Balances{A: 5, B: 5}
		for i := 0; i < 2; i++ {
			check(transact(&s, func(t *Balances) error { t.A--; t.B++; return nil }) == nil, "transfer")
		}
		check(s.A+s.B == 10, "total")
	}

	// Keep a failed retry distinct
	{
		s := Balances{A: 5, B: 5}
		_ = transact(&s, func(t *Balances) error { t.A = 99; return errors.New("fail") })
		check(transact(&s, func(t *Balances) error { t.A--; t.B++; return nil }) == nil && s.A == 4, "retry")
	}

	// Transfer no-op semantics
	{
		s := Balances{A: 5, B: 5}
		err := transact(&s, func(t *Balances) error { return nil })
		check(err == nil && s.A == 5 && s.B == 5, "no-op")
	}
	fmt.Println("All lesson checks passed.")
}
