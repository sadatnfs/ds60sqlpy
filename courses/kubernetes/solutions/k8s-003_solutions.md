# k8s-003: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/k8s-003.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

A Kubernetes manifest describes a typed API request. `apiVersion` chooses a resource API version; `kind` chooses the object type; metadata names and labels the object. For a Deployment, spec expresses desired state, including replica count and a Pod template. Status is an observed server/controller report, not a field to invent in the learner source.

YAML indentation defines nesting. A number such as replicas:1 must be a number, not a quoted string. The Deployment selector must match the Pod-template labels. Some API kinds, such as ConfigMap, use data rather than spec: do not force every object into a memorized shape. The source intentionally omits namespace so the reviewed operation binds it from a valid owned lease. It may not use current-context, accept an arbitrary host target or silently broaden credentials. [Deployment concepts](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) explain the desired-state structure.

- **apiVersion:** the API group/version for a resource type
- **kind:** the requested resource category
- **metadata:** name, labels and server-assigned identity fields
- **spec:** desired state for objects such as Deployments
- **status:** server/controller observation, requiring readback

## Worked example / walkthrough

### Worked example 1: Read a small ConfigMap

This is a reading example; the lesson operation must explicitly allow the kind before any apply.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: vocabulary
data:
  label: learner
```

**Expected:** name vocabulary;one data string; no spec or status is required for this kind.

### Worked example 2: Reject the wrong replica type

The snippet is deliberately incomplete and invalid; do not apply it hoping to create a workload. Separate a YAML parse from API-schema acceptance.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: invalid-example
spec:
  replicas: "two"
```

**Expected:** A schema-aware API validation rejects the string where an integer is required.

## Exercises and explanatory solutions

### Exercise 1: Read the request envelope

**Inputs/evidence:** For k8s-003 Exercise 1, the complete hello Deployment learner source.

**Expected result/shape:** For k8s-003 Exercise 1, apps/v1,Deployment,hello.

**Verify:** For k8s-003 Exercise 1, read the three exact fields at their declared levels.

These fields identify what API object is requested. They do not establish current replica health or authorize a target cluster.

### Exercise 2: Validate a numeric field

**Inputs/evidence:** For k8s-003 Exercise 2, one valid number and one invalid string.

**Expected result/shape:** For k8s-003 Exercise 2, numeric1 is the intended request; the string is rejected by schema validation.

**Verify:** For k8s-003 Exercise 2, retain the validation phase/result and do not claim a rejected object has a new UID.

A generic YAML parser can accept both scalar values. Kubernetes schema validation adds the typed field requirement, which is why parse success alone is insufficient.

### Exercise 3: Trace selector and template labels

**Inputs/evidence:** For k8s-003 Exercise 3, selector app:hello and template label app:hello.

**Expected result/shape:** For k8s-003 Exercise 3, the key/value pairs agree; app:wrong would violate the intended controller/template relation.

**Verify:** For k8s-003 Exercise 3, compare the exact pair on both sides.

Selectors express membership; matching only the key while changing the value is not enough. This controller relation is separate from a later Service selector.

### Exercise 4: Bind only the owned namespace

**Inputs/evidence:** For k8s-003 Exercise 4, source omits namespace;private lease specifies lesson-a with verified UID.

**Expected result/shape:** For k8s-003 Exercise 4, the reviewed operation binds lesson-a; no ambient fallback or source namespace escape.

**Verify:** For k8s-003 Exercise 4, inspect the bound request and receipt; refuse when the lease is absent.

Omission is deliberate in this workflow. It delegates target binding to the typed operation, not to a kubectl default namespace or an arbitrary browser field.

### Exercise 5: Separate intent from observation

**Inputs/evidence:** For k8s-003 Exercise 5, desired1,observed ready0.

**Expected result/shape:** For k8s-003 Exercise 5, the request can be accepted while readiness is not established.

**Verify:** For k8s-003 Exercise 5, record generation/observedGeneration and readiness after bounded reconciliation; do not edit status into the source.

A controller observes and acts after the request. API acceptance and application readiness answer different questions, so preserve both rather than declaring success early.

### Exercise 6: Verify server identity and safe cleanup

**Inputs/evidence:** For k8s-003 Exercise 6, name hello,namespace from lease,server-assigned UID.

**Expected result/shape:** For k8s-003 Exercise 6, namespace matches the lease; UID is recorded from readback and used for owned cleanup.

**Verify:** For k8s-003 Exercise 6, check actual returned identity; never fabricate a fixed UID from this document.

UIDs, resource versions and timing vary. The exact check is relational: the object is in the verified namespace and cleanup still refers to the recorded object instance.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.
