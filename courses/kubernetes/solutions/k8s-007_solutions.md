# k8s-007: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Labels are key-value metadata used to select sets of objects. A Service uses a selector to identify backing Pods and provides a stable network abstraction over their changing identities. The Service object, its selected Pods and its EndpointSlices are separate resources whose relationships must be observed.

A ClusterIP Service does not publish an external address or prove that an application is healthy. Its port is the port clients use on the Service, while targetPort identifies the destination port on backing Pods. A named targetPort such as http resolves through the container port declaration. A mismatch can break traffic even when the Service object exists.

The current browser operation supports the fixed hello Deployment and hello Service. It checks Ready Pod UIDs, unique eligible EndpointSlice Pod UIDs and a new in-cluster version client, then cleans only owned resources. It deliberately permits a wrong selector value as a bounded negative case, which should fail to establish backends rather than silently succeed.

## Exercise 1: Trace selector equality

A selector is a set query over labels. It does not establish ownership by itself and it does not create missing Pods. The owned-controller UID check remains necessary after selection.

**Expected:** Matching selector finds the intended set; wrong selector has no intended backends.

## Exercise 2: Resolve the port chain

The chain connects client-facing and backend ports. A Service object can exist even if this mapping is wrong, so object creation alone is insufficient routing evidence.

**Expected:** Client8080 -> targetPort http -> container8080.

## Exercise 3: Count unique backends

Multiple slices or IP families can repeat a Pod identity. Set comparison avoids inflated backend counts and also detects an unrelated endpoint with the wrong UID.

**Expected:** Exactly two unique Pod UIDs matching the owned Ready set.

## Exercise 4: Run a selector negative case

The negative case tests the connection between selection and routing. A later successful Run is a fresh operation with its own UIDs, not evidence that the earlier Service persisted and was patched.

**Expected:** No matching ready backends; bounded failure and cleanup; restored source can pass separately.

## Exercise 5: Verify an independent client

The independent request establishes that the Service path reaches the expected fixture response. Job completion alone is tied to owned Pod identity and the fixed checker behavior; the result remains bounded to the observed request.

**Expected:** Job/Pod ownership and exit 0 accompany the expected ds60-fixture-v1 payload contract.

## Exercise 6: Design a second-Service transfer

Generalizing the mechanism requires a deliberate new resource scope, not changing the browser validator to accept arbitrary names. The same evidence chain applies, but actual execution remains unavailable until the host capability is provided.

**Expected:** A separate capability, unique owned resource receipt, selector/port/backend/client checks and UID-aware cleanup are specified.

## Boundary and troubleshooting review

A Service with no endpoints is different from a Service with ready endpoints but a wrong application response. A wrong selector is not repaired by changing the container image without evidence. A named-port mismatch is not a DNS failure. Record the discriminating field or client result before choosing a repair.

The browser source uses only its fixed port contract. Experiments with a second Service or arbitrary ports require a separate scoped host capability. Do not claim that the one-shot operation executed those transfer cases, or that finite client success proves long-term traffic availability.
