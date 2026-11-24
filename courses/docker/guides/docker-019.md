# docker-019: Network isolation, gateways and outbound connectivity

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-018`

## Learning objectives

Design a frontend/backend attachment table. Define outbound acceptance for an offline worker. Use network isolation, internal network and gateway accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A gateway forwards traffic beyond a local network. Docker bridge networking commonly uses routing and address translation for outbound traffic. The exact host rules depend on the engine and platform. Container traffic can reach external destinations unless its configuration and surrounding policy restrict it.

An internal network reduces external connectivity for its attached network. A service attached to both an external-facing and internal network can intentionally connect two application tiers, but this is not an automatic application firewall. Review the service’s role, listener ports and credentials.

Network mode none creates a container without ordinary external networking. This is useful for a pure computation that needs no DNS or HTTP. Host networking removes a major layer of network isolation and behaves differently across environments; it is not the beginner default or a repair for a wrong port mapping.

### Key terms

- **Gateway:** The router address that forwards a network's traffic to destinations beyond it.
- **Internal network:** A Docker network marked internal, which blocks external connectivity for the containers attached to it.
- **Outbound connectivity:** A container's ability to reach destinations outside its network, normally through routing and address translation.
- **Network mode none:** A setting that gives a container no ordinary external networking, suited to pure computation.
- **Host networking:** A mode where the container uses the host's network stack directly, removing a major layer of network isolation.

## Anatomy and a trace you can follow

Compose networks are named model objects. Services explicitly join the networks they require. A database can live only on `backend`, while an API joins `frontend` and `backend`. Marking `backend` internal should be tested from the actual callers and engine because host connectivity and DNS details are operational facts.

The fixture uses a single bridge for its first exercises. Sketch multi-tier designs before editing your copy. No chapter asks you to change host firewall rules, install a packet filter or disable existing security software.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-019.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Distinguish attachment from published ports.

**Hint:** Compare the networks key with the ports key.

### Exercise 2: Predict a pure computation with network none.

**Hint:** Ask whether the computation needs anything outside the container.

### Exercise 3: Design a frontend/backend attachment table.

**Expected evidence:** Each service joins only the networks needed by its role.

**Hint:** List which services must talk to each other.

### Exercise 4: Diagnose host-network mode used to hide a mapping error.

**Hint:** Undo host networking and test the original mapping hop by hop.

### Exercise 5: Explain why network isolation is not authentication.

**Hint:** Ask what a caller on the same network can still do.

### Exercise 6: Define outbound acceptance for an offline worker.

**Expected evidence:** Prepared local computation succeeds and no external fetch is required.

**Hint:** Run the worker with outbound access removed.

## Common mistakes and diagnosis

Switching to host networking to make a port problem disappear. Treating a private network as authentication. Attaching every service to every network.

Exercise 4 is this chapter's boundary case: Diagnose host-network mode used to hide a mapping error. Restore the bridge network, reproduce the original refusal and read the published mapping and listen address that host mode was hiding. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Predict the output of the computation under `--network none` and explain why no network was needed. Then reconstruct worked example 2 (Run a network-free computation) with one different value, predict what changes, and name which of network isolation, internal network, gateway and outbound connectivity the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [None network driver](https://docs.docker.com/engine/network/drivers/none/)
- [Compose file reference: networks](https://docs.docker.com/reference/compose-file/networks/)

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
