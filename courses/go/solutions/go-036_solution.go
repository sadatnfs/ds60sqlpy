package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type PodView struct {
	Labels map[string]string
	Ready  bool
}

func matches(labels, selector map[string]string) bool {
	for k, want := range selector {
		got, ok := labels[k]
		if !ok || got != want {
			return false
		}
	}
	return true
}

func main() {
	// Match all required labels
	{
		check(matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"}), "match")
	}

	// Reject a missing label
	{
		check(!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"}), "missing")
	}

	// Distinguish empty value from absence
	{
		check(matches(map[string]string{"flag": ""}, map[string]string{"flag": ""}), "empty present")
		check(!matches(map[string]string{}, map[string]string{"flag": ""}), "empty absent")
	}

	// Filter readiness separately
	{
		pods := []PodView{{Labels: map[string]string{"app": "web"}, Ready: true}, {Labels: map[string]string{"app": "web"}, Ready: false}}
		count := 0
		for _, p := range pods {
			if matches(p.Labels, map[string]string{"app": "web"}) && p.Ready {
				count++
			}
		}
		check(count == 1, "ready backends")
	}

	// Inspect an overly broad selector
	{
		check(matches(map[string]string{"app": "web"}, nil) && matches(map[string]string{"app": "db"}, nil), "broad selector")
	}

	// Transfer rollout-stable identity
	{
		selector := map[string]string{"app": "web"}
		check(matches(map[string]string{"app": "web", "revision": "a"}, selector) && matches(map[string]string{"app": "web", "revision": "b"}, selector), "rollout selector")
	}
	fmt.Println("All lesson checks passed.")
}
