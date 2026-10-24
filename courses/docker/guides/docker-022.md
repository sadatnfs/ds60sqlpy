# docker-022: Resource limits, contention and honest performance experiments

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-021`

## Learning objectives

Design a controlled CPU comparison. Define a safe resource stress boundary. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

CPU and memory are finite resources shared by containers and other host workloads. Resource controls constrain or weight access; they do not automatically reserve a dedicated physical machine. A process can be throttled, run slowly under contention or be killed after memory pressure, depending on its settings and the kernel.

A CPU quota limits how much CPU time a cgroup can consume over a period. A memory limit constrains accounted memory, with behavior influenced by swap and engine configuration. Containers still share the underlying host or VM budget. Allocating a large limit in Compose does not create physical RAM.

Performance experiments need controlled inputs and measurements. A single fast run can benefit from caches, idle neighbors or a different architecture. Record the workload, image, limits, host allocation and several runs. Avoid deliberately exhausting the host as a lesson demonstration.

## Anatomy and a trace you can follow

The fixture uses modest `mem_limit`, `cpus` and `pids_limit` settings. These are runtime constraints on the teaching process, not proof of a production capacity plan. `docker stats --no-stream` gives a point-in-time view. Observe trends with bounded sampling if you need a rate, and distinguish cumulative values from instantaneous ones.

For a safe experiment, compare a short CPU computation at two modest limits in the disposable project. Keep data size fixed and avoid claiming that a single elapsed time isolates every scheduler effect. Memory fault experiments require deliberately small inputs and a controlled target.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Declare bounded teaching resources

This is a Compose service fragment.

```yaml
mem_limit: 128m
cpus: 0.5
pids_limit: 64
```

**Expected observation:** The app runs within explicit small constraints; these do not reserve half a physical core exclusively.

### Worked example 2: Read a bounded resource sample

Select only the owned app container.

```sh
docker stats --no-stream "$(docker compose -p ds60-docker-study ps -q app)"
```

**Expected observation:** A point-in-time sample for the owned container; it is not a full capacity study.

## Six progressive exercises

### Exercise 1: Compare a CPU limit with dedicated hardware.

**Expected evidence:** A quota constrains time; it does not grant exclusive cores.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict the effect of insufficient engine VM memory.

**Expected evidence:** Container limits cannot compensate for missing host capacity.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a controlled CPU comparison.

**Expected evidence:** Same input and image, one changed limit, several bounded measurements.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose slowness without assuming memory failure.

**Expected evidence:** Compare CPU throttling, I/O, requests and memory observations.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why a single docker stats sample is limited.

**Expected evidence:** It does not capture the whole workload or historical peaks.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Define a safe resource stress boundary.

**Expected evidence:** Small fixed workload, timeout and owned disposable target.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose slowness without assuming memory failure. Use its expected observation, Compare CPU throttling, I/O, requests and memory observations., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/containers/resource_constraints/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-022: Resource limits, contention and honest performance experiments.
Read courses/docker/guides/docker-022.md and courses/docker/lessons/docker-022.md. Direct prerequisites: `docker-021`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
