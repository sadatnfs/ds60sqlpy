# go-042: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-042_solution.go` implements all six cases.

## Mechanism

An informer maintains a local view of API objects and supplies events that can enqueue reconciliation. Its cache improves efficiency but is eventually consistent: a successful write may not be visible in the cache immediately. Wait for initial cache synchronization before relying on its contents. Objects returned from shared caches must be treated as read-only. Mutating them in place can corrupt observations for other consumers without making any API change. DeepCopy before constructing an update, and use the API response or a fresh read when a particular consistency requirement demands it. A cache miss is evidence about that view, not always proof of server-side absence.

An informer factory starts shared controllers; WaitForCacheSync confirms initial synchronization or cancellation. Listers read cached objects. The fixture models a cache map and a defensive copy of nested labels. Copying only the outer struct still aliases its map. Event handlers should enqueue keys quickly instead of blocking on long reconciliation or retaining stale object pointers as authoritative state.

## 1. Copy before changing labels: change one input

Copy worked example 1, change `cached := Cached{Labels: map[string]string{"app": "web"}, Version: "a"}` to `cached := Cached{Labels: map[string]string{"app!": "web"}, Version: "a"}` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
cached := Cached{Labels: map[string]string{"app": "web"}, Version: "a"}
copy := copyCached(cached)
copy.Labels["app"] = "api"
check(cached.Labels["app"] == "web" && copy.Labels["app"] == "api", "copy")
```

**Expected:** The edited run panics with `copy` because `cached.Labels["app"] == "web" && copy.Labels["app"] == "api"` no longer holds.

**Verify:** Restoring `cached := Cached{Labels: map[string]string{"app": "web"}, Version: "a"}` makes the check pass again with the worked observation: the cache still contains the original label.

The copy duplicates the map as well as the struct. An outer assignment alone would still share mutable labels.

## 2. Expose a shallow-copy defect safely: debug a regression

A one-token regression in worked example 2 makes a line read `shallow.Labels["app!"] = "bad"`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
cached := Cached{Labels: map[string]string{"app": "web"}}
shallow := cached
shallow.Labels["app"] = "bad"
check(cached.Labels["app"] == "bad", "shallow counterexample")
```

**Expected:** The defective run panics with `shallow counterexample`; after restoring `shallow.Labels["app"] = "bad"`, the original observes the unintended change.

**Verify:** The failing run shows message `shallow counterexample`; after the repair `cached.Labels["app"] == "bad"` holds again.

This is a deterministic sequential demonstration of aliasing. The real cache rule forbids such mutation, especially across concurrent consumers.

## 3. Represent a stale view

Deliver only the first of two watch events to a cache that starts at version a.

```go
cache := Cached{Version: "a"}
events := []Cached{{Version: "b"}, {Version: "c"}}
delivered := 1
for _, event := range events[:delivered] {
	cache = event
}
check(cache.Version == "b" && events[len(events)-1].Version == "c", "stale view")
```

**Expected:** The cache shows b while the server's latest version is already c.

**Verify:** Your solution must keep `cache.Version == "b" && events[len(events)-1].Version == "c"` true. Control: changing `delivered := 1` to `delivered := 2` panics with message `stale view`; revert it.

A lagging cache and a successful server update can coexist. Immediate reread from the same cache is not a strong write-confirmation test.

## 4. Gate on initial synchronization

Offer one item to a processor before and after the cache reports synced.

```go
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
```

**Expected:** No item is processed before the cache reports synced; one item is processed afterward.

**Verify:** Your solution must keep `process(true) && processed == 1` true. Control: changing `return true` to `return false` panics with message `after sync`; revert it.

A started goroutine is not evidence that its initial list has completed. Production code waits on the actual synchronization function.

## 5. Queue identities instead of objects

Queue the key of a cached object, then let the store receive a newer version before the key is processed.

```go
store := map[string]Cached{"lesson/demo": {Version: "a"}}
queue := []string{"lesson/demo"}
store["lesson/demo"] = Cached{Version: "b"}
check(store[queue[0]].Version == "b", "key identity")
```

**Expected:** The queued key reads the latest object, version b, not the snapshot taken when it was queued.

**Verify:** Your solution must keep `store[queue[0]].Version == "b"` true. Control: changing `queue := []string{"lesson/demo"}` to `queue := []string{"lesson/demo!"}` panics with message `key identity`; revert it.

The next reconciliation obtains current state for the key. Retaining an event object as permanent truth would preserve stale assumptions.

## 6. Transfer nested-copy independence

Add a new label to a copied object.

```go
cached := Cached{Labels: map[string]string{"app": "web"}}
copy := copyCached(cached)
copy.Labels["tier"] = "frontend"
check(len(cached.Labels) == 1 && len(copy.Labels) == 2, "nested copy")
```

**Expected:** The original label count is unchanged.

**Verify:** Your solution must keep `len(cached.Labels) == 1 && len(copy.Labels) == 2` true. Control: changing `check(len(cached.Labels) == 1 && len(copy.Labels) == 2, "nested copy")` to `check(len(cached.Labels) != 1 && len(copy.Labels) == 2, "nested copy")` panics with message `nested copy`; revert it.

Separate nested storage matters for insertion and deletion as well as replacement of an existing value.

## Transfer after comparison

In client-go, listers return pointers into the shared informer cache, and generated types provide DeepCopy for exactly this reason. Read from the lister, copy, change, then write through the client. Expect the cache to lag your own writes, and let the next reconcile, triggered by the watch event, observe the result instead of polling the cache.
