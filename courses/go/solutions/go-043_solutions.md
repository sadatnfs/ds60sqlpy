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

## 2. Retain a healthy object: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(finalAction(true, true, false, true) == "reconcile", "normal")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
check(finalAction(false, true, false, true) == "reconcile", "normal")
```

**Expected:** Before the repair the program panics with `normal`; after it the line reads `check(finalAction(false, true, false, true) == "reconcile", "normal")` again and the action is reconcile.

A finalizer does not itself request deletion. Normal desired-state work continues while deletion has not begun.

## 3. Clean before releasing deletion

Inspect a deleting object with outstanding owned cleanup.

```go
check(finalAction(true, true, false, true) == "cleanup", "cleanup")
```

**Expected:** The action is cleanup.

Removing the gate before cleanup succeeds can lose the only durable reminder of the external responsibility.

## 4. Remove only after success

Inspect a deleting object with confirmed cleanup.

```go
check(finalAction(true, true, true, true) == "remove-own-finalizer", "release")
```

**Expected:** The action is remove-own-finalizer.

Successful cleanup and removal are separate durable steps. Retrying either must tolerate the previous step having already completed.

## 5. Refuse ownership mismatch

Inspect a resource whose observed UID no longer matches the owned UID.

```go
check(finalAction(true, true, false, false) == "ownership-error", "UID mismatch")
```

**Expected:** The action is ownership-error.

A replacement resource reusing a name is not owned merely because the name is familiar. Do not delete it to force progress.

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

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
