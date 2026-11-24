# spark-deploy-007: Repair driver DNS and callback routes

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-006`, `k8s-048`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Diagnose the callback path from the executor's location

`spark.driver.bindAddress` selects the driver's listening interfaces. `spark.driver.host` is the address advertised to other processes. The master URL is a third address. A correct master URL can allocate executors while an incorrect driver address makes the application fail afterward.

Compose supplies service-name DNS within its network. Use `driver` or `notebook` there. A host-published port is for a connection originating outside that network. The workshop never publishes master RPC or worker data ports to the host. A multi-host deployment needs actual routes and firewall rules for its advertised addresses, not a larger set of random public port mappings.

In this project the name `driver` comes from the Compose service's `hostname`. Its `SPARK_LOCAL_IP` sets the default bind address for Spark processes in that container; the submit call's `spark.driver.bindAddress=0.0.0.0` overrides it for the driver's listening sockets, as the Spark configuration reference states:

From [`projects/cluster-lab/compose.yaml`](../projects/cluster-lab/compose.yaml):

```yaml
driver:
  <<: *runtime
  hostname: driver
  environment:
    <<: *spark-environment
    SPARK_LOCAL_IP: driver
  command: [idle]
  mem_limit: 1536m
  cpus: 1
  pids_limit: 512
  volumes:
    - ./entrypoint.py:/lab/entrypoint.py:ro
    - ./jupyter_config.py:/lab/jupyter_config.py:ro
    - ./app:/lab/app:ro
    - ./conf:/lab/conf:ro
    - ${DS60_SPARK_STATE:?Missing workshop state}/events:/events
    - ${DS60_SPARK_STATE}/results:/results
  depends_on: [master, worker-a, worker-b]
```

## Key terms

- **Bind address:** The value of spark.driver.bindAddress, which selects the local interfaces the driver listens on.
- **Advertised address:** The value of spark.driver.host, which other processes use to call back to the driver.
- **Service-name DNS:** Compose name resolution, such as driver or notebook, that works only inside the shared network.
- **Callback path:** The connection an executor opens to the driver after allocation, which can fail even when the master URL is correct.
- **Published port:** A host mapping for connections that originate outside the network; master RPC and worker data ports are never published.

## Worked case A: trace the working two-way path

```text
driver resolves master -> connects to master:7077
worker launches executor -> executor resolves driver
executor connects to driver:39000
driver and executor exchange block data using their advertised block endpoints
```

Use the master UI to establish allocation, the executor inventory to establish registration, and a completed aggregate to establish usable data movement. Each observation answers a narrower question. An HTTP response from the driver UI says nothing about executor RPC permission. A TCP connection establishes a listener, not application protocol compatibility.

With fixed driver ports, firewall analysis can name driver RPC 39000 and driver block manager 39001. Executor block-manager ports also matter. They remain within the private Compose network here. For a restricted Kubernetes policy, deliberately configure the corresponding executor ports and allow the full Spark data flow, not only a one-way driver-to-executor connection.

## Worked case B: interpret an unreachable loopback advertisement

```text
master worker list: two live workers
driver host advertised to executors: 127.0.0.1
executor log: connection refused to 127.0.0.1:39000
driver HTTP UI: reachable from host
```

These observations are mutually consistent. Each executor's loopback belongs to its own network namespace. The minimal correction is a reachable advertised driver address with a matching listener, not publishing every port or setting an arbitrary longer timeout. Reproduce the failure only in an owned test, retain its diagnostic and restore the valid configuration before running acceptance.

## Worked example: flagging an advertisement that only works from the driver

```python
import ipaddress


def review(conf):
    host = conf["spark.driver.host"]
    bind = conf.get("spark.driver.bindAddress", host)
    findings = []
    try:
        address = ipaddress.ip_address(host)
        if address.is_loopback:
            findings.append("advertised loopback: each executor would call itself")
        elif address.is_private:
            findings.append("literal private IP: valid only if every executor can route to it")
    except ValueError:
        findings.append(f"name {host!r}: resolve it from an executor, not from the driver")
    if bind not in ("0.0.0.0", host):
        findings.append(f"bind {bind} may not listen on the interface behind {host}")
    return findings


print(review({"spark.driver.host": "driver", "spark.driver.bindAddress": "0.0.0.0"}))
print(review({"spark.driver.host": "127.0.0.1", "spark.driver.bindAddress": "0.0.0.0"}))
print(review({"spark.driver.host": "192.168.1.20", "spark.driver.bindAddress": "127.0.0.1"}))
```

Output from running the block above:

```text
["name 'driver': resolve it from an executor, not from the driver"]
['advertised loopback: each executor would call itself']
['literal private IP: valid only if every executor can route to it', 'bind 127.0.0.1 may not listen on the interface behind 192.168.1.20']
```

The three calls cover the configurations this chapter keeps returning to. The workshop pair, host `driver` with bind `0.0.0.0`, produces only a reminder: a service name is meaningful inside the Compose network, so the lookup that matters is the one an executor performs, not the one the driver performs on itself. The second call reproduces Worked case B, where `127.0.0.1` is advertised; every executor would dial its own loopback and get connection refused on 39000 even though the master happily allocated workers. The third call stacks two faults: a literal 192.168.1.20 advertisement that only works if every worker host routes to that LAN, plus a bind of 127.0.0.1 that would not accept connections arriving on that interface at all. The checker is deliberately static. It cannot prove reachability, and it never opens a socket, so its job is to stop an obviously wrong pair of settings before a submission wastes an allocation and leaves a confusing executor log behind.

## Worked example: testing name, route and listener from an executor container

```bash
PROJECT=OWNED_COMPOSE_PROJECT
docker compose -p "$PROJECT" exec -T worker-a getent hosts driver
docker compose -p "$PROJECT" exec -T worker-a python3 -c '
import socket
for port in (39000, 39001):
    try:
        socket.create_connection(("driver", port), timeout=3).close()
        print(port, "listener reachable from worker-a")
    except OSError as error:
        print(port, "failed:", error)
'
```

This sequence runs the diagnosis in the order the chapter recommends, but from worker-a, which is where the executor callback actually originates. `getent hosts driver` answers the name question using the same resolver the executor JVM would use. The inline Python then attempts TCP connections to 39000 and 39001, the fixed driver RPC and block manager ports, so a refusal on one and success on the other points at a single listener rather than at DNS. No output is printed here because it depends on a live Compose project that this page cannot run; `OWNED_COMPOSE_PROJECT` must be the project name that `lab.py` created, never a guess at someone else's stack. A connect from the host terminal would test a different network namespace entirely and could succeed while executors still fail. Keep the command, its origin container and the printed lines in the incident notes, then restore the valid configuration before acceptance if the probe was part of a deliberate failure rehearsal.

## Diagnose and transfer

Follow this order: name resolution, route, listener, policy, then protocol. DNS can return an address whose Service has no ready endpoints. A successful ping may bypass a blocked TCP port. NAT can make an advertised container address unreachable across machines. A remote notebook using a VPN may advertise a laptop interface that cluster nodes cannot route to.

Prefer running the driver inside the cluster's network boundary when client reachability is difficult. A port-forward is excellent for a local browser inspecting HTTP, but is not generally a replacement for all distributed executor callbacks. Record the origin and destination for every test so a host-side success is not mistaken for an executor-side success.

## Primary references

- [Spark driver and block-manager settings](https://spark.apache.org/docs/4.0.1/configuration.html)
- [Kubernetes client-mode networking](https://spark.apache.org/docs/4.0.1/running-on-kubernetes.html#client-mode-networking)
