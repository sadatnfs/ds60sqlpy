package main

import (
	"fmt"
)

func check(ok bool, message string) {
	if !ok {
		panic(message)
	}
}

type Cached struct {
	Labels  map[string]string
	Version string
}

func copyCached(v Cached) Cached {
	out := v
	out.Labels = map[string]string{}
	for k, value := range v.Labels {
		out.Labels[k] = value
	}
	return out
}

func main() {
	// Copy before changing labels
	{
		cached := Cached{Labels: map[string]string{"app": "web"}, Version: "a"}
		copy := copyCached(cached)
		copy.Labels["app"] = "api"
		check(cached.Labels["app"] == "web" && copy.Labels["app"] == "api", "copy")
	}

	// Expose a shallow-copy defect safely
	{
		cached := Cached{Labels: map[string]string{"app": "web"}}
		shallow := cached
		shallow.Labels["app"] = "bad"
		check(cached.Labels["app"] == "bad", "shallow counterexample")
	}

	// Represent a stale view
	{
		cache := Cached{Version: "a"}
		events := []Cached{{Version: "b"}, {Version: "c"}}
		delivered := 1
		for _, event := range events[:delivered] {
			cache = event
		}
		check(cache.Version == "b" && events[len(events)-1].Version == "c", "stale view")
	}

	// Gate on initial synchronization
	{
		processed := 0
		process := func(synced bool) bool {
			if !synced {
				return false
			}
			processed++
			return true
		}
		check(!process(false) && processed == 0, "initial sync")
		check(process(true) && processed == 1, "after sync")
	}

	// Queue identities instead of objects
	{
		store := map[string]Cached{"lesson/demo": {Version: "a"}}
		queue := []string{"lesson/demo"}
		store["lesson/demo"] = Cached{Version: "b"}
		check(store[queue[0]].Version == "b", "key identity")
	}

	// Transfer nested-copy independence
	{
		cached := Cached{Labels: map[string]string{"app": "web"}}
		copy := copyCached(cached)
		copy.Labels["tier"] = "frontend"
		check(len(cached.Labels) == 1 && len(copy.Labels) == 2, "nested copy")
	}
	fmt.Println("All lesson checks passed.")
}
