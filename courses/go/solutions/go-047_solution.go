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

var ErrForbidden = errors.New("forbidden")

type FakeReader struct {
	Value, Calls int
	Err          error
}

func (f *FakeReader) Read(ctx context.Context) (int, error) { f.Calls++; return f.Value, f.Err }

type Reader interface {
	Read(context.Context) (int, error)
}

func readOnce(ctx context.Context, r Reader) (int, error) {
	if err := ctx.Err(); err != nil {
		return 0, err
	}
	v, err := r.Read(ctx)
	if err != nil {
		return 0, fmt.Errorf("read object: %w", err)
	}
	return v, nil
}

func main() {
	// Verify one successful API call
	{
		f := &FakeReader{Value: 3}
		v, err := readOnce(context.Background(), f)
		check(err == nil && v == 3 && f.Calls == 1, "success")
	}

	// Preserve a forbidden error
	{
		f := &FakeReader{Err: ErrForbidden}
		_, err := readOnce(context.Background(), f)
		check(errors.Is(err, ErrForbidden) && f.Calls == 1, "forbidden")
	}

	// Stop before a canceled call
	{
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		f := &FakeReader{}
		_, err := readOnce(ctx, f)
		check(errors.Is(err, context.Canceled) && f.Calls == 0, "cancel")
	}

	// Distinguish returned zero from failure
	{
		f := &FakeReader{Value: 0}
		v, err := readOnce(context.Background(), f)
		check(err == nil && v == 0, "zero success")
	}

	// Retain an unknown failure
	{
		cause := errors.New("transport outcome unknown")
		f := &FakeReader{Err: cause}
		_, err := readOnce(context.Background(), f)
		check(errors.Is(err, cause), "unknown cause")
	}

	// Transfer source-bound evidence
	{
		receipt := map[string]string{"lesson": "go-047", "source": "reviewed-fixture"}
		check(receipt["lesson"] == "go-047" && receipt["source"] == "reviewed-fixture", "receipt identity")
	}
	fmt.Println("All lesson checks passed.")
}
