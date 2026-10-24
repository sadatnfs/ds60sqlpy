# k8s-054: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Gateway API separates infrastructure selection, traffic listeners and application routes into distinct resources. A GatewayClass describes a controller-managed class. A Gateway asks for listeners and an entrypoint. An HTTPRoute attaches routing rules to an allowed parent Gateway. This can separate platform responsibilities from application routing ownership.

The resources still require installed APIs and a compatible controller. Status conditions such as Accepted, Programmed and ResolvedRefs describe different aspects of reconciliation. A route being accepted does not prove an actual client request reached the expected application.

Cross-namespace references require deliberate authorization under the API’s rules. ReferenceGrant is one mechanism for allowing supported cross-namespace object references. It should be narrow, naming the intended kinds and relationships. Broad grants or permissive listener attachment can turn an organizational boundary into an accidental shared routing surface.

The fixture uses gateway.networking.k8s.io/v1 for Gateway and HTTPRoute. The exact supported route features depend on the installed controller and API version. Read parentRefs, listener names, hostnames and backendRefs field by field.

A platform team might own a shared Gateway while an application team owns an HTTPRoute in its namespace. The listener’s allowedRoutes policy controls which routes may attach. This is separate from whether the referenced backend exists and whether traffic succeeds.

## Exercise 1: Name the roles of class, gateway and route.

The separation makes ownership explicit. It does not eliminate the need for a controller.

**Expected:** Implementation class, listener/entrypoint and application routing intent.

## Exercise 2: Predict a route with an unavailable parent.

A syntactically valid parentRef is not evidence that the parent exists or accepts the route.

**Expected:** It cannot establish the intended attached traffic path.

## Exercise 3: Design a route attachment boundary.

The platform should define who can attach routes rather than assuming every namespace may publish through a shared listener.

**Expected:** Listener allowedRoutes and route parentRef agree on intended ownership.

## Exercise 4: Diagnose ResolvedRefs=False.

Do not bypass the condition by granting broad cluster permissions. Repair the exact intended reference.

**Expected:** Inspect backend identity and required reference authorization.

## Exercise 5: Explain a narrow cross-namespace grant.

The grant is an authorization relationship. Keep it as small as the application requirement.

**Expected:** Only the intended source kind/namespace can reference the intended target kind.

## Exercise 6: Plan Gateway acceptance evidence.

A complete claim follows configuration through data-plane behavior. Status alone is not an end-to-end test.

A useful counterexample is an accepted route whose backend reference remains unresolved. Attachment permission has passed, but the intended upstream still cannot be configured. Inspect the exact namespace, kind, name and port, then any required narrow ReferenceGrant. After correcting the reference, verify both its status and a real request with the intended hostname and path instead of assuming one condition implies every later stage.

**Expected:** API/controller support, conditions, listener reachability and expected app response.
