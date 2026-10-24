# Deep networking fixtures and owned host-lab boundary

These are original synthetic teaching inputs for k8s-043 through k8s-066. They are not a saved cluster observation. No file contains a real kubeconfig, credential, cloud endpoint or public certificate. Addresses in topology.json are examples only. Do not contact them.

## What is maintained here

- `topology.json`: distinct node, Pod and Service ranges; two endpoint identities; explicit readiness; three policy cases.
- `deployment.yaml` and `service.yaml`: a non-root bounded app and ClusterIP mapping from 80 to named port 8080, using the separately preloaded course fixture image.
- `headless.yaml`: direct Pod discovery without an ordinary ClusterIP. A/AAAA clients connect to the actual endpoint port 8080; there is no Service port 80 to 8080 proxy translation.
- `network-policy.yaml`: an AND relationship between namespace and Pod selectors for ingress to 8080.
- `ingress.yaml`: a manual HTTP route requiring an explicitly prepared IngressClass called study-controller.
- `gateway.yaml`: Gateway and HTTPRoute requiring the APIs and a compatible GatewayClass called study-controller.
- `dual-stack-service.yaml`: API intent requiring a dual-stack-capable cluster. The supplied app server binds IPv4 only, so IPv6 traffic additionally requires a separately reviewed IPv6/dual-stack listener and client.
- `lesson-inventory.json`: reading-only lesson coverage and capability boundaries, not runtime receipts.

Run the static checker from the repository root with the already prepared Python authoring environment:

```sh
python courses/kubernetes/fixtures/networking/check_fixtures.py
```

It performs no API calls, network access, installations or Docker operations. It checks CIDR separation, address membership, node references, label matching, target-port resolution, ready endpoint identity, AND-selector cases and manifest structure. A pass proves consistency of these supplied examples only. It does not prove a CNI enforces policy or an external controller serves traffic.

## Before any optional live work

A teacher or operator must separately prepare an owned disposable target using the repository's documented lease/ownership route and record exact private kubeconfig path, context, namespace, expiry and permitted capabilities. Windows uses Bash in WSL 2. Never inherit an ambient current-context. Never point these manifests at a workplace, shared or production cluster.

The ordinary browser adapter admits only its reviewed operations. These advanced manifests are not a request to broaden that allowlist. A missing API, controller, CNI policy implementation or dual-stack capability is reported as unavailable. Do not install it or change cluster networking merely because a lesson references it.

The controller class names are deliberate placeholders for a separately prepared capability. A class named study-controller must actually exist and be owned for the host lab before those files can be used. No cloud load balancer is created by default. The hostname study.example.test is a reserved teaching name, not public DNS you should expect to resolve.

## Field-level observations

After the owned session is prepared and its retained resources actually exist, these are scoped reads:

```sh
: "${LAB_KUBECONFIG:?Use the private path from the owned receipt}"
: "${LAB_CONTEXT:?Use the exact context from the owned receipt}"
: "${LAB_NAMESPACE:?Use the namespace from the owned receipt}"
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get service network-study -o yaml
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get pods -l app=network-study -o wide
kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" --namespace "$LAB_NAMESPACE" get endpointslices -l kubernetes.io/service-name=network-study -o yaml
```

Record Service UID, actual assigned IPs, all relevant slices, target Pod UIDs, ready conditions and resolved port. Do not assume the synthetic topology addresses were allocated. A one-shot browser Run already cleaned its objects and cannot be reused as an unbounded host session.

## Capability-specific acceptance

| Capability | Additional prepared requirement | Actual evidence needed |
| --- | --- | --- |
| Internal Service | Owned app and Service, preloaded fixture image, working CNI/DNS | Current endpoint identities plus fresh request from the intended caller |
| NetworkPolicy | Named enforcing CNI and two owned caller cases | Allowed request succeeds and denied request fails; object creation alone is insufficient |
| Ingress | Prepared controller/class and a scoped external entrypoint | Matching host/path request reaches the current app revision |
| Gateway API | Installed compatible APIs/controller/class | Relevant conditions plus actual listener and route request |
| TLS | Deliberately prepared public teaching certificate and scoped trust | Correct name/chain validation without exposing private keys |
| Dual-stack | Actual IPv4/IPv6 cluster and CNI support plus a separately reviewed dual-stack app listener/client; supplied app is IPv4-only | Family-specific DNS, endpoints, routing and application responses |
| Topology/locality | Prepared multi-node/zone topology and supported policy | Caller placement, selected endpoint and failure behavior |

## Cleanup and state

The host-lab operator records every created object's UID before testing. Cleanup must use the reviewed lease mechanism and compare ownership/UID before deletion. Names alone are insufficient because an object may have been replaced. Do not delete a namespace or run a broad label deletion from this README. The study manifests have labels for identification, not authority to delete every matching object.

Preserve bounded failure evidence and the cleanup result separately. Keep private runtime receipts and credentials outside source and portable learner exports. A completed design worksheet is useful learning evidence; label actual runtime acceptance only after the corresponding capability was exercised.

## Policy and endpoint interpretation

A podSelector-only policy peer selects Pods in the policy’s own namespace.
A namespaceSelector-only peer selects all Pods in matching namespaces. Both
selectors in one peer combine as AND; separate peers combine as alternatives.
A Pod-to-Pod connection must satisfy source egress and destination ingress when
each is isolated. Reply traffic for an allowed connection is implicitly allowed;
that does not allow an unrelated new reverse connection. The synthetic cases
include an egress-blocked caller even though its destination ingress labels match.

Headless discovery returns individual Pod destinations and does not provide an
ordinary Service port translation. Inspect EndpointSlice ports or actual SRV
answers, and connect to the target listener. Do not assume the manifest’s
Service port 80 is a proxy endpoint for this headless 8080 server.

## Exact successful application requests

The original IPv4 fixture serves GET `/version` with HTTP 200 and exact text
`ds60-fixture-v1` plus a newline; GET `/ready` returns `ready` plus a newline.
GET `/` returns 404 by design. An Ingress/Gateway Prefix rule for `/` forwards
`/version` as `/version` unless a separately documented rewrite is configured.
Use `/version` for the positive application acceptance request. A correctly
routed root404 is not evidence that the network failed.

For the ordinary ClusterIP fixture, an in-cluster client requests
`http://network-study:80/version`. For the headless fixture, A/AAAA resolution
returns Pod addresses and the client connects to the actual listener 8080, for
example `http://network-study-headless:8080/version` with an appropriate client
selection policy. SRV-aware clients inspect `_http._tcp.network-study-headless`
within the actual namespace/domain and honor each returned target and port;
A/AAAA-only clients do not receive a port from DNS. There is no headless
Service port 80 to 8080 proxy translation.

The [separate dual-stack application](dual-stack/README.md) supplies an actual
IPv6-capable listener and family-specific bounded client, alongside explicit
cluster prerequisites and its own image identity. It remains manual-only and
does not change the original admitted IPv4 verifier contract.
