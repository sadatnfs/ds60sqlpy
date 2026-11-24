# k8s-023: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Service provides an internal backend abstraction; an ingress or gateway controller can expose selected routes through a managed listener. Gateway API separates infrastructure ownership, listener configuration and application route attachment. Creating an HTTPRoute object does not install a controller or create a working external address.

This host lab requires a preinstalled qualified Gateway controller, a host-owned Gateway named lesson-gateway, an owned Service backend and a loopback-only listener. A synthetic TLS case also needs a verified local trust chain and hostname. The normal browser adapter provides none of those cluster/controller operations and does not accept Gateway or Ingress resources.

The real HTTPRoute example matches host lesson.example.test and path prefix /version, then forwards to `hello:8080`. It leaves other paths unmatched. The Ingress comparison is a separate fixture with its own ingressClassName; do not assume the two APIs are interpreted by the same controller or apply both to an unreviewed listener.

## Exercise 1: Draw the ownership layers

The layered design lets different roles own infrastructure and application routing. It also means a learner route manifest cannot create the missing controller or authorize itself to attach anywhere.

**Expected:** Controller/listener ownership is separated from the application route and backend.

**Solution reasoning**

- **Approach:** Mark each object's scope and manager, from GatewayClass down to Pods.
- **Why it is correct:** GatewayClass is cluster scoped and tied to a controller, the Gateway is the platform listener and the HTTPRoute, Service and Pods belong to the application.
- **Plausible wrong approach:** Drawing the HTTPRoute as owning the Gateway reverses the parentRefs direction, where the route attaches to the listener.
- **How to verify:** Each object shows scope and manager: controller, platform owner or application team.

## Exercise 2: Read matches and references

The route must be accepted by the intended parent and resolve its backend. Cross-namespace attachment/reference permissions are separate conditions, not implied by a familiar service name.

**Expected:** lesson.example.test, /version, lesson-gateway, hello 8080 are the declared contract.

**Solution reasoning**

- **Approach:** Read hostnames, matches path, parentRefs and backendRefs directly from the HTTPRoute.
- **Why it is correct:** These fields fully declare the route: lesson.example.test with prefix /version on lesson-gateway forwards to Service hello port 8080.
- **Plausible wrong approach:** Taking the backend port from the container port instead of backendRefs would cite 8080 by coincidence rather than from the route.
- **How to verify:** Four values are quoted from their fields.

## Exercise 3: Inspect current conditions

Stale or unrelated parent status can mislead a rollout review. The live packet should connect conditions to the requested generation and intended Gateway, then continue to a client check.

**Expected:** Current parent-specific conditions support configuration acceptance, not final delivery alone.

**Solution reasoning**

- **Approach:** Compare each parent's Accepted and ResolvedRefs observedGeneration with the route's generation.
- **Why it is correct:** Conditions are reported per parent, and only those at the current generation describe the current spec.
- **Plausible wrong approach:** Reading a True condition from an older generation would accept a route the controller has not yet seen.
- **How to verify:** Each condition's observedGeneration equals metadata.generation for its named parent.

## Exercise 4: Verify matching and unmatched requests

The pair tests the actual route selection rather than only a generic HTTP response. Record backend readiness and route identity so a default route cannot accidentally satisfy the positive case.

**Expected:** Expected version response on the match; documented no-route result on the negative path.

**Solution reasoning**

- **Approach:** Send /version and an unmatched path with Host lesson.example.test and record status and body.
- **Why it is correct:** Only requests matching hostname and prefix reach hello; others get the Gateway's no-route response.
- **Plausible wrong approach:** Omitting the Host header would fail both requests on hostname, hiding whether the path match works.
- **How to verify:** /version returns the expected version, and the unmatched path never reaches hello.

## Exercise 5: Verify synthetic TLS correctly

A request made with verification disabled would not prove the trust contract. The certificate is synthetic and host-owned; the normal worker receives no Secret or external-listener privilege.

**Expected:** Valid chain/hostname succeeds; wrong identity fails without an insecure bypass.

**Solution reasoning**

- **Approach:** Verify with the supplied CA and expected hostname, then repeat with a mismatched identity.
- **Why it is correct:** Certificate verification checks both chain and name, so the wrong identity must fail at the TLS layer.
- **Plausible wrong approach:** Passing an insecure flag makes the mismatch succeed and proves nothing about the certificate.
- **How to verify:** The valid case succeeds, and the wrong identity fails verification without bypass.

## Exercise 6: Compare Ingress and cleanup scope

The comparison should describe ownership and supported features rather than declaring one manifest a universal replacement. Preserve the host Gateway/controller unless its separate receipt authorizes lifecycle cleanup.

**Expected:** Qualified ingressClass/controller plus exact route cleanup; no assumption of API interchangeability.

**Solution reasoning**

- **Approach:** List what the Ingress fixture needs, an ingressClassName and its controller, and the exact route UIDs to clean up.
- **Why it is correct:** Ingress and Gateway are separate APIs served by separate controllers, so one being ready says nothing about the other.
- **Plausible wrong approach:** Converting the HTTPRoute fields into an Ingress and assuming the same behavior ignores differences such as path match types.
- **How to verify:** The list names class and controller, and cleanup cites exact UIDs.

## Boundary and troubleshooting review

A Kubernetes API object is not a running controller. An Ingress class or GatewayClass name must correspond to an installed, qualified implementation. A Service of type ClusterIP does not expose a host port by itself.

Keep listener ownership and cleanup separate from the namespaced route. The learner should remove only its recorded route UID unless the host capability explicitly owns the Gateway/controller lifecycle. Never disable TLS verification or install a remote controller automatically to make the example pass.
