# docker-022: Resource limits, contention and honest performance experiments

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-021`

## Learning objectives

Design a controlled CPU comparison. Define a safe resource stress boundary. Use memory limit, CPU limit and PID limit accurately when you explain what you observed.

## Purpose, vocabulary and mental model

CPU and memory are finite resources shared by containers and other host workloads. Resource controls constrain or weight access; they do not automatically reserve a dedicated physical machine. A process can be throttled, run slowly under contention or be killed after memory pressure, depending on its settings and the kernel.

A CPU quota limits how much CPU time a cgroup can consume over a period. A memory limit constrains accounted memory, with behavior influenced by swap and engine configuration. Containers still share the underlying host or VM budget. Allocating a large limit in Compose does not create physical RAM.

Performance experiments need controlled inputs and measurements. A single fast run can benefit from caches, idle neighbors or a different architecture. Record the workload, image, limits, host allocation and several runs. Avoid deliberately exhausting the host as a lesson demonstration.

### Key terms

- **Memory limit:** A cap on a container's accounted memory, beyond which its processes can be killed under memory pressure.
- **CPU limit:** A quota on the CPU time a container's cgroup may use per period, which throttles work but does not reserve a core.
- **PID limit:** A bound on how many processes a container may create, set in Compose with `pids_limit`.
- **Contention:** Competition among workloads for the same shared CPU, memory or I/O, which slows each of them.
- **Measurement:** Several recorded runs with a fixed workload, image, limits and host allocation that support an honest performance claim.

## Anatomy and a trace you can follow

The fixture uses modest `mem_limit`, `cpus` and `pids_limit` settings. These are runtime constraints on the teaching process, not proof of a production capacity plan. `docker stats --no-stream` gives a point-in-time view. Observe trends with bounded sampling if you need a rate, and distinguish cumulative values from instantaneous ones.

For a safe experiment, compare a short CPU computation at two modest limits in the disposable project. Keep data size fixed and avoid claiming that a single elapsed time isolates every scheduler effect. Memory fault experiments require deliberately small inputs and a controlled target.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-022.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Compare two CPU limits with the same small workload: run `docker run --rm --pull never --cpus 1 ds60-docker-study:local python -c "import time; t=time.time(); sum(range(30_000_000)); print(round(time.time()-t,2))"` three times, then three times with `--cpus 0.25`, and record all six numbers. The limited runs take longer, but the ratio is rarely exactly four. Add `print(open('/sys/fs/cgroup/cpu.stat').read())` to one limited run on a cgroup v2 engine and look for a nonzero `nr_throttled`. Next, start a named container with `--memory 64m` that allocates `bytearray(200_000_000)`, then read `docker inspect --format '{{.State.OOMKilled}} {{.State.ExitCode}}'` on it. Expect `true 137`. Remove the named container when you finish.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Compare a CPU limit with dedicated hardware.

**Hint:** Ask what cpus: 0.5 limits: cores or CPU time per period.

### Exercise 2: Predict the effect of insufficient engine VM memory.

**Hint:** Compare the engine VM's memory setting with the container's mem_limit.

### Exercise 3: Design a controlled CPU comparison.

**Expected evidence:** Same input and image, one changed limit, several bounded measurements.

**Hint:** Change only the CPU limit and repeat each measurement several times.

### Exercise 4: Diagnose slowness without assuming memory failure.

**Hint:** Collect CPU throttling, I/O wait, request timing and memory figures before choosing a cause.

### Exercise 5: Explain why a single docker stats sample is limited.

**Hint:** Ask what happened before and after the moment the sample was taken.

### Exercise 6: Define a safe resource stress boundary.

**Expected evidence:** Small fixed workload, timeout and owned disposable target.

**Hint:** Choose a fixed amount of work, a timeout and a container you own.

## Common mistakes and diagnosis

Reading `cpus: 0.5` as half of a dedicated core. Raising container limits when the engine VM itself is short of memory. Drawing a conclusion from one `docker stats` sample.

Exercise 4 is this chapter's boundary case: Diagnose slowness without assuming memory failure. Check `docker stats` CPU% against the cpus quota and the cgroup `cpu.stat` `nr_throttled` count before reading memory usage.

A common misreading is that exit code 137 always means the container ran out of memory. The code only says the main process was ended by SIGKILL, and that signal also arrives when a stop exceeds its grace period, when someone runs `docker kill`, or when the host kernel kills a process for its own reasons. Before raising a memory limit, read `.State.OOMKilled` in `docker inspect`, which is set when the container's memory limit was the cause, and compare the time of death with the logs of any stop or deploy command that ran then.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Say which column in a `docker stats` sample would rise first under CPU contention and which under a memory leak.

**Transfer case.** A worker has `pids_limit: 64` and starts one thread per job. Under load it fails with `can't start new thread` while memory and CPU look normal in `docker stats`. Explain the failure and how you would confirm it.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/)

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
