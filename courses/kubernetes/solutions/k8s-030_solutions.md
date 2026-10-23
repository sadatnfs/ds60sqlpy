# k8s-030: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

An operator combines a custom API with a controller that repeatedly moves observed state toward desired state. Reconciliation is level-driven: the controller reads the current state and decides the next bounded action. Events help schedule work, but they are not a reliable once-only transaction log. The same event can be delivered repeatedly, and a restart can require reconstructing the needed work from objects already present.

For LessonReport, imagine a qualified controller that owns one child Deployment and reports whether its requested message and replica count have converged. The first reconcile may create the child; a later reconcile with the same state should do nothing. A changed spec can update the intended child, but an unrelated child with the same name must not be adopted solely because its name matches.

This chapter supplies an executable pure-Python decision model and real custom-resource input. It does not ship or claim to run a production operator. Live work needs a reviewed, preloaded controller with a documented child contract and namespaced permissions. The model makes ownership, idempotence and status reasoning visible before that operation is available.

## Exercise 1: Build the state table

The table separates an allowed convergence action from a collision. Choosing update based only on a name would mutate a resource outside the parent ownership graph, even if the desired spec seems harmless.

**Expected:** create, no-op, update and refuse respectively.

## Exercise 2: Replay repeated reconciliation

A level-driven controller reconstructs the result from state. It does not need the event stream to prove which event was first. The stable child identity is evidence against a create-on-every-event bug.

**Expected:** One create followed by two no-ops, with one child.

## Exercise 3: Change desired replicas

The model demonstrates decision idempotence only. A live controller still needs to wait for Deployment observation, readiness and any required application gate before recording a successful changed generation.

**Expected:** update then no-op after observed state matches.

## Exercise 4: Test replacement identity

The safe default is a collision report. Adoption would require an explicit separately reviewed policy. Automatic takeover could erase resources belonging to a different operation or a previous partially completed cleanup.

**Expected:** The old child is foreign to the new parent under this contract.

## Exercise 5: Review retry and status

A useful condition carries a reason tied to the current generation and retry state. Repeating a permanently invalid request without feedback wastes capacity, while treating every temporary failure as terminal prevents convergence.

**Expected:** Bounded backoff for transient failure; corrected intent for invalid input; stale readiness does not pass.

## Exercise 6: Complete a finalizer obligation

The controller must know its obligation completed before removing its marker. A bounded failure should surface the missing action and retain recoverable evidence. Clearing unrelated finalizers is outside this controller ownership.

**Expected:** other.cleanup remains; failed cleanup retains lesson.cleanup.

## Boundary and troubleshooting review

A status field supplied by the learner or copied from a synthetic trace is not a live controller observation. A child Ready condition with an old observed generation is insufficient for a changed message. Compare parent generation, intended child fields, owned identities and application output.

Do not debug a stuck finalizer by indiscriminately clearing metadata.finalizers. Identify the responsible controller, its cleanup contract and the missing evidence. If the required controller is not provisioned, label the live activity unavailable rather than impersonating it with a sequence of manual creates.
