# docker-036: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Compose is excellent for defining and operating a related application on a selected engine. It does not automatically provide a distributed scheduler, multi-node failure recovery or a cloud load balancer. A process can be restarted on one host without making the application resilient to loss of that host.

Orchestration systems coordinate desired state across resources and failure domains. Kubernetes introduces API objects, controllers, scheduling, service discovery and policy with its own complexity. Moving a Compose app to Kubernetes is a design exercise, not a mechanical translation that guarantees reliability.

The correct choice follows the workload. A local learning classroom benefits from a simple single-engine model with explicit volumes. A public service with strict availability and scaling requirements may need a different operational architecture. More infrastructure is not automatically a better educational or production experience.

Map concepts carefully: an image is reused; a container process still runs; Compose service configuration may inform a Pod template; a named local volume does not automatically become a portable replicated database. Published host ports and Kubernetes Services have different routing and ownership semantics.

Before changing platforms, write the failure model. What happens if a process exits, the engine restarts, the host disk fails, a dependency is unavailable or an availability zone disappears? Each case requires evidence and a recovery mechanism, not merely a new YAML file.

## Exercise 1: Predict whether Compose survives host loss automatically.

Restarting a process on a live host differs from replacing a failed host and recovering its data. State the actual failure domain.

**Expected:** Not without an external recovery design.

## Exercise 2: Identify the classroom reason for Compose.

The product’s scope is one learner machine. A distributed control plane would add prerequisites without automatically improving that experience.

**Expected:** A reproducible local application with understandable resource ownership.

## Exercise 3: Build a failure-domain matrix.

For each row, name detection, recovery and retained state. Empty cells reveal architecture work still needed.

**Expected:** Process, container, engine, host and external dependency rows.

## Exercise 4: Diagnose a mechanical volume translation to Kubernetes.

A claim in YAML does not prove the storage exists or has the desired durability. Validate the actual provisioner and application data behavior.

**Expected:** A storage class and data recovery model are still required.

## Exercise 5: Explain why a load balancer does not replicate a database.

A request router can select healthy endpoints while all endpoints still depend on one failing data store.

**Expected:** Traffic distribution and data durability are separate mechanisms.

## Exercise 6: Choose an orchestration approach for a stated workload.

Defend the smallest system that meets the actual requirements. A platform name is not a substitute for a failure and recovery design.

**Expected:** A reasoned choice based on availability, scaling, operations and learning cost.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
