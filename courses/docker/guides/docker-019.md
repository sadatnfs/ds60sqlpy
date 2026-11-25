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

The classroom saves `courses/docker/lessons/docker-019.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Create a scratch internal network with `docker network create --internal ds60-internal-demo`. Run `docker run --rm --pull never --network ds60-internal-demo ds60-docker-study:local cat /proc/net/route` and compare it with `docker compose -p ds60-docker-study exec app cat /proc/net/route` from the running project. The project container has a row whose destination is `00000000`, its default route through the network gateway; the internal network gives a subnet route and no default route, so traffic for any other address has nowhere to go. Then run worked example 2 and add `cat /proc/net/dev` to see that `--network none` leaves only the loopback interface. No request leaves the machine during this lab. Remove the scratch network with `docker network rm ds60-internal-demo`.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose host-network mode used to hide a mapping error. Restore the bridge network, reproduce the original refusal and read the published mapping and listen address that host mode was hiding.

Network isolation limits sockets, not every data path. A worker started with `--network none` can still read and change any volume or bind mount it receives, and whatever it writes to stdout is kept in the container log for anyone who can run `docker logs`. So an offline job that mounts a broad host directory is not contained just because it cannot open connections. When you review an isolated service, list its mounts, its output destinations and its environment alongside its networks, and give it only the paths its task needs, read-only where it only reads.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Predict the output of the computation under `--network none` and explain why no network was needed.

**Transfer case.** A worker must call an API on the internal `backend` network and must never reach the internet. A teammate attaches it to both `backend` and the non-internal `frontend` network so it starts faster. Evaluate the change and state an acceptance check.

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
