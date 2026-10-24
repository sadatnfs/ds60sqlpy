package main

import (
	"errors"
	"fmt"
	"strconv"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

var ErrMissing = errors.New("missing record")
var ErrDenied = errors.New("access denied")

type LimitError struct{ Max int }

func (e *LimitError) Error() string { return fmt.Sprintf("limit %d", e.Max) }

func main() {
	// Preserve a cause
	{
		err := fmt.Errorf("read record: %w", ErrMissing)
		check(errors.Is(err, ErrMissing), "wrapped cause")
	}

	// Reject text equality
	{
		a := errors.New("missing")
		b := errors.New("missing")
		check(!errors.Is(a, b), "identity not text")
	}

	// Inspect a typed boundary
	{
		err := fmt.Errorf("request: %w", &LimitError{Max: 3})
		var limit *LimitError
		check(errors.As(err, &limit) && limit.Max == 3, "typed error")
	}

	// Handle successful parsing
	{
		v, err := strconv.Atoi("42")
		check(err == nil && v == 42, "valid parse")
	}

	// Classify invalid parsing
	{
		_, err := strconv.Atoi("4x")
		var number *strconv.NumError
		check(errors.As(err, &number), "parse error")
	}

	// Transfer joined failures
	{
		err := errors.Join(ErrMissing, ErrDenied)
		check(errors.Is(err, ErrMissing) && errors.Is(err, ErrDenied), "joined errors")
	}
	fmt.Println("All lesson checks passed.")
}
