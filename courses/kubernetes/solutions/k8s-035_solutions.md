# k8s-035: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A read-modify-write operation can lose another client's change if it assumes the object stayed unchanged after reading. Kubernetes uses resourceVersion for optimistic concurrency. The client submits a conditional update based on the version it read; if the stored object changed, the server can reject the stale update with 409 Conflict. The correct recovery is to read current state and recompute the intended change, not repeatedly force the old snapshot over newer state.

resourceVersion is an opaque token supplied by the server. Treat it as a string for the API contract. Do not increment it, subtract two versions to estimate elapsed time or use it as a user-defined clock. UID identifies an object lifetime, while resourceVersion identifies a state version within API semantics. Recreating the same name can change UID and invalidate an operation's ownership assumptions.

A watch streams changes after a starting point, reducing repeated full-list work. It can disconnect, deliver repeated information or expire beyond the server's retained history. A robust observer rebuilds a current snapshot when required and reconciles from that state. The normal course credential does not offer arbitrary watch/update operations; this is a host-scoped advanced activity with an offline trace model.

## Exercise 1: Separate name, UID and version

The distinctions prevent accidental updates after replacement and incorrect arithmetic on server tokens. A human-friendly name is useful navigation, but it is not enough for a destructive or ownership-sensitive operation.

**Expected:** Name addresses an object; UID its lifetime; resourceVersion is an opaque API token.

**Solution reasoning**

- **Approach:** State what happens to hello-config, u1 and rv-A when the object is deleted and recreated.
- **Why it is correct:** The name is reused, a new UID is assigned and resourceVersion is an opaque token that changes on every write.
- **Plausible wrong approach:** Comparing resourceVersion values as numbers to decide which is newer relies on a format the API does not promise.
- **How to verify:** Name stays, UID changes and resourceVersion changes.

## Exercise 2: Predict the conflict

Optimistic concurrency detects that the read premise became stale. The rejection protects the newer state, but the client still has to handle it explicitly rather than treating conflict as an unexplained generic failure.

**Expected:** 409-style conflict with current data unchanged.

**Solution reasoning**

- **Approach:** Send an update carrying rv-A against stored rv-B and read the object afterward.
- **Why it is correct:** An update with a stale resourceVersion fails with 409 Conflict and does not modify the stored object.
- **Plausible wrong approach:** Retrying the same request blindly repeats the conflict because rv-A is still stale.
- **How to verify:** The stored object still shows rv-B and its original data.

## Exercise 3: Recompute after reread

A correct retry is a fresh decision based on current state. The desired change may no longer be necessary or appropriate. Bounded retries and cancellation make contention visible instead of hiding an endless loop.

**Expected:** A new conditional request uses current state and a bounded retry count.

**Solution reasoning**

- **Approach:** Reread at rv-B, reapply only the message edit and send it with a retry limit.
- **Why it is correct:** The new request carries the current version and the fields another writer changed, so the update does not undo their work.
- **Plausible wrong approach:** Removing resourceVersion to force the write overwrites whatever changed since rv-A.
- **How to verify:** The request carries rv-B, preserves unrelated fields and has a retry cap.

## Exercise 4: Stop on replacement identity

The new object may belong to another actor or a later operation. Updating it solely because the name matches violates the original operation scope, even if its content looks familiar.

**Expected:** Refuse the mutation across object replacement.

**Solution reasoning**

- **Approach:** Compare the reread UID u2 with the recorded u1 before writing.
- **Why it is correct:** A different UID means the object was replaced, so the lease's expectations no longer apply.
- **Plausible wrong approach:** Writing because the name still matches would modify an object the lease never covered.
- **How to verify:** UIDs differ, and the mutation is refused.

## Exercise 5: Recover from watch expiration

The server no longer promises the requested historical stream. Rebuilding from current state is compatible with level-driven reconciliation and avoids fabricating a sequence that may never have happened.

**Expected:** Current u2 snapshot retained; watcher restarts from the new list token.

**Solution reasoning**

- **Approach:** After 410 Gone, replace the cache with the fresh list and resume watching from its resourceVersion.
- **Why it is correct:** An expired resourceVersion cannot be resumed, so a new list is the only consistent starting point.
- **Plausible wrong approach:** Restarting the watch from the old version returns 410 again and never recovers.
- **How to verify:** The cache holds the u2 snapshot, and the watch starts from the list token.

## Exercise 6: Handle bookmarks and duplicates

The observer should separate stream progress from application objects and make side effects idempotent. A watch reconnect is expected operational behavior, not evidence that each event must trigger another create or external call.

**Expected:** Bookmark advances progress; duplicate state does not repeat external effects.

**Solution reasoning**

- **Approach:** Treat the bookmark as progress only and dedupe the repeated MODIFIED event by resourceVersion.
- **Why it is correct:** A bookmark carries a version with no object change, and a duplicate event describes state already handled.
- **Plausible wrong approach:** Calling the external service for each MODIFIED event repeats side effects on redelivery.
- **How to verify:** The bookmark updates progress, and the duplicate causes no second effect.

## Boundary and troubleshooting review

A conditional replace, a patch with appropriate preconditions and server-side apply have different merge/ownership semantics. This lesson models compare-and-swap on a tiny object; it does not teach that every PATCH automatically prevents lost updates. Specify the actual API operation and precondition when reviewing a live client.

A supplied 409 or 410 trace is a deterministic teaching fixture. A live receipt must include the exact owned identity, request outcome and bounded recovery observation without exposing credentials. Do not enable broad watch or write permissions merely to make a reading exercise runnable in the normal module pad.
