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

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-039.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

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

Exercise 4 is this chapter's boundary case: Diagnose a missing cgroup path from an example. Record the host's cgroup version and mount layout, then map the example's path onto it without changing kernel or boot settings. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Match network namespace, mount namespace, cgroup and OCI runtime to what each isolates or controls. Then reconstruct worked example 2 (Separate isolation and accounting) with one different value, predict what changes, and name which of namespaces, cgroups, OCI runtime and container runtime the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

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
