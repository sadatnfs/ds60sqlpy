# k8s-054: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

Gateway API separates infrastructure selection, traffic listeners and application routes into distinct resources. A GatewayClass describes a controller-managed class. A Gateway asks for listeners and an entrypoint. An HTTPRoute attaches routing rules to an allowed parent Gateway. This can separate platform responsibilities from application routing ownership.

The resources still require installed APIs and a compatible controller. Status conditions such as Accepted, Programmed and ResolvedRefs describe different aspects of reconciliation. A route being accepted does not prove an actual client request reached the expected application.

Cross-namespace references require deliberate authorization under the API’s rules. ReferenceGrant is one mechanism for allowing supported cross-namespace object references. It should be narrow, naming the intended kinds and relationships. Broad grants or permissive listener attachment can turn an organizational boundary into an accidental shared routing surface.

The fixture uses gateway.networking.k8s.io/v1 for Gateway and HTTPRoute. The exact supported route features depend on the installed controller and API version. Read parentRefs, listener names, hostnames and backendRefs field by field.

A platform team might own a shared Gateway while an application team owns an HTTPRoute in its namespace. The listener’s allowedRoutes policy controls which routes may attach. This is separate from whether the referenced backend exists and whether traffic succeeds.

## Exercise 1: Name the roles of class, gateway and route.

The separation makes ownership explicit. It does not eliminate the need for a controller.

**Expected:** Implementation class, listener/entrypoint and application routing intent.

**Solution reasoning**

- **Approach:** Map GatewayClass to the implementation, Gateway to listeners and HTTPRoute to application routing rules.
- **Why it is correct:** Each resource is meant for a different owner: platform, cluster operator and application team.
- **Plausible wrong approach:** Treating Gateway as the routing rule set merges listener ownership with route intent.
- **How to verify:** Class, gateway and route each get their role.

## Exercise 2: Predict a route with an unavailable parent.

A syntactically valid parentRef is not evidence that the parent exists or accepts the route.

**Expected:** It cannot establish the intended attached traffic path.

**Solution reasoning**

- **Approach:** Expect the route to stay detached when its parentRef names a missing or unavailable Gateway.
- **Why it is correct:** A route attaches only after a matching parent accepts it, so no traffic path is built.
- **Plausible wrong approach:** Assuming the rules apply once the route exists ignores the attachment step.
- **How to verify:** The prediction says the intended path is not established.

## Exercise 3: Design a route attachment boundary.

The platform should define who can attach routes rather than assuming every namespace may publish through a shared listener.

**Expected:** Listener allowedRoutes and route parentRef agree on intended ownership.

**Solution reasoning**

- **Approach:** Set the listener's allowedRoutes and the route's parentRef so both name the intended namespaces and kinds.
- **Why it is correct:** Attachment needs both sides to agree, which lets the Gateway owner limit who can bind to a listener.
- **Plausible wrong approach:** Allowing routes from all namespaces lets unrelated teams attach to the listener.
- **How to verify:** allowedRoutes and parentRef agree on the intended owner.

## Exercise 4: Diagnose ResolvedRefs=False.

Do not bypass the condition by granting broad cluster permissions. Repair the exact intended reference.

**Expected:** Inspect backend identity and required reference authorization.

**Solution reasoning**

- **Approach:** Read the condition's reason, then check backend names, kinds and any needed ReferenceGrant.
- **Why it is correct:** ResolvedRefs is false when a backend does not exist or a cross-namespace reference lacks authorization.
- **Plausible wrong approach:** Restarting the gateway controller does not create a missing backend or grant.
- **How to verify:** The diagnosis checks backend identity and reference authorization.

## Exercise 5: Explain a narrow cross-namespace grant.

The grant is an authorization relationship. Keep it as small as the application requirement.

**Expected:** Only the intended source kind/namespace can reference the intended target kind.

**Solution reasoning**

- **Approach:** Write a ReferenceGrant in the target namespace naming one source kind and namespace and one target kind.
- **Why it is correct:** The grant is opt-in and owned by the target namespace, so a narrow grant limits who can reference its objects.
- **Plausible wrong approach:** Granting all kinds or every namespace exposes more targets than the route needs.
- **How to verify:** Only the intended source can reference the intended target kind.

## Exercise 6: Plan Gateway acceptance evidence.

A complete claim follows configuration through data-plane behavior. Status alone is not an end-to-end test.

A useful counterexample is an accepted route whose backend reference remains unresolved. Attachment permission has passed, but the intended upstream still cannot be configured. Inspect the exact namespace, kind, name and port, then any required narrow ReferenceGrant. After correcting the reference, verify both its status and a real request with the intended hostname and path instead of assuming one condition implies every later stage.

**Expected:** API/controller support, conditions, listener reachability and expected app response.

**Solution reasoning**

- **Approach:** List API support, controller support, Accepted and ResolvedRefs conditions, a reachable listener and an app response.
- **Why it is correct:** Each item proves a different layer, from installed CRDs to a working backend.
- **Plausible wrong approach:** Stopping at an Accepted condition skips proof that requests reach the app.
- **How to verify:** The plan has evidence for every layer, ending with the expected response.
