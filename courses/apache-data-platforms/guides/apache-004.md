# apache-004: Processes, networks and ownership

Tutorial mode. Stage: beginner. Direct prerequisites: `apache-003`.

## Localhost belongs to the process's network namespace

A client connects to a listener through an address, port and protocol. Before that
connection succeeds, it may need a DNS lookup, network route and protocol handshake.
Each layer can fail independently. A container normally has its own network
namespace, so its loopback address refers to that container, not to the host and
not to a neighboring service. Two processes can both use port 8815 in different
namespaces without referring to the same listener.

Compose supplies service-name discovery on a project network. A client in that
network can resolve server to the current container address and use the server's
container port. A host browser cannot generally resolve that private service name.
Publishing a host port creates a separate access path with its own host address
and port; it does not change what localhost means inside another container.
Hardcoding a current container IP is fragile because replacement can change it.

The worked notebook uses the real Arrow Flight workshop. It starts one bounded
server and a short-lived client on a private network. There is no published host
port and no Docker socket inside either service. These are actual network and
RPC observations, not an in-memory imitation of Compose DNS or a mocked service.
The main classroom browser continues to use its own separate application URL.

## Worked case A: service discovery reaches the right process

After copying the project and preparing the declared local image, start the owned
workshop and run network-check. The client calls the real container resolver for
server, connects to its Flight listener, retrieves the three logical rows carried in
record batches and validates the independent fixture oracle. The diagnostic reports the
addresses it actually observed; do not copy those transient addresses into a
maintained configuration.

A successful DNS lookup alone would not prove the listener is healthy. The server
could be stopped, listening on a different interface, using another protocol or
rejecting the request. This check therefore proceeds through the full protocol
read and exact semantic validation. The expected total for east is 11 and the
fixture contains exactly orders 1, 2 and 3.

The endpoint name is stable within this owned Compose project, but an existing
connection can still break when the server is replaced. A resilient client needs
bounded reconnect behavior and must resolve the service again. A stable DNS name
is a discovery contract, not a guarantee that one TCP connection remains valid
forever.

## Worked case B: the client loopback cannot reach its neighbor

The same client then tries 127.0.0.1 on port 8815 with a one-second Flight deadline.
That address names the short-lived client container. Because it has no Flight
server listening there, the request must fail with an unavailable or timeout
condition. The checker treats success as a failure of this diagnostic, rather
than silently accepting any endpoint that happens to return data.

This negative case is intentionally narrow. A container sharing another process's
network namespace or using host networking would have different semantics. The
provided Compose topology uses separate ordinary containers on a private project
network, which is the condition under test. Do not generalize its exact addresses
to every possible Docker networking mode.

A host connection to localhost would be a third path and is not enabled here.
Exposing this unauthenticated teaching service publicly would change its security
boundary. If a separate application needs host access, it must explicitly bind a
loopback host port and configure the server's advertised endpoints consistently.
Opening arbitrary ports is not a repair for an incorrect service URL.

## Diagnosis and interview discussion

Follow DNS, route, listener, handshake and application result in that order.
Inspect the namespace where a command actually runs. Keep network ownership,
service health and persisted data separate: a healthy network cannot recover a
deleted volume, and retained data cannot make a stopped single server available.
Use the workshop's status and bounded logs commands before changing configuration.

**Interview discussion: why does localhost work in a container healthcheck but
fail in another container's client?** The healthcheck runs in the server's own
namespace, while the client loopback names itself. The two cases observe both
paths on the real topology and connect the address distinction to an actual
successful read and a bounded expected failure.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Actual namespace and Flight observations

From the repository root, copy the complete project into a fresh owned location.
Prepare the native `data-platforms-python` image as documented in its README.

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/arrow-flight work/arrow-flight
cd work/arrow-flight
bash run.sh start
bash run.sh network-check
```

The result must report actual service DNS addresses, `service_dns_read_passed:true`
and `client_loopback_rejected:true`. Addresses are observations, not stable config.

```bash
bash run.sh status
bash run.sh logs
bash run.sh stop
bash run.sh resume
bash run.sh network-check
```

Use the project README for down, retained-state replacement and explicitly
confirmed deletion. Do not run service commands in a classroom pad.

## Primary references

- [Docker Compose networking](https://docs.docker.com/compose/how-tos/networking/)
- [Arrow Flight protocol](https://arrow.apache.org/docs/format/Flight.html)
