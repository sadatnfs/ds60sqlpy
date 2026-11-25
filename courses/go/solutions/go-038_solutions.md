# go-038: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-038_solution.go` implements all six cases.

## Mechanism

Optimistic concurrency protects a write from silently overwriting a newer observation. A client reads an object with resourceVersion, prepares a change and submits the version it observed. If another writer changed the object, the API can reject the stale write with a conflict. The correct response is usually to reread current state, recompute the intended change and retry within a budget. Retrying the identical stale object cannot resolve the conflict. Resource versions are opaque tokens, not counters for client arithmetic. Server-side apply and patch operations have additional field-management contracts that should not be confused with unrestricted last-writer-wins replacement.

This fixture represents an object as value plus opaque version. update requires equality with the observed token and returns a new server-selected token. A conflict is a typed outcome distinct from invalid input or access denial. Recompute from the new read rather than blindly replacing fields owned by another controller. Keep retries bounded and preserve context cancellation.

## 1. Accept a current version: change one input

Copy worked example 1, change `err := versionUpdate(&s, "a", 3, "b")` to `err := versionUpdate(&s, "a", 4, "b")` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
s := Versioned{Value: 2, Version: "a"}
err := versionUpdate(&s, "a", 3, "b")
check(err == nil && s.Value == 3 && s.Version == "b", "current update")
```

**Expected:** The edited run panics with `current update` because `err == nil && s.Value == 3 && s.Version == "b"` no longer holds.

**Verify:** Restoring `err := versionUpdate(&s, "a", 3, "b")` makes the check pass again with the worked observation: the value changes and token becomes b.

The new token is selected by the simulated server. A real client must not construct the next resourceVersion itself.

## 2. Reject a stale version: debug a regression

A one-token regression in worked example 2 makes a line read `s := Versioned{Value: 4, Version: "b"}`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
s := Versioned{Value: 3, Version: "b"}
err := versionUpdate(&s, "a", 9, "c")
check(errors.Is(err, ErrConflict) && s.Value == 3, "conflict")
```

**Expected:** The defective run panics with `conflict`; after restoring `s := Versioned{Value: 3, Version: "b"}`, conflict is returned and value stays unchanged.

**Verify:** The failing run shows message `conflict`; after the repair `errors.Is(err, ErrConflict) && s.Value == 3` holds again.

The failed write does not overwrite newer state. The error is useful evidence about the caller assumption.

## 3. Reread before retry

Read the current token after conflict and recompute an increment.

```go
s := Versioned{Value: 4, Version: "b"}
observed := s
check(versionUpdate(&s, observed.Version, observed.Value+1, "c") == nil && s.Value == 5, "reread")
```

**Expected:** The new value is based on current state.

**Verify:** Your solution must keep `versionUpdate(&s, observed.Version, observed.Value+1, "c") == nil && s.Value == 5` true. Control: changing `check(versionUpdate(&s, observed.Version, observed.Value+1, "c") == nil && s.Value == 5, "reread")` to `check(versionUpdate(&s, observed.Version, observed.Value-1, "c") == nil && s.Value == 5, "reread")` panics with message `reread`; revert it.

Recomputation preserves the intervening change. Replaying an old absolute value could erase it.

## 4. Keep opaque tokens opaque

Use token rv:opaque rather than an integer.

```go
s := Versioned{Value: 1, Version: "rv:opaque"}
check(versionUpdate(&s, "rv:opaque", 2, "next:opaque") == nil, "opaque")
```

**Expected:** Equality-based update succeeds.

**Verify:** Your solution must keep `versionUpdate(&s, "rv:opaque", 2, "next:opaque") == nil` true. Control: changing `s := Versioned{Value: 1, Version: "rv:opaque"}` to `s := Versioned{Value: 1, Version: "rv:opaque!"}` panics with message `opaque`; revert it.

No parsing or arithmetic is needed. Treating tokens as numbers would add an unsupported assumption.

## 5. Retain another field

Update the value of an object that also carries an owner label, using its current token.

```go
s := Versioned{Value: 1, Version: "x", Labels: map[string]string{"owner": "other"}}
check(versionUpdate(&s, "x", 2, "y") == nil && s.Value == 2 && s.Version == "y" && s.Labels["owner"] == "other", "field scope")
```

**Expected:** The value and token change while the owner label is unchanged.

**Verify:** Your solution must keep `versionUpdate(&s, "x", 2, "y") == nil && s.Value == 2 && s.Version == "y" && s.Labels["owner"] == "other"` true. Control: changing `versionUpdate(&s, "x", 2, "y")` to `versionUpdate(&s, "x", 3, "y")` panics with message `field scope`; revert it.

Real patches and apply operations should be scoped to fields the controller owns. Here the label lives in the updated object itself, so the check shows that versionUpdate wrote only the fields it is responsible for.

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

**Verify:** Your solution must keep `conflicts == 2 && s.Value == 3` true. Control: changing `for i := 0; i < 2; i++ {` to `for i := 0; i <= 2; i++ {` panics with message `stale retries`; revert it.

The counterexample explains why automatic retry must reread. More attempts with the same invalid assumption do not create progress.

## Transfer after comparison

client-go's retry.RetryOnConflict wraps exactly this loop for Kubernetes updates: get the latest object, apply your change, update, and retry only on a conflict error. Server-side apply narrows the problem further by tracking field ownership. Use the same shape for any store with ETags or row versions, such as an HTTP API that honors If-Match.
