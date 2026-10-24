# go-038: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Optimistic concurrency protects a write from silently overwriting a newer observation. A client reads an object with resourceVersion, prepares a change and submits the version it observed. If another writer changed the object, the API can reject the stale write with a conflict. The correct response is usually to reread current state, recompute the intended change and retry within a budget. Retrying the identical stale object cannot resolve the conflict. Resource versions are opaque tokens, not counters for client arithmetic. Server-side apply and patch operations have additional field-management contracts that should not be confused with unrestricted last-writer-wins replacement.

This fixture represents an object as value plus opaque version. update requires equality with the observed token and returns a new server-selected token. A conflict is a typed outcome distinct from invalid input or access denial. Recompute from the new read rather than blindly replacing fields owned by another controller. Keep retries bounded and preserve context cancellation.

## 1. Accept a current version

Update value 2 using its current token a.

```go
s := Versioned{Value: 2, Version: "a"}
err := versionUpdate(&s, "a", 3, "b")
check(err == nil && s.Value == 3 && s.Version == "b", "current update")
```

**Expected:** The value changes and token becomes b.

The new token is selected by the simulated server. A real client must not construct the next resourceVersion itself.

## 2. Reject a stale version

Attempt a write with old token a against current token b.

```go
s := Versioned{Value: 3, Version: "b"}
err := versionUpdate(&s, "a", 9, "c")
check(errors.Is(err, ErrConflict) && s.Value == 3, "conflict")
```

**Expected:** Conflict is returned and value stays unchanged.

The failed write does not overwrite newer state. The error is useful evidence about the caller assumption.

## 3. Reread before retry

Read the current token after conflict and recompute an increment.

```go
s := Versioned{Value: 4, Version: "b"}
observed := s
check(versionUpdate(&s, observed.Version, observed.Value+1, "c") == nil && s.Value == 5, "reread")
```

**Expected:** The new value is based on current state.

Recomputation preserves the intervening change. Replaying an old absolute value could erase it.

## 4. Keep opaque tokens opaque

Use token rv:opaque rather than an integer.

```go
s := Versioned{Value: 1, Version: "rv:opaque"}
check(versionUpdate(&s, "rv:opaque", 2, "next:opaque") == nil, "opaque")
```

**Expected:** Equality-based update succeeds.

No parsing or arithmetic is needed. Treating tokens as numbers would add an unsupported assumption.

## 5. Retain another field

Change one scalar while keeping a separate owner label.

```go
labels := map[string]string{"owner": "other"}
s := Versioned{Value: 1, Version: "x"}
check(versionUpdate(&s, "x", 2, "y") == nil && labels["owner"] == "other", "field scope")
```

**Expected:** The unrelated label is unchanged.

Real patches and apply operations should be scoped to fields the controller owns. This fixture makes that responsibility explicit without emulating field management.

## 6. Transfer bounded conflict handling

Try the same stale token twice and count conflicts.

```go
s := Versioned{Value: 3, Version: "new"}
conflicts := 0
for i := 0; i < 2; i++ {
	if errors.Is(versionUpdate(&s, "old", 9, "unused"), ErrConflict) {
		conflicts++
	}
}
check(conflicts == 2 && s.Value == 3, "stale retries")
```

**Expected:** Both attempts conflict and neither changes state.

The counterexample explains why automatic retry must reread. More attempts with the same invalid assumption do not create progress.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
