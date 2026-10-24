# k8s-023: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Service provides an internal backend abstraction; an ingress or gateway controller can expose selected routes through a managed listener. Gateway API separates infrastructure ownership, listener configuration and application route attachment. Creating an HTTPRoute object does not install a controller or create a working external address.

This host lab requires a preinstalled qualified Gateway controller, a host-owned Gateway named lesson-gateway, an owned Service backend and a loopback-only listener. A synthetic TLS case also needs a verified local trust chain and hostname. The normal browser adapter provides none of those cluster/controller operations and does not accept Gateway or Ingress resources.

The real HTTPRoute example matches host lesson.local and path prefix /version, then forwards to hello:8080. It leaves other paths unmatched. The Ingress comparison is a separate fixture with its own ingressClassName; do not assume the two APIs are interpreted by the same controller or apply both to an unreviewed listener.

## Exercise 1: Draw the ownership layers

The layered design lets different roles own infrastructure and application routing. It also means a learner route manifest cannot create the missing controller or authorize itself to attach anywhere.

**Expected:** Controller/listener ownership is separated from the application route and backend.

## Exercise 2: Read matches and references

The route must be accepted by the intended parent and resolve its backend. Cross-namespace attachment/reference permissions are separate conditions, not implied by a familiar service name.

**Expected:** lesson.local, /version, lesson-gateway, hello8080 are the declared contract.

## Exercise 3: Inspect current conditions

Stale or unrelated parent status can mislead a rollout review. The live packet should connect conditions to the requested generation and intended Gateway, then continue to a client check.

**Expected:** Current parent-specific conditions support configuration acceptance, not final delivery alone.

## Exercise 4: Verify matching and unmatched requests

The pair tests the actual route selection rather than only a generic HTTP response. Record backend readiness and route identity so a default route cannot accidentally satisfy the positive case.

**Expected:** Expected version response on the match; documented no-route result on the negative path.

## Exercise 5: Verify synthetic TLS correctly

A request made with verification disabled would not prove the trust contract. The certificate is synthetic and host-owned; the normal worker receives no Secret or external-listener privilege.

**Expected:** Valid chain/hostname succeeds; wrong identity fails without an insecure bypass.

## Exercise 6: Compare Ingress and cleanup scope

The comparison should describe ownership and supported features rather than declaring one manifest a universal replacement. Preserve the host Gateway/controller unless its separate receipt authorizes lifecycle cleanup.

**Expected:** Qualified ingressClass/controller plus exact route cleanup; no assumption of API interchangeability.

## Boundary and troubleshooting review

A Kubernetes API object is not a running controller. An Ingress class or GatewayClass name must correspond to an installed, qualified implementation. A Service of type ClusterIP does not expose a host port by itself.

Keep listener ownership and cleanup separate from the namespaced route. The learner should remove only its recorded route UID unless the host capability explicitly owns the Gateway/controller lifecycle. Never disable TLS verification or install a remote controller automatically to make the example pass.
