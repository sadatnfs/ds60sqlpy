# docker-036: Compose on one host and the limits of orchestration

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-035`

## Learning objectives

Build a failure-domain matrix. Choose an orchestration approach for a stated workload. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

Compose is excellent for defining and operating a related application on a selected engine. It does not automatically provide a distributed scheduler, multi-node failure recovery or a cloud load balancer. A process can be restarted on one host without making the application resilient to loss of that host.

Orchestration systems coordinate desired state across resources and failure domains. Kubernetes introduces API objects, controllers, scheduling, service discovery and policy with its own complexity. Moving a Compose app to Kubernetes is a design exercise, not a mechanical translation that guarantees reliability.

The correct choice follows the workload. A local learning classroom benefits from a simple single-engine model with explicit volumes. A public service with strict availability and scaling requirements may need a different operational architecture. More infrastructure is not automatically a better educational or production experience.

## Anatomy and a trace you can follow

Map concepts carefully: an image is reused; a container process still runs; Compose service configuration may inform a Pod template; a named local volume does not automatically become a portable replicated database. Published host ports and Kubernetes Services have different routing and ownership semantics.

Before changing platforms, write the failure model. What happens if a process exits, the engine restarts, the host disk fails, a dependency is unavailable or an availability zone disappears? Each case requires evidence and a recovery mechanism, not merely a new YAML file.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Predict whether Compose survives host loss automatically.

**Expected evidence:** Not without an external recovery design.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Identify the classroom reason for Compose.

**Expected evidence:** A reproducible local application with understandable resource ownership.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Build a failure-domain matrix.

**Expected evidence:** Process, container, engine, host and external dependency rows.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a mechanical volume translation to Kubernetes.

**Expected evidence:** A storage class and data recovery model are still required.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why a load balancer does not replicate a database.

**Expected evidence:** Traffic distribution and data durability are separate mechanisms.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Choose an orchestration approach for a stated workload.

**Expected evidence:** A reasoned choice based on availability, scaling, operations and learning cost.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a mechanical volume translation to Kubernetes. Use its expected observation, A storage class and data recovery model are still required., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/intro/features-uses/)
- [Official reference 2](https://kubernetes.io/docs/concepts/overview/)

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
