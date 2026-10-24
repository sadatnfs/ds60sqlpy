package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net/http"
	"strings"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(r *http.Request) (*http.Response, error) { return f(r) }
func fetch(ctx context.Context, status int, body string, limit int64) (string, error) {
	client := &http.Client{Transport: roundTripFunc(func(r *http.Request) (*http.Response, error) {
		if err := r.Context().Err(); err != nil {
			return nil, err
		}
		return &http.Response{StatusCode: status, Header: make(http.Header), Body: io.NopCloser(strings.NewReader(body)), Request: r}, nil
	})}
	req, err := http.NewRequestWithContext(ctx, "GET", "http://lesson.invalid/resource", nil)
	if err != nil {
		return "", err
	}
	response, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer response.Body.Close()
	if response.StatusCode != 200 {
		return "", fmt.Errorf("status %d", response.StatusCode)
	}
	data, err := io.ReadAll(io.LimitReader(response.Body, limit+1))
	if err != nil {
		return "", err
	}
	if int64(len(data)) > limit {
		return "", errors.New("response too large")
	}
	return string(data), nil
}

func main() {
	// Read a successful response
	{
		v, err := fetch(context.Background(), 200, "ready", 8)
		check(err == nil && v == "ready", "client success")
	}

	// Reject an HTTP failure status
	{
		_, err := fetch(context.Background(), 404, "missing", 8)
		check(err != nil, "HTTP status")
	}

	// Detect an oversized body
	{
		_, err := fetch(context.Background(), 200, "abcde", 4)
		check(err != nil, "body limit")
	}

	// Honor cancellation
	{
		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		_, err := fetch(ctx, 200, "ready", 8)
		check(errors.Is(err, context.Canceled), "cancellation")
	}

	// Allow exact size
	{
		v, err := fetch(context.Background(), 200, "abcd", 4)
		check(err == nil && v == "abcd", "exact size")
	}

	// Transfer an empty body
	{
		v, err := fetch(context.Background(), 200, "", 4)
		check(err == nil && v == "", "empty response")
	}
	fmt.Println("All lesson checks passed.")
}
