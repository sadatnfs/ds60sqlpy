# go-042: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

An informer maintains a local view of API objects and supplies events that can enqueue reconciliation. Its cache improves efficiency but is eventually consistent: a successful write may not be visible in the cache immediately. Wait for initial cache synchronization before relying on its contents. Objects returned from shared caches must be treated as read-only. Mutating them in place can corrupt observations for other consumers without making any API change. DeepCopy before constructing an update, and use the API response or a fresh read when a particular consistency requirement demands it. A cache miss is evidence about that view, not always proof of server-side absence.

An informer factory starts shared controllers; WaitForCacheSync confirms initial synchronization or cancellation. Listers read cached objects. The fixture models a cache map and a defensive copy of nested labels. Copying only the outer struct still aliases its map. Event handlers should enqueue keys quickly instead of blocking on long reconciliation or retaining stale object pointers as authoritative state.

## 1. Copy before changing labels

Copy a cached object and change its app label.

```go
cached := Cached{Labels: map[string]string{"app": "web"}, Version: "a"}
copy := copyCached(cached)
copy.Labels["app"] = "api"
check(cached.Labels["app"] == "web" && copy.Labels["app"] == "api", "copy")
```

**Expected:** The cache still contains the original label.

The copy duplicates the map as well as the struct. An outer assignment alone would still share mutable labels.

## 2. Expose a shallow-copy defect safely

Assign a struct containing a map and mutate the assigned map sequentially.

```go
cached := Cached{Labels: map[string]string{"app": "web"}}
shallow := cached
shallow.Labels["app"] = "bad"
check(cached.Labels["app"] == "bad", "shallow counterexample")
```

**Expected:** The original observes the unintended change.

This is a deterministic sequential demonstration of aliasing. The real cache rule forbids such mutation, especially across concurrent consumers.

## 3. Represent a stale view

Keep cache version a while a server model has version b.

```go
cache := Cached{Version: "a"}
server := Cached{Version: "b"}
check(cache.Version != server.Version, "stale view")
```

**Expected:** The versions differ without implying a failed write.

A lagging cache and a successful server update can coexist. Immediate reread from the same cache is not a strong write-confirmation test.

## 4. Gate on initial synchronization

Inspect a false cache-synced flag before processing.

```go
synced := false
ready := synced
check(!ready, "initial sync")
```

**Expected:** The worker does not claim readiness.

A started goroutine is not evidence that its initial list has completed. Production code waits on the actual synchronization function.

## 5. Queue identities instead of objects

Store a namespace/name key derived from a snapshot.

```go
key := "lesson/demo"
version := "a"
version = "b"
check(key == "lesson/demo" && version == "b", "key identity")
```

**Expected:** The key remains usable after the object value changes.

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

Separate nested storage matters for insertion and deletion as well as replacement of an existing value.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
