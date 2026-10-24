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

type WatchEvent struct {
	Kind, Key, Version string
	Value              int
}
type WatchState struct {
	Items     map[string]int
	Version   string
	NeedsList bool
}

func newWatch() WatchState { return WatchState{Items: map[string]int{}} }
func applyWatch(s *WatchState, e WatchEvent) error {
	switch e.Kind {
	case "ADDED", "MODIFIED":
		s.Items[e.Key] = e.Value
	case "DELETED":
		delete(s.Items, e.Key)
	case "BOOKMARK":
	case "EXPIRED":
		s.NeedsList = true
		return errors.New("relist required")
	default:
		return errors.New("unknown event")
	}
	s.Version = e.Version
	return nil
}

func main() {
	// Apply an added object
	{
		s := newWatch()
		check(applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"}) == nil && s.Items["demo"] == 2, "add")
	}

	// Apply a modification
	{
		s := newWatch()
		_ = applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})
		check(applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"}) == nil && s.Items["demo"] == 3, "modify")
	}

	// Advance a bookmark
	{
		s := newWatch()
		check(applyWatch(&s, WatchEvent{Kind: "BOOKMARK", Version: "b"}) == nil && s.Version == "b" && len(s.Items) == 0, "bookmark")
	}

	// Invalidate expired continuity
	{
		s := newWatch()
		err := applyWatch(&s, WatchEvent{Kind: "EXPIRED"})
		check(err != nil && s.NeedsList, "expiry")
	}

	// Delete current membership
	{
		s := newWatch()
		s.Items["demo"] = 2
		_ = applyWatch(&s, WatchEvent{Kind: "DELETED", Key: "demo", Version: "c"})
		_ = applyWatch(&s, WatchEvent{Kind: "DELETED", Key: "demo", Version: "d"})
		check(len(s.Items) == 0, "delete")
	}

	// Transfer unknown-event refusal
	{
		s := newWatch()
		check(applyWatch(&s, WatchEvent{Kind: "MYSTERY"}) != nil, "unknown")
	}
	fmt.Println("All lesson checks passed.")
}
