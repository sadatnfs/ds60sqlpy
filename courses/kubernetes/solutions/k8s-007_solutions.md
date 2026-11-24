# k8s-007: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Labels are key-value metadata used to select sets of objects. A Service uses a selector to identify backing Pods and provides a stable network abstraction over their changing identities. The Service object, its selected Pods and its EndpointSlices are separate resources whose relationships must be observed.

A ClusterIP Service does not publish an external address or prove that an application is healthy. Its port is the port clients use on the Service, while targetPort identifies the destination port on backing Pods. A named targetPort such as http resolves through the container port declaration. A mismatch can break traffic even when the Service object exists.

The current browser operation supports the fixed hello Deployment and hello Service. It checks Ready Pod UIDs, unique eligible EndpointSlice Pod UIDs and a new in-cluster version client, then cleans only owned resources. It deliberately permits a wrong selector value as a bounded negative case, which should fail to establish backends rather than silently succeed.

## Exercise 1: Trace selector equality

A selector is a set query over labels. It does not establish ownership by itself and it does not create missing Pods. The owned-controller UID check remains necessary after selection.

**Expected:** Matching selector finds the intended set; wrong selector has no intended backends.

**Solution reasoning**

- **Approach:** Compare each key and value in the Service spec.selector with the labels in the Deployment Pod template, treating the selector as a set query.
- **Why it is correct:** A Service selects every Pod in its namespace whose labels contain all selector pairs, so app=hello matches the template label and app=wrong matches nothing in this manifest.
- **Plausible wrong approach:** Checking only that a Service named hello exists misses the selector entirely; the object is accepted with app=wrong and simply has zero endpoints.
- **How to verify:** Key and value agree exactly for app=hello; for app=wrong the value differs, so the intended set is empty.

## Exercise 2: Resolve the port chain

The chain connects client-facing and backend ports. A Service object can exist even if this mapping is wrong, so object creation alone is insufficient routing evidence.

**Expected:** Client 8080 -> targetPort http -> container 8080.

**Solution reasoning**

- **Approach:** Follow the chain from the Service port to targetPort, then resolve the name `http` against the container ports list.
- **Why it is correct:** A string targetPort is looked up by name on each selected container, and this container declares `http` once as containerPort 8080.
- **Plausible wrong approach:** Assuming targetPort must equal port numerically would break as soon as the Service port changes, and a misspelled port name still creates a valid Service that routes nowhere.
- **How to verify:** The chain reads 8080 to `http` to 8080, and `http` appears exactly once in the container ports list.

## Exercise 3: Count unique backends

Multiple slices or IP families can repeat a Pod identity. Set comparison avoids inflated backend counts and also detects an unrelated endpoint with the wrong UID.

**Expected:** Exactly two unique Pod UIDs matching the owned Ready set.

**Solution reasoning**

- **Approach:** Collect every targetRef.uid from the four EndpointSlice entries and reduce them to a set before comparing with the owned Ready Pods.
- **Why it is correct:** The same Pod can appear in more than one slice or once per IP family, so only distinct UIDs measure distinct backends.
- **Plausible wrong approach:** Counting endpoint rows reports four backends and would also hide a foreign UID among them.
- **How to verify:** The set holds exactly two UIDs, and it equals the owned Ready Pod UIDs recorded independently.

## Exercise 4: Run a selector negative case

The negative case tests the connection between selection and routing. A later successful Run is a fresh operation with its own UIDs, not evidence that the earlier Service persisted and was patched.

**Expected:** The unchanged starter has no matching ready backends and fails within its bound, with cleanup; the restored source can pass in a separate Run.

**Solution reasoning**

- **Approach:** Run the starter with selector app=wrong unchanged, keep its failure record, then restore app=hello and submit a separate Run.
- **Why it is correct:** No Pod carries app=wrong, so the Service never gains a ready endpoint and the bounded backend check fails before the client step.
- **Plausible wrong approach:** Editing the selector and rerunning without first recording the failure loses the negative evidence, and treating the second Run as a patch of the first ignores that each Run creates and deletes its own Service.
- **How to verify:** The record shows the exact app=wrong selector, the failed check name and cleanup, then a separate passing Run with new UIDs.

## Exercise 5: Verify an independent client

The independent request establishes that the Service path reaches the expected fixture response. Job completion alone is tied to owned Pod identity and the fixed checker behavior; the result remains bounded to the observed request.

**Expected:** Job/Pod ownership and exit 0 accompany the expected ds60-fixture-v1 payload contract.

**Solution reasoning**

- **Approach:** Check that the client Job's UID belongs to this Run, then compare its output with the `/version` payload contract.
- **Why it is correct:** The client Pod resolves the Service name and receives the fixture response only if selector, port chain and readiness all line up.
- **Plausible wrong approach:** Accepting Job completion alone would pass a client that called `/ready`, which proves probe health, not the version payload.
- **How to verify:** Job and Pod ownership match this Run, exit status is 0 and the output equals ds60-fixture-v1.

## Exercise 6: Design a second-Service transfer

Generalizing the mechanism requires a deliberate new resource scope, not changing the browser validator to accept arbitrary names. The same evidence chain applies, but actual execution remains unavailable until the host capability is provided.

**Expected:** A separate capability, unique owned resource receipt, selector/port/backend/client checks and UID-aware cleanup are specified.

**Solution reasoning**

- **Approach:** Specify a new Service name with its own receipt and repeat the selector, port, backend and client checks against that object only.
- **Why it is correct:** A distinct owned receipt and UID-aware cleanup keep the experiment from mutating the shared `hello` Service or another learner's objects.
- **Plausible wrong approach:** Editing the hello Service selector in place to test the idea would change the baseline other checks depend on and cannot be undone by UID.
- **How to verify:** The design names its own Service, its own receipt and a UID-scoped delete, and never edits hello.

## Boundary and troubleshooting review

A Service with no endpoints is different from a Service with ready endpoints but a wrong application response. A wrong selector is not repaired by changing the container image without evidence. A named-port mismatch is not a DNS failure. Record the discriminating field or client result before choosing a repair.

The browser source uses only its fixed port contract. Experiments with a second Service or arbitrary ports require a separate scoped host capability. Do not claim that the one-shot operation executed those transfer cases, or that finite client success proves long-term traffic availability.
