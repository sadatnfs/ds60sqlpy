# go-043: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Deletion can require coordination with an external resource whose lifetime is not handled by Kubernetes garbage collection. A finalizer records that cleanup must complete before the API object is removed. Once deletionTimestamp is set, the controller performs its owned cleanup and removes only its own finalizer after success. Removing the finalizer first can orphan the external resource; retaining it forever can leave an object stuck terminating. Cleanup must be idempotent and identify the exact owned incarnation, not merely a reusable name. Owner references support Kubernetes garbage collection, but they are not a general substitute for finalizing resources outside the cluster.

A finalizer is a qualified string in metadata.finalizers. The state machine first ensures the finalizer exists during normal operation, then observes deletion, performs bounded cleanup and removes its own entry. Preserve other controllers' entries. An already absent external resource can count as successful cleanup only when the ownership check and absence observation are reliable. Never remove unrelated finalizers as a generic repair shortcut.

## 1. Register cleanup responsibility: predict an edited check

Copy worked example 1 into a scratch pad and change `check(finalAction(false, false, false, true) == "add-finalizer", "register")` to `check(finalAction(true, false, false, true) == "add-finalizer", "register")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.

The unchanged code is worked example 1:

```go
check(finalAction(false, false, false, true) == "add-finalizer", "register")
```

**Expected:** The changed run panics with `register` because the edited check no longer holds. Restoring the original line brings back the worked observation: the next action is add-finalizer.

Register responsibility before creating an external resource that would otherwise be orphaned during deletion.

**Approach.** Evaluate the edited call `finalAction(true, false, false, true)` in branch order: the object is owned, it is deleting, and it has no finalizer, so the result is `done`.

**Why it holds here.** Registration happens only while the object is not deleting. With deletion already started and no finalizer to wait for, the function returns `done`, and the check expecting `add-finalizer` panics with `register`.

**A plausible wrong approach.** Predicting `add-finalizer` because the finalizer is missing. A Kubernetes API server refuses to add new finalizers to an object that is already being deleted, so the controller must register before deletion begins.

**Verify.** Print `finalAction(true, false, false, true)` and `finalAction(false, false, false, true)` and see `done add-finalizer`.

## 2. Retain a healthy object: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(finalAction(true, true, false, true) == "reconcile", "normal")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
check(finalAction(false, true, false, true) == "reconcile", "normal")
```

**Expected:** Before the repair the program panics with `normal`; after it the line reads `check(finalAction(false, true, false, true) == "reconcile", "normal")` again and the action is reconcile.

A finalizer does not itself request deletion. Normal desired-state work continues while deletion has not begun.

**Approach.** Evaluate the edited call `finalAction(true, true, false, true)`: owned, deleting, finalizer present and cleanup not done, so the result is `cleanup`.

**Why it holds here.** The deleting flag is tested before ordinary reconciliation, so a deleting object never returns `reconcile`. The edited check therefore panics with `normal`, while the original non-deleting call returns `reconcile`.

**A plausible wrong approach.** Expecting `reconcile` because the finalizer is present and the object is owned, as if the finalizer itself meant normal operation. Once deletion starts, the finalizer is a gate for cleanup, not a sign of health.

**Verify.** Print `finalAction(false, true, false, true)` and `finalAction(true, true, false, true)` and see `reconcile cleanup`.

## 3. Clean before releasing deletion

Inspect a deleting object with outstanding owned cleanup.

```go
check(finalAction(true, true, false, true) == "cleanup", "cleanup")
```

**Expected:** The action is cleanup.

Removing the gate before cleanup succeeds can lose the only durable reminder of the external responsibility.

**Approach.** Call `finalAction(true, true, false, true)` for a deleting object whose external cleanup has not succeeded yet.

**Why it holds here.** With deletion in progress, the finalizer present and `cleaned` false, the function returns `cleanup`, so the finalizer keeps the object until the external resource is gone.

**A plausible wrong approach.** Removing the finalizer first and cleaning up afterward. The function would return `remove-own-finalizer`, the check panics with `cleanup`, and in a cluster the object could disappear before cleanup ran, leaving no record of the external resource.

**Verify.** Print the action for `cleaned` false and true and see `cleanup` then `remove-own-finalizer`.

## 4. Remove only after success

Inspect a deleting object with confirmed cleanup.

```go
check(finalAction(true, true, true, true) == "remove-own-finalizer", "release")
```

**Expected:** The action is remove-own-finalizer.

Successful cleanup and removal are separate durable steps. Retrying either must tolerate the previous step having already completed.

**Approach.** Call `finalAction(true, true, true, true)` for a deleting object whose cleanup is confirmed.

**Why it holds here.** The only remaining duty is releasing this controller's own gate, so the function returns `remove-own-finalizer`. On the next observation the finalizer is gone and the action becomes `done`.

**A plausible wrong approach.** Returning `done` after cleanup without removing the finalizer. The check panics with `release`, and in a cluster the object would stay in Terminating because deletion waits for every finalizer to be removed.

**Verify.** Print `finalAction(true, true, true, true)` and then `finalAction(true, false, true, true)` and see `remove-own-finalizer done`.

## 5. Refuse ownership mismatch

Inspect a resource whose observed UID no longer matches the owned UID.

```go
check(finalAction(true, true, false, false) == "ownership-error", "UID mismatch")
```

**Expected:** The action is ownership-error.

A replacement resource reusing a name is not owned merely because the name is familiar. Do not delete it to force progress.

**Approach.** Check ownership before anything else: when the observed UID does not match the owned UID, return `ownership-error` regardless of the other flags.

**Why it holds here.** `owned` is false, so the first branch returns `ownership-error` and the controller neither cleans up nor removes finalizers on an object it does not own.

**A plausible wrong approach.** Placing the ownership test after the deleting branch. For this input the function returns `cleanup` before it reads `owned`, the check panics with `UID mismatch`, and a real controller would delete external resources of a replacement that reused the name.

**Verify.** Print `finalAction(false, false, false, false)` and `finalAction(true, true, true, false)` and see `ownership-error` both times.

## 6. Transfer preservation of other finalizers

Remove only lesson.example/cleanup from two entries.

```go
values := []string{"lesson.example/cleanup", "other.example/retain"}
out := []string{}
for _, v := range values {
	if v != "lesson.example/cleanup" {
		out = append(out, v)
	}
}
check(len(out) == 1 && out[0] == "other.example/retain", "preserve others")
```

**Expected:** The unrelated entry remains.

Each controller owns its own finalizer entry. Editing the list must preserve responsibilities belonging to other components.

**Approach.** Build a new slice that keeps every finalizer except the exact string `lesson.example/cleanup`.

**Why it holds here.** Only the entry equal to this controller's name is skipped, so `other.example/retain` is copied to `out` and remains the single element.

**A plausible wrong approach.** Removing by position with `values[:len(values)-1]`, assuming this controller's entry is last. Here it is first, so the slice keeps `lesson.example/cleanup`, drops the other controller's entry and the check panics with `preserve others`.

**Verify.** Print `out` and see `[other.example/retain]`; the positional version prints `[lesson.example/cleanup]`.

## Transfer after comparison

Write `removeFinalizer(list []string, name string) []string` that returns a new slice without `name` and leaves the input unchanged. Check `[other.example/a lesson.example/cleanup other.example/b]` gives the two others in order, a list without the name comes back equal, and an empty list stays empty. Explain which case removal by position or replacing the list with nil would break.
