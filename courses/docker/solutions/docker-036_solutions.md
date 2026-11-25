# docker-036: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-036.md).

## Exercise 1: Predict whether Compose survives host loss automatically.

**Expected answer:** Not without an external recovery design.

**Why:** Restarting a process on a live host differs from replacing a failed host and recovering its data. State the actual failure domain.

**Approach:** Ask what Compose can act on: containers on one engine, not a replacement host when this one fails.

**Why this is correct:** If the host's disk or power fails, study-data and the engine go with it, and no Compose setting brings them back elsewhere.

**A plausible wrong approach:** Counting restart settings as host-loss protection confuses restarting a process with replacing a machine.

**How to verify:** The worked example's failure table shows host disk failure needing an external copy that Compose does not make.

## Exercise 2: Identify the classroom reason for Compose.

**Expected answer:** A reproducible local application with understandable resource ownership.

**Why:** The product’s scope is one learner machine. A distributed control plane would add prerequisites without automatically improving that experience.

**Approach:** Name what the classroom needs: one learner, one machine, resources the learner can list and remove.

**Why this is correct:** Compose gives a reproducible app with a project name that scopes every container, network and volume.

**A plausible wrong approach:** Adopting a cluster scheduler for a single laptop adds setup without improving the learner's experience.

**How to verify:** A learner can see everything the project owns with docker compose ps and docker volume ls filtered by project label.

## Exercise 3: Build a failure-domain matrix.

**Expected evidence:** Process, container, engine, host and external dependency rows.

**Why:** For each row, name detection, recovery and retained state. Empty cells reveal architecture work still needed.

**Approach:** Write rows for process, container, engine, host and outside dependencies, with columns for detection, recovery and state kept.

**Why this is correct:** Filling each cell shows which failures the fixture handles, such as container replacement, and which leave blanks.

**A plausible wrong approach:** Listing only failures you already handle produces a reassuring table with no gaps by design.

**How to verify:** Blank cells, such as host recovery, are named as remaining work rather than left out.

## Exercise 4: Diagnose a mechanical volume translation to Kubernetes.

**Expected answer:** A storage class and data recovery model are still required.

**Why:** A claim in YAML does not prove the storage exists or has the desired durability. Validate the actual provisioner and application data behavior.

**Approach:** Ask where a Kubernetes volume claim gets storage: a storage class and provisioner must exist and meet your durability needs.

**Why this is correct:** A claim requests storage; the cluster decides what backs it, which may be a single node's disk.

**A plausible wrong approach:** Translating study-data to a claim and assuming the data is now durable skips the storage review.

**How to verify:** Check the bound volume's storage class and test a pod reschedule that reads the counter back.

## Exercise 5: Explain why a load balancer does not replicate a database.

**Expected answer:** Traffic distribution and data durability are separate mechanisms.

**Why:** A request router can select healthy endpoints while all endpoints still depend on one failing data store.

**Approach:** Separate traffic paths from data storage: a load balancer picks a healthy endpoint, but every endpoint may use the same database.

**Why this is correct:** If that database fails, all endpoints fail together, however requests are spread.

**A plausible wrong approach:** Adding a load balancer and calling the data highly available addresses routing only.

**How to verify:** Stop the shared data store in a test and observe every endpoint failing behind the balancer.

## Exercise 6: Choose an orchestration approach for a stated workload.

**Expected answer:** A reasoned choice based on availability, scaling, operations and learning cost.

**Why:** Defend the smallest system that meets the actual requirements. A platform name is not a substitute for a failure and recovery design.

**Approach:** Start from the workload's stated needs, availability, scale, who operates it and what learners must learn, and pick the smallest system that meets them.

**Why this is correct:** Each requirement maps to a mechanism, so the choice can be argued from the needs rather than from fashion.

**A plausible wrong approach:** Choosing a platform first and adjusting needs to match it leaves failures and recovery undesigned.

**How to verify:** The recommendation lists each requirement with the feature that meets it and the matching failure-table row.

## Check your transfer

For a single-host teaching fixture used by two classes, Compose remains the better fit: the workload is one process with one small volume, nobody needs failover, and learners benefit from seeing every resource. The recommendation changes if the app must survive host loss, serve many concurrent users, or be run by a team already operating a cluster; then the work is a storage, recovery and traffic design, not a file conversion. A measured outage or a load that one host cannot carry would be the evidence against the current choice.
