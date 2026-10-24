package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log/slog"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

func logRecord(message string, args ...any) map[string]any {
	var b bytes.Buffer
	handler := slog.NewJSONHandler(&b, &slog.HandlerOptions{ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
		if a.Key == slog.TimeKey {
			return slog.Attr{}
		}
		return a
	}})
	slog.New(handler).Info(message, args...)
	var value map[string]any
	if err := json.Unmarshal(b.Bytes(), &value); err != nil {
		panic(err)
	}
	return value
}

func main() {
	// Emit a structured event
	{
		v := logRecord("processed", "count", 3)
		check(v["msg"] == "processed" && v["count"] == float64(3), "fields")
	}

	// Retain correlation
	{
		v := logRecord("read", "request_id", "lesson-7")
		check(v["request_id"] == "lesson-7", "correlation")
	}

	// Control variable time
	{
		v := logRecord("stable")
		_, present := v["time"]
		check(!present, "time")
	}

	// Keep status structured
	{
		v := logRecord("read finished", "status", "failed")
		check(v["status"] == "failed", "status")
	}

	// Redact before logging
	{
		v := logRecord("configuration", "credential", "[redacted]")
		check(v["credential"] == "[redacted]", "redaction")
	}

	// Transfer numeric evidence
	{
		v := logRecord("read", "bytes", 12)
		check(v["bytes"] == float64(12), "numeric")
	}
	fmt.Println("All lesson checks passed.")
}
