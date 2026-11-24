# go-037: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A controller repeatedly compares desired and observed state and takes a bounded step toward convergence. Reconciliation is level-based: it should ask what is true now rather than assume it received every historical event. Events are hints that work may be needed, not an exactly-once command log. A successful reconcile can be a no-op when the object already satisfies intent. Repeating it should not create duplicate side effects. Separate a pure decision function from the API adapter so planning can be tested deterministically. External operations need ownership, idempotency keys and explicit handling of uncertain outcomes.

Represent desired and observed state as small values, then return a typed action such as create, update or none. Avoid embedding API calls inside every conditional. The adapter performs an action, records evidence and schedules another observation. A real controller often converges over several reconciliations rather than blocking until every resource becomes ready. Status should describe observed facts, including the generation to which they apply.

## 1. Plan a missing child: predict an edited check

Copy worked example 1 into a scratch pad and change `check(plan(3, false, 0) == "create", "missing child")` to `check(plan(3, true, 0) == "create", "missing child")` inside its check. Before running, predict whether the check still passes and explain why; then restore it.

The unchanged code is worked example 1:

```go
check(plan(3, false, 0) == "create", "missing child")
```

**Expected:** The changed run panics with `missing child` because the edited check no longer holds. Restoring the original line brings back the worked observation: the action is create.

The planner reports intent without performing a cluster mutation. The adapter still needs an exact owner identity.

**Approach.** Walk `plan(3, true, 0)` through the branches in order: 3 is not negative, the child exists, and 3 differs from 0, so the planner returns `update`.

**Why it holds here.** The edit only flipped `exists`, and an existing child is never created again, so the result is `update` rather than `create` and the check panics with `missing child`.

**A plausible wrong approach.** Predicting `create` because a current count of 0 looks like "nothing there". The planner decides absence from `exists`, not from the count, which is what lets an existing child legitimately sit at 0.

**Verify.** Print `plan(3, true, 0)` and `plan(3, false, 0)` and see `update create`.

## 2. Plan a changed child: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `check(plan(3, true, 3) == "update", "changed child")`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
check(plan(3, true, 2) == "update", "changed child")
```

**Expected:** Before the repair the program panics with `changed child`; after it the line reads `check(plan(3, true, 2) == "update", "changed child")` again and the action is update.

The update is justified by a current difference, not by assuming a prior event was delivered once.

**Approach.** Evaluate the edited call `plan(3, true, 3)`: the child exists and its observed count already equals the desired 3, so the planner returns `none`.

**Why it holds here.** The edited check expects `update` for a converged child, which the planner never returns when nothing differs, so it panics with `changed child`. The original call with current 2 has a real difference and returns `update`.

**A plausible wrong approach.** Expecting `update` because an earlier event announced a change to 3. The planner compares desired with observed state each time, so a change that has already been applied produces no further write.

**Verify.** Print `plan(3, true, 2)` and `plan(3, true, 3)` and see `update none`.

## 3. Make convergence a no-op

Observe an existing child already at count 3.

```go
check(plan(3, true, 3) == "none", "converged")
```

**Expected:** The action is none.

A repeated event should not produce duplicate writes after convergence. No-op behavior also reduces control-plane load.

**Approach.** Call `plan(3, true, 3)`, where desired and observed state agree, and expect the planner's no-op result.

**Why it holds here.** None of the earlier branches apply, invalid, create or update, so the function reaches `return "none"` and the adapter writes nothing.

**A plausible wrong approach.** Returning `update` whenever the planner runs so that every event re-applies the spec. For this converged input the check panics with `converged`, and every periodic resync would send a write that changes nothing.

**Verify.** Print `plan(3, true, 3)` three times and see `none` each time, which shows repeated events are harmless.

## 4. Reject invalid desired state

Supply a negative desired count.

```go
check(plan(-1, true, 2) == "invalid", "invalid intent")
```

**Expected:** The planner returns invalid.

A persistent validation error should be surfaced to the user rather than retried forever as if it were a transient API outage.

**Approach.** Validate desired state first: any negative `wanted` returns `invalid` before existence or counts are considered.

**Why it holds here.** -1 hits the first branch, so the planner reports `invalid` even though the child exists and its count differs.

**A plausible wrong approach.** Placing the validation after the existence and difference checks. Then `plan(-1, true, 2)` returns `update`, the adapter would try to set a negative count, and the check panics with `invalid intent`.

**Verify.** Print `plan(-1, true, 2)` and `plan(-1, false, 0)` and see `invalid invalid`.

## 5. Simulate a converging step

Start at count 1, apply the planned update to 3 and plan again.

```go
current := 1
check(plan(3, true, current) == "update", "first plan")
current = 3
check(plan(3, true, current) == "none", "second plan")
```

**Expected:** The next plan is none.

The state transition shows convergence for this simple model. Distributed delays and conflicts belong to adapter-level integration tests.

**Approach.** Plan from current 1, apply the action by setting `current` to the desired 3, and plan again from the new observation.

**Why it holds here.** The first plan sees a difference and returns `update`; after the update the observed count equals the desired count, so the second plan returns `none`, which is convergence.

**A plausible wrong approach.** Modeling the update as one step closer, `current++`. After one step the count is 2, the second plan returns `update` again and the check panics with `second plan`; the action means set to the desired count.

**Verify.** Print both plans and see `update none`, then plan a third time with `current` still 3 and see `none` again.

## 6. Transfer scale-to-zero

Request zero for an existing child with count 2.

```go
check(plan(0, true, 2) == "update" && plan(0, true, 0) == "none", "zero scale")
```

**Expected:** The planner requests update, then converges at zero.

Zero can be a valid desired value. Confusing it with absence would prevent a legitimate scale-to-zero operation.

**Approach.** Treat 0 as a real desired count: `plan(0, true, 2)` differs from the observed 2 and returns `update`, and `plan(0, true, 0)` returns `none`.

**Why it holds here.** 0 passes the `wanted < 0` validation, the child exists, and the comparison with current drives the result, so the planner scales down and then converges.

**A plausible wrong approach.** Validating with `wanted <= 0`. Zero then becomes `invalid`, the first call returns `invalid` instead of `update` and the check panics with `zero scale`; a legitimate scale-to-zero is refused.

**Verify.** Print `plan(0, true, 2)`, `plan(0, true, 0)` and `plan(0, false, 0)` and see `update none create`.

## Transfer after comparison

Add a `deleting bool` parameter, checked after validation, that returns `delete` for an existing child and `none` for a missing one. Check `plan(3, true, 3, true)` gives `delete`, `plan(3, false, 0, true)` gives `none`, `plan(0, true, 0, false)` still gives `none`, and replanning after each applied action converges to `none`. Explain which result a planner that treats a count of zero as absent would get wrong.
