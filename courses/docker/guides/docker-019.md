# docker-019: Network isolation, gateways and outbound connectivity

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-018`

## Learning objectives

Design a frontend/backend attachment table. Define outbound acceptance for an offline worker. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A gateway forwards traffic beyond a local network. Docker bridge networking commonly uses routing and address translation for outbound traffic. The exact host rules depend on the engine and platform. Container traffic can reach external destinations unless its configuration and surrounding policy restrict it.

An internal network reduces external connectivity for its attached network. A service attached to both an external-facing and internal network can intentionally connect two application tiers, but this is not an automatic application firewall. Review the service’s role, listener ports and credentials.

Network mode none creates a container without ordinary external networking. This is useful for a pure computation that needs no DNS or HTTP. Host networking removes a major layer of network isolation and behaves differently across environments; it is not the beginner default or a repair for a wrong port mapping.

## Anatomy and a trace you can follow

Compose networks are named model objects. Services explicitly join the networks they require. A database can live only on `backend`, while an API joins `frontend` and `backend`. Marking `backend` internal should be tested from the actual callers and engine because host connectivity and DNS details are operational facts.

The fixture uses a single bridge for its first exercises. Sketch multi-tier designs before editing your copy. No chapter asks you to change host firewall rules, install a packet filter or disable existing security software.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Separate tiers in a model fragment

This illustrates attachment, not a complete deployable app.

```yaml
services:
  api:
    networks: [frontend, backend]
  database:
    networks: [backend]
networks:
  frontend: {}
  backend:
    internal: true
```

**Expected observation:** Only api joins both named networks; database has no declared frontend attachment.

### Worked example 2: Run a network-free computation

This deliberately needs no external connectivity.

```sh
docker run --rm --pull never --network none ds60-docker-study:local python -c "print(sum([2, 4, 6]))"
```

**Expected observation:** 12 prints without a network request; the computation does not need DNS or a published port.

## Six progressive exercises

### Exercise 1: Distinguish attachment from published ports.

**Expected evidence:** Joining a network and exposing a host socket are different operations.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict a pure computation with network none.

**Expected evidence:** It succeeds if its files and runtime are already present.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a frontend/backend attachment table.

**Expected evidence:** Each service joins only the networks needed by its role.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose host-network mode used to hide a mapping error.

**Expected evidence:** Restore the intended isolation and fix the actual address or port.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why network isolation is not authentication.

**Expected evidence:** Reachability policy and application identity answer different questions.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Define outbound acceptance for an offline worker.

**Expected evidence:** Prepared local computation succeeds and no external fetch is required.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose host-network mode used to hide a mapping error. Use its expected observation, Restore the intended isolation and fix the actual address or port., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/engine/network/drivers/none/)
- [Official reference 2](https://docs.docker.com/reference/compose-file/networks/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-019: Network isolation, gateways and outbound connectivity.
Read courses/docker/guides/docker-019.md and courses/docker/lessons/docker-019.md. Direct prerequisites: `docker-018`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
