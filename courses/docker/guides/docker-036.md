# docker-036: Compose on one host and the limits of orchestration

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-035`

## Learning objectives

Build a failure-domain matrix. Choose an orchestration approach for a stated workload. Use single-host Compose, orchestration and scheduling accurately when you explain what you observed.

## Purpose, vocabulary and mental model

Compose is excellent for defining and operating a related application on a selected engine. It does not automatically provide a distributed scheduler, multi-node failure recovery or a cloud load balancer. A process can be restarted on one host without making the application resilient to loss of that host.

Orchestration systems coordinate desired state across resources and failure domains. Kubernetes introduces API objects, controllers, scheduling, service discovery and policy with its own complexity. Moving a Compose app to Kubernetes is a design exercise, not a mechanical translation that guarantees reliability.

The correct choice follows the workload. A local learning classroom benefits from a simple single-engine model with explicit volumes. A public service with strict availability and scaling requirements may need a different operational architecture. More infrastructure is not automatically a better educational or production experience.

### Key terms

- **Single-host Compose:** Defining and operating a related application on one selected engine, with no multi-node recovery.
- **Orchestration:** Coordinating desired state for workloads across many resources and failure domains.
- **Scheduling:** Deciding which node runs each workload based on resources, constraints and policy.
- **Failure domain:** A set of resources, such as one host, that can fail together and take every workload on it down.
- **Desired state:** The declared configuration that an orchestrator's controllers continually work to make true.

## Anatomy and a trace you can follow

Map concepts carefully: an image is reused; a container process still runs; Compose service configuration may inform a Pod template; a named local volume does not automatically become a portable replicated database. Published host ports and Kubernetes Services have different routing and ownership semantics.

Before changing platforms, write the failure model. What happens if a process exits, the engine restarts, the host disk fails, a dependency is unavailable or an availability zone disappears? Each case requires evidence and a recovery mechanism, not merely a new YAML file.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-036.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Compare failure domains

This is a design table.

```text
process failure: restart may help
container replacement: retained volume may preserve data
host disk failure: local volume alone is insufficient
multiple hosts: scheduling and durable data design required
```

**Expected observation:** A mechanism that handles one failure does not automatically handle all the others.

### Worked example 2: Map only what actually transfers

These are conceptual correspondences, not generated manifests.

```text
image -> same packaged application
Compose service -> workload requirements to redesign
local volume -> storage/recovery requirement
published port -> explicit external traffic design
```

**Expected observation:** The migration preserves requirements, not necessarily the original configuration syntax.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict whether Compose survives host loss automatically.

**Hint:** Ask what restarts the project if the host itself fails.

### Exercise 2: Identify the classroom reason for Compose.

**Hint:** Ask what a learner needs to own and understand on one machine.

### Exercise 3: Build a failure-domain matrix.

**Expected evidence:** Process, container, engine, host and external dependency rows.

**Hint:** For each row, name what fails and what recovers it.

### Exercise 4: Diagnose a mechanical volume translation to Kubernetes.

**Hint:** Ask what replaces a named volume's storage and its backup in a cluster.

### Exercise 5: Explain why a load balancer does not replicate a database.

**Hint:** Ask what a load balancer copies: requests or data.

### Exercise 6: Choose an orchestration approach for a stated workload.

**Hint:** Weigh availability needs against operating and learning cost.

## Common mistakes and diagnosis

Treating Compose restart policies as host-failure recovery. Translating volumes to Kubernetes without a storage and backup design. Expecting a load balancer to replicate data.

Exercise 4 is this chapter's boundary case: Diagnose a mechanical volume translation to Kubernetes. Name the storage class and provisioner the translated claim depends on, and check whether a restore procedure exists for its data. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Map each Compose concept to the requirement it becomes on a cluster without looking at the table. Then reconstruct worked example 2 (Map only what actually transfers) with one different value, predict what changes, and name which of single-host Compose, orchestration, scheduling and failure domain the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Why use Compose](https://docs.docker.com/compose/intro/features-uses/)
- [Kubernetes overview](https://kubernetes.io/docs/concepts/overview/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-036: Compose on one host and the limits of orchestration.
Read courses/docker/guides/docker-036.md and courses/docker/lessons/docker-036.md. Direct prerequisites: `docker-035`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
