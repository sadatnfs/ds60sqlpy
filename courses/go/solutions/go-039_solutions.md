# go-039: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A watch streams changes after a chosen observation point, but it is not an infinite durable event log. A controller normally obtains a list snapshot and continues from its resourceVersion so the initial state and later events connect coherently. Connections end, history can expire, and clients must recover by relisting when the server cannot continue from an old version. Bookmarks can advance the known position without carrying an ordinary object mutation; they are not guaranteed periodic heartbeats. Treat events as prompts to reconcile current state. Never assume every intermediate transition is delivered exactly once or that a disconnected watch proves no changes occurred.

This offline reducer handles ADDED, MODIFIED, DELETED, BOOKMARK and an explicit expired-history signal. Ordinary events update a keyed cache; bookmarks only advance the token. Expiration invalidates continuity and requires a fresh list rather than fabricated incremental recovery. The real API uses Status errors and HTTP responses whose interpretation belongs to client-go or a carefully reviewed client.

## 1. Apply an added object

Apply ADDED for demo with value 2.

```go
s := newWatch()
check(applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"}) == nil && s.Items["demo"] == 2, "add")
```

**Expected:** The cache gains demo=2.

The key identifies current state. Reconciliation should inspect that state rather than treat addition as an irreversible once-only command.

## 2. Apply a modification

Add then modify the same key.

```go
s := newWatch()
_ = applyWatch(&s, WatchEvent{Kind: "ADDED", Key: "demo", Value: 2, Version: "a"})
check(applyWatch(&s, WatchEvent{Kind: "MODIFIED", Key: "demo", Value: 3, Version: "b"}) == nil && s.Items["demo"] == 3, "modify")
```

**Expected:** The cached value becomes 3.

The newest observed value replaces the prior value for this simplified cache. A production informer also manages resource typing and synchronization.

## 3. Advance a bookmark

Apply a bookmark without an object.

```go
s := newWatch()
check(applyWatch(&s, WatchEvent{Kind: "BOOKMARK", Version: "b"}) == nil && s.Version == "b" && len(s.Items) == 0, "bookmark")
```

**Expected:** The version advances and no item is created.

A bookmark supplies continuity information, not an object named by an empty key.

## 4. Invalidate expired continuity

Apply an expired-history signal.

```go
s := newWatch()
err := applyWatch(&s, WatchEvent{Kind: "EXPIRED"})
check(err != nil && s.NeedsList, "expiry")
```

**Expected:** The state requests a relist.

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

Idempotent removal tolerates repeated signals. Real cleanup still requires exact UID ownership before external deletion.

## 6. Transfer unknown-event refusal

Apply an unsupported event kind.

```go
s := newWatch()
check(applyWatch(&s, WatchEvent{Kind: "MYSTERY"}) != nil, "unknown")
```

**Expected:** An error is returned without accepting invented semantics.

Unknown protocol data should not silently mutate the cache. Preserve diagnostic evidence and recover under an explicit policy.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
