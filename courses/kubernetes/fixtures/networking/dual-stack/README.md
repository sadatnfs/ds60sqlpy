# Optional complete dual-stack application fixture

This is a separate, manual teaching fixture for k8s-060. It does not modify the
ordinary IPv4-only course image or add a browser verifier operation. No source
file automatically starts Docker, creates a cluster or installs a CNI.

## What makes both address families work

The original `ds60sqlpy-k8s-fixture:0.2.0` server binds IPv4 only. This separate
server creates an `AF_INET6` socket and explicitly sets `IPV6_V6ONLY` to zero.
Inside its container it binds `::`, accepting IPv6 plus IPv4-mapped connections
on a capable Linux kernel. Missing dual-stack socket support is a clear startup
failure, never a silent IPv4 fallback. Running the script directly defaults to
IPv6 loopback `::1`; wildcard binding is selected explicitly by the image CMD.

Both families serve GET `/version` with HTTP 200 and the exact text
`ds60-dualstack-v1` followed by a newline. GET `/ready` returns `ready` plus a
newline. GET `/` intentionally returns 404. The client opens a socket in the
requested family, reads a bounded response with a three-second socket timeout,
and rejects a wrong status or payload. A successful IPv4 response cannot fill
the IPv6 result row.

## Required owned environment

An operator must separately prepare an explicitly owned disposable cluster
with IPv4/IPv6 node, Pod, Service and CNI routing, appropriate kernel support,
private kubeconfig/context/namespace receipt and UID-aware cleanup. The included
`kind-config.yaml` is a reviewed configuration example for that operator; it is
not permission to reconfigure an existing cluster or bypass the course's lease
preparation. Windows host work uses WSL 2 with a Linux engine. Desktop host API
access can stay on IPv4 loopback while the cluster supports both families.

The operator builds and preloads this local image into that exact owned target.
From this fixture directory, an explicitly prepared local engine can build it:

```sh
docker build --progress=plain -t ds60sqlpy-k8s-dualstack-study:0.1.0 .
```

The optional trusted mirror uses the build-only argument
`--build-arg DS60_PYTHON_IMAGE=mirror.gcr.io/library/python:3.12-slim` with TLS
verification retained. Nothing is pushed. The operator uses their exact owned
cluster identity when loading the image; do not infer it from an ambient context.
`workload.yaml` requests that prepared image with `imagePullPolicy: Never`.
It contains a non-root, read-only, bounded Deployment and a RequireDualStack
Service mapping 80 to the named app listener 8080.

Resource creation is a separately reviewed host operation. Bind the manifest
to the owned namespace, record each returned UID and retain the source hash.
Use the ownership-aware cleanup mechanism from that prepared session. A raw
name-only delete or broad namespace deletion is not supplied as a shortcut.

## Observe and test the real path

Use only the private receipt fields after the operator has retained the owned
resources for this host lab:

```sh
: "${LAB_KUBECONFIG:?Use the owned receipt path}"
: "${LAB_CONTEXT:?Use the owned receipt context}"
: "${LAB_NAMESPACE:?Use the owned receipt namespace}"
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get service dual-stack-study -o json
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get endpointslices -l kubernetes.io/service-name=dual-stack-study -o json
```

Record the actual IPv4 and IPv6 Service addresses, both families of current
endpoint identities, and the ready app Pod UID. The readiness probe may use only
one address family, so it cannot qualify both paths. The prepared in-cluster
client then runs the included `probe.py` with those literal Service addresses:

```sh
python /app/probe.py --ipv4 ACTUAL_OWNED_SERVICE_IPV4 --ipv6 ACTUAL_OWNED_SERVICE_IPV6 --port 80
```

The placeholders are not addresses to copy blindly. The command belongs inside
the separately prepared owned client container that can route to those Service
IPs. It is not a promise that the laptop can reach them. Expected JSON has two
passed rows, one IPv4 and one IPv6, each with version `ds60-dualstack-v1`.
A missing family, a refusal, a timeout or a wrong body fails the command.

Test Pod endpoints separately with port 8080 when diagnosing Service forwarding.
For DNS, inspect A and AAAA answers from the intended client and compare them
with actual Service addresses. DNS success, listener success and Service-path
success are separate evidence rows.

## Limits and cleanup

This source provides the missing IPv6-capable application and explicit client
mechanics. Static tests and native loopback checks do not qualify a cluster,
CNI, policy implementation or cloud load balancer. Record actual owned runtime
evidence separately. Stop the owned client, clean only the recorded object UIDs,
then release the prepared target through its lease workflow. Retain failure and
cleanup evidence without exporting private kubeconfigs or credentials.
