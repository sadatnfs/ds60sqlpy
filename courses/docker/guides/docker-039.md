# docker-039: Namespaces, cgroups, OCI and the runtime beneath Docker

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-038`

## Learning objectives

Draw the client-to-process runtime chain. Describe the shared-kernel security implication. Use namespaces, cgroups and OCI runtime accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A namespace changes which operating-system objects a process can see. Linux provides namespaces for areas including processes, mounts, networking and users. A cgroup groups processes for accounting and resource controls. Visibility isolation and resource limits are different mechanisms, even though both contribute to a container environment.

The Open Container Initiative, or OCI, defines specifications for image and runtime interoperability. Docker tooling can use components such as containerd and an OCI runtime to manage execution. These layers explain why an image format, an engine API and a running process are related but not identical products.

The shared Linux kernel remains an important trust boundary. A container is not a separate guest kernel by default. Kernel vulnerabilities, privileged configuration and host mounts can affect isolation. Rootless mode and least privilege reduce specific risks but do not turn every process into a harmless mathematical function.

### Key terms

- **Namespace:** A kernel feature that changes which operating-system objects, such as processes or mounts, a process can see.
- **cgroup:** A kernel group of processes used for resource accounting and limits.
- **OCI:** The Open Container Initiative, which defines image and runtime specifications for interoperability.
- **OCI runtime:** The low-level program that creates a container process from a bundle according to the OCI runtime specification.
- **containerd:** The container manager that Docker tooling can use to pull images and supervise containers through an OCI runtime.

## Anatomy and a trace you can follow

Trace a launch as client request, engine configuration, runtime setup of namespaces and cgroups, filesystem mounts, then the application process. A process still makes ordinary system calls. Its view and allowed operations depend on the setup around it.

Use read-only observations in the fixture. `/proc/self/status` can show process information, while cgroup details vary by host and cgroup version. Do not modify kernel settings or mount host control filesystems to make the lesson output match a screenshot.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-039.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Read the isolation from inside without changing anything. Run worked example 1 and note that the process sees itself as PID 1, while `docker compose -p ds60-docker-study top app` on the same engine lists the app's processes with host-side PIDs. Then compare kernels: `uname -r` on a Linux host, and `docker run --rm --pull never ds60-docker-study:local python -c "import platform; print(platform.release())"` inside. On Linux both print the same release, because containers share the host kernel; on Docker Desktop the container reports the virtual machine's kernel, which differs from macOS or Windows. Finally run the same image with `--network none` and `python -c "import socket; print(socket.if_nameindex())"` to see a network namespace holding only loopback. Every container used `--rm`, so nothing persists.

## Worked example / walkthrough

### Worked example 1: Inspect process namespace evidence

This uses the process view already available in the fixture image.

```sh
docker run --rm --pull never ds60-docker-study:local python -c "import os; print('pid', os.getpid()); print(open('/proc/self/cgroup').read())"
```

**Expected observation:** The process prints its PID and cgroup membership view; exact paths depend on the engine configuration.

### Worked example 2: Separate isolation and accounting

This is a mechanism map.

```text
network namespace -> interfaces, loopback and routes visible to a process
mount namespace -> filesystem mount view
cgroup -> resource accounting and limits
OCI runtime -> applies a prepared runtime configuration
```

**Expected observation:** No single row replaces the other mechanisms.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Distinguish namespace and cgroup.

**Hint:** Ask which one hides objects and which one limits resource use.

### Exercise 2: Predict whether the container has its own kernel.

**Hint:** Compare uname -r inside a container with the engine host.

### Exercise 3: Draw the client-to-process runtime chain.

**Hint:** Follow a docker run from the CLI to the engine to the OCI runtime.

### Exercise 4: Diagnose a missing cgroup path from an example.

**Hint:** Check whether the host uses cgroup v1 or v2.

### Exercise 5: Explain OCI interoperability limits.

**Hint:** Ask what the OCI specification standardizes and what it leaves to implementations.

### Exercise 6: Describe the shared-kernel security implication.

**Hint:** Ask what a kernel vulnerability means for every container on the host.

## Common mistakes and diagnosis

Believing each container has its own kernel. Changing kernel or cgroup settings to match an example. Assuming every OCI runtime behaves identically.

Exercise 4 is this chapter's boundary case: Diagnose a missing cgroup path from an example. Record the host's cgroup version and mount layout, then map the example's path onto it without changing kernel or boot settings.

Inside the app container, `python -c "import os; print(os.cpu_count())"` prints the engine's full CPU count rather than the half CPU the service is allowed, and `/proc/meminfo` shows the machine's memory rather than 128 MB. Neither source is namespaced; the limits live in the cgroup. Programs that size worker pools or heaps from those numbers start more threads or allocate more memory than the cgroup permits, and the kernel's out-of-memory killer then ends the process, which Docker reports as exit code 137. Read the real limits from `/sys/fs/cgroup/memory.max` and `/sys/fs/cgroup/cpu.max` on cgroup v2, and set worker counts explicitly rather than trusting detected hardware.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Match network namespace, mount namespace, cgroup and OCI runtime to what each isolates or controls.

**Transfer case.** A colleague says containers are lightweight virtual machines, so a kernel exploit inside one cannot touch the others. Correct the claim using what this lesson's observations showed.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Open Container Initiative](https://opencontainers.org/)
- [Docker Engine security: kernel namespaces](https://docs.docker.com/engine/security/#kernel-namespaces)
- [Docker Engine security: control groups](https://docs.docker.com/engine/security/#control-groups)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-039: Namespaces, cgroups, OCI and the runtime beneath Docker.
Read courses/docker/guides/docker-039.md and courses/docker/lessons/docker-039.md. Direct prerequisites: `docker-038`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
