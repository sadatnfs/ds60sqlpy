# k8s-029: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

An API resource is a typed collection of objects, not necessarily a running process. A CustomResourceDefinition, abbreviated CRD, registers a new resource type with the API server. A custom resource is one instance of that type. Here the cluster-scoped registration is `lessonreports.learning.ds60sqlpy`, while hello-report is a namespaced LessonReport instance. Registering a schema does not install an operator or create a Deployment automatically.

The synthetic API describes a report application with message and replicas. A structural schema gives the server a typed shape it can validate and use for other API machinery. Our spec.message is one of two strings and spec.replicas is an integer from 1 through 2. These are deliberate course limits, not a generic configuration format. A desired instance can be valid yet remain unimplemented when no qualified controller observes it.

The normal module credential cannot register CRDs or create arbitrary custom resources. The live extension requires a separately provisioned advanced lease. Start by inspecting the complete registration in the linked fixture and the namespaced instance in the solution. Keep API registration, instance acceptance and application convergence as three separate evidence rows.

## Exercise 1: Map the two scopes

The registration changes the API surface for the cluster. A namespaced instance is addressed under its own namespace. This difference explains why ordinary worker credentials cannot safely install a CRD as part of a learner submission.

**Expected:** CRD is cluster-scoped; hello-report is namespaced.

**Solution reasoning**

- **Approach:** Read spec.scope in the CRD and metadata.namespace in the instance.
- **Why it is correct:** A CustomResourceDefinition is itself cluster scoped, while its scope field decides that LessonReport instances live in namespaces.
- **Plausible wrong approach:** Assuming the CRD is namespaced because its instances are confuses the registration with the objects it registers.
- **How to verify:** CRD is cluster scoped, and hello-report has a namespace.

## Exercise 2: Trace names and version

The mapping determines API discovery and object addressing. A typo in the kind or API version can fail before schema validation, while a different metadata.name creates a different instance rather than changing its type.

**Expected:** learning.ds60sqlpy/v1, LessonReport, `lessonreports` and hello-report are distinct fields.

**Solution reasoning**

- **Approach:** Find each value in spec.group, spec.versions name, spec.names.kind, spec.names.plural and the instance metadata.name.
- **Why it is correct:** Group and version form the API path, kind is the type in YAML, plural is the URL segment and metadata.name names one object.
- **Plausible wrong approach:** Using the kind LessonReport in a URL instead of the plural lesson reports addresses a resource that does not exist.
- **How to verify:** Five values come from five distinct fields.

## Exercise 3: Predict schema negatives

The valid object satisfies every constraint. A numeric-looking string is still the wrong type, 3 exceeds maximum 2, and absence of message violates required. These produce specific, explainable controls rather than one generic invalid example.

**Expected:** Only integer 1 with a present allowed message passes the stated complete spec.

**Solution reasoning**

- **Approach:** Check each candidate against required, type and range separately.
- **Why it is correct:** Structural schemas reject a string where an integer is required, a value outside the range and a missing required field.
- **Plausible wrong approach:** Expecting string 2 to be coerced to an integer assumes conversion the API server does not perform.
- **How to verify:** Only integer 1 with an allowed message passes.

## Exercise 4: Inspect unknown-field handling

Pruning can remove an unknown key while leaving an object that differs from the author intention. Strict validation may reject it instead. Either outcome should be documented, and the offline subset checker cannot establish that server behavior.

**Expected:** Record validation mode and actual rejection or pruning; do not assume silently stored intent.

**Solution reasoning**

- **Approach:** Send the replcias typo with a named field validation mode and read the object back.
- **Why it is correct:** Depending on the mode, the server rejects the unknown field or prunes it, and in neither case is replicas set.
- **Plausible wrong approach:** Assuming the typo was stored as intent because the request succeeded ignores pruning.
- **How to verify:** The readback is compared with the request, and the validation mode is recorded.

## Exercise 5: Separate status from intent

Status may still describe a previously successful configuration. A meaningful readiness gate joins the observed generation with child and application evidence rather than accepting a boolean without its temporal context.

**Expected:** Current generation 7 is not yet proven reconciled by that status.

**Solution reasoning**

- **Approach:** Compare metadata.generation 7 with status.observedGeneration 6 before reading ready.
- **Why it is correct:** The status describes generation 6, so ready true says nothing yet about the spec at generation 7.
- **Plausible wrong approach:** Accepting ready true as current trusts a status that predates the latest change.
- **How to verify:** Generation 7 is reported as not yet reconciled.

## Exercise 6: Plan scoped teardown

The advanced lease owner should confirm controller/finalizer completion before deregistering the type. The handoff retains exact object identities and does not use registration deletion as a shortcut to bypass stuck resource cleanup.

**Expected:** Instance UID cleanup is separate from CRD removal; no learner privilege widening.

**Solution reasoning**

- **Approach:** Separate instance deletion by name and UID from CRD removal as a host operation.
- **Why it is correct:** Deleting the CRD deletes every instance of that type cluster wide, which exceeds learner scope.
- **Plausible wrong approach:** Running kubectl delete crd to clean up after one instance removes all LessonReports everywhere.
- **How to verify:** Learner steps touch only the instance, and CRD removal is listed as a host step.

## Boundary and troubleshooting review

A no-matches-for-kind error suggests registration or discovery/version trouble. Forbidden suggests credentials lack authorization. A schema validation error should name a field and constraint. An accepted instance with no child workload suggests missing or failing reconciliation. Those errors require different repairs.

Do not grant the learner cluster-admin to make the example work. The host owns registration and the lease must provide only the intended namespaced instance operations. Removing a CRD can remove its stored custom resources, so registration cleanup is a separate host responsibility after instance/controller cleanup.
