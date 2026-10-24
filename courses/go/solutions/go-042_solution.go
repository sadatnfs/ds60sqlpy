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
		server := Cached{Version: "b"}
		check(cache.Version != server.Version, "stale view")
	}

	// Gate on initial synchronization
	{
		synced := false
		ready := synced
		check(!ready, "initial sync")
	}

	// Queue identities instead of objects
	{
		key := "lesson/demo"
		version := "a"
		version = "b"
		check(key == "lesson/demo" && version == "b", "key identity")
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
