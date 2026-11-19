# docker-036: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-036.md`.

## Exercise 1: Predict whether Compose survives host loss automatically.

**Expected answer:** Not without an external recovery design.

**Why:** Restarting a process on a live host differs from replacing a failed host and recovering its data. State the actual failure domain.

## Exercise 2: Identify the classroom reason for Compose.

**Expected answer:** A reproducible local application with understandable resource ownership.

**Why:** The product’s scope is one learner machine. A distributed control plane would add prerequisites without automatically improving that experience.

## Exercise 3: Build a failure-domain matrix.

**Expected evidence:** Process, container, engine, host and external dependency rows.

**Why:** For each row, name detection, recovery and retained state. Empty cells reveal architecture work still needed.

## Exercise 4: Diagnose a mechanical volume translation to Kubernetes.

**Expected answer:** A storage class and data recovery model are still required.

**Why:** A claim in YAML does not prove the storage exists or has the desired durability. Validate the actual provisioner and application data behavior.

## Exercise 5: Explain why a load balancer does not replicate a database.

**Expected answer:** Traffic distribution and data durability are separate mechanisms.

**Why:** A request router can select healthy endpoints while all endpoints still depend on one failing data store.

## Exercise 6: Choose an orchestration approach for a stated workload.

**Expected answer:** A reasoned choice based on availability, scaling, operations and learning cost.

**Why:** Defend the smallest system that meets the actual requirements. A platform name is not a substitute for a failure and recovery design.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
