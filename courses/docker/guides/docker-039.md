# docker-039: Namespaces, cgroups, OCI and the runtime beneath Docker

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-038`

## Learning objectives

Draw the client-to-process runtime chain. Describe the shared-kernel security implication. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A namespace changes which operating-system objects a process can see. Linux provides namespaces for areas including processes, mounts, networking and users. A cgroup groups processes for accounting and resource controls. Visibility isolation and resource limits are different mechanisms, even though both contribute to a container environment.

The Open Container Initiative, or OCI, defines specifications for image and runtime interoperability. Docker tooling can use components such as containerd and an OCI runtime to manage execution. These layers explain why an image format, an engine API and a running process are related but not identical products.

The shared Linux kernel remains an important trust boundary. A container is not a separate guest kernel by default. Kernel vulnerabilities, privileged configuration and host mounts can affect isolation. Rootless mode and least privilege reduce specific risks but do not turn every process into a harmless mathematical function.

## Anatomy and a trace you can follow

Trace a launch as client request, engine configuration, runtime setup of namespaces and cgroups, filesystem mounts, then the application process. A process still makes ordinary system calls. Its view and allowed operations depend on the setup around it.

Use read-only observations in the fixture. `/proc/self/status` can show process information, while cgroup details vary by host and cgroup version. Do not modify kernel settings or mount host control filesystems to make the lesson output match a screenshot.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

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

### Exercise 1: Distinguish namespace and cgroup.

**Expected evidence:** Object visibility versus grouping and resource controls.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict whether the container has its own kernel.

**Expected evidence:** Ordinary Linux containers share the engine environment kernel.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Draw the client-to-process runtime chain.

**Expected evidence:** Client, engine, runtime setup, mounts and application process.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a missing cgroup path from an example.

**Expected evidence:** Inspect host and cgroup-version differences without changing kernel settings.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain OCI interoperability limits.

**Expected evidence:** A shared specification does not guarantee every platform or feature is identical.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Describe the shared-kernel security implication.

**Expected evidence:** Least privilege and patching remain necessary parts of the trust model.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a missing cgroup path from an example. Use its expected observation, Inspect host and cgroup-version differences without changing kernel settings., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://opencontainers.org/)
- [Official reference 2](https://docs.docker.com/engine/security/#kernel-namespaces)
- [Official reference 3](https://docs.docker.com/engine/security/#control-groups)

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
