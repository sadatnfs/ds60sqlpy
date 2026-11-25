# go-039: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-039_solution.go` implements all six cases.

## Mechanism

A watch streams changes after a chosen observation point, but it is not an infinite durable event log. A controller normally obtains a list snapshot and continues from its resourceVersion so the initial state and later events connect coherently. Connections end, history can expire, and clients must recover by relisting when the server cannot continue from an old version. Bookmarks can advance the known position without carrying an ordinary object mutation; they are not guaranteed periodic heartbeats. Treat events as prompts to reconcile current state. Never assume every intermediate transition is delivered exactly once or that a disconnected watch proves no changes occurred.

This offline reducer handles ADDED, MODIFIED, DELETED, BOOKMARK and an explicit expired-history signal. Ordinary events update a keyed cache; bookmarks only advance the token. Expiration invalidates continuity and requires a fresh list rather than fabricated incremental recovery. The real API uses Status errors and HTTP responses whose interpretation belongs to client-go or a carefully reviewed client.

## 1. Apply an added object: predict an edited check

Copy worked example 1, change `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})` to `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 3, Version: "a"})` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
s := newWatch()
check(applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"}) == nil && s.Items["demo"] == 2, "add")
```

**Expected:** The edited check panics with `add` even though `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"}) == nil && s.Items["demo"] == 2` still holds.

**Verify:** Restoring `applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})` makes the check pass again with the worked observation: the cache gains demo=2.

The key identifies current state. Reconciliation should inspect that state rather than treat addition as an irreversible once-only command.

## 2. Apply a modification: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 4, Version: "b"})`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
s := newWatch()
_ = applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})
check(applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"}) == nil && s.Items["demo"] == 3, "modify")
```

**Expected:** The defective run panics with `modify`; after restoring `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"})`, the cached value becomes 3.

**Verify:** The edited check fails with message `modify` for a state that `applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"}) == nil && s.Items["demo"] == 3` accepts.

The newest observed value replaces the prior value for this simplified cache. A production informer also manages resource typing and synchronization.

## 3. Advance a bookmark

Apply a bookmark without an object.

```go
s := newWatch()
check(applyWatch(&s, WatchEvent{Kind: "BOOKMARK", Version: "b"}) == nil && s.Version == "b" && len(s.Items) == 0, "bookmark")
```

**Expected:** The version advances and no item is created.

**Verify:** Your solution must keep `applyWatch(&s, WatchEvent{Kind: "BOOKMARK", Version: "b"}) == nil && s.Version == "b" && len(s.Items) == 0` true. Control: changing `applyWatch(&s, WatchEvent{Kind: "BOOKMARK", Version: "b"})` to `applyWatch(&s, WatchEvent{Kind: "BOOKMARK!", Version: "b"})` panics with message `bookmark`; revert it.

A bookmark supplies continuity information, not an object named by an empty key.

## 4. Invalidate expired continuity

Apply an expired-history signal.

```go
s := newWatch()
err := applyWatch(&s, WatchEvent{Kind: "EXPIRED"})
check(err != nil && s.NeedsList, "expiry")
```

**Expected:** The state requests a relist.

**Verify:** Your solution must keep `err != nil && s.NeedsList` true. Control: changing `err := applyWatch(&s, WatchEvent{Kind: "EXPIRED"})` to `err := applyWatch(&s, WatchEvent{Kind: "EXPIRED!"})` panics with message `expiry`; revert it.

Continuing from an unavailable position can miss state changes. A fresh list reestablishes the baseline.

## 5. Delete current membership

Delete an existing key and then delete it again.

```go
s := newWatch()
s.Items["demo"] = 2
_ = applyWatch(&s, WatchEvent{Kind: "DELETED", Key: "demo", Version: "c"})
_ = applyWatch(&s, WatchEvent{Kind: "DELETED", Key: "demo", Version: "d"})
check(len(s.Items) == 0, "delete")
```

**Expected:** The cache remains empty.

**Verify:** Your solution must keep `len(s.Items) == 0` true. Control: changing `s.Items["demo"] = 2` to `s.Items["demo!"] = 2` panics with message `delete`; revert it.

Idempotent removal tolerates repeated signals. Real cleanup still requires exact UID ownership before external deletion.

## 6. Transfer unknown-event refusal

Apply an unsupported event kind.

```go
s := newWatch()
check(applyWatch(&s, WatchEvent{Kind: "MYSTERY"}) != nil, "unknown")
```

**Expected:** An error is returned without accepting invented semantics.

**Verify:** Your solution must keep `applyWatch(&s, WatchEvent{Kind: "MYSTERY"}) != nil` true. Control: changing `check(applyWatch(&s, WatchEvent{Kind: "MYSTERY"}) != nil, "unknown")` to `check(applyWatch(&s, WatchEvent{Kind: "MYSTERY"}) == nil, "unknown")` panics with message `unknown`; revert it.

Unknown protocol data should not silently mutate the cache. Preserve diagnostic evidence and recover under an explicit policy.

## Transfer after comparison

Informers in the next lessons run this list-then-watch loop for you, including the relist on expiry. Knowing the model tells you what to expect: after a relist, handlers may see updates for objects that did not change, and some deletions arrive only as missing items. Write handlers that converge from current state rather than counting events.
