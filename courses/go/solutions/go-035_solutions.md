# go-035: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Kubernetes exposes typed API resources through a declarative control plane. An object has an identity and metadata, desired configuration in spec, and observed information in status. A controller does not assume a successful API write means the requested real-world state already exists. metadata.uid distinguishes an object incarnation from a later object reusing the same name. generation tracks desired-state changes for resources that support that convention, while resourceVersion supports concurrency and watch semantics. Treat resourceVersion as opaque. This lesson decodes synthetic Deployment-shaped JSON to make these distinctions concrete without using credentials or contacting a cluster.

apiVersion identifies the API group and version; kind identifies an object kind. metadata.namespace plus name locates a namespaced object, while uid identifies its incarnation. Spec and status should have separate Go fields and responsibilities. Pointer fields can distinguish an omitted desired value from an explicit zero. JSON tags bind the Go representation to wire names. A struct here models only the selected fields and is not the full generated Kubernetes API type.

## 1. Decode desired and observed replicas

Decode a fixture requesting 3 replicas with 2 ready.

```go
var d Deployment
err := json.Unmarshal([]byte(`{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"demo","namespace":"lesson","uid":"u1"},"spec":{"replicas":3},"status":{"readyReplicas":2}}`), &d)
check(err == nil && d.Spec.Replicas != nil && *d.Spec.Replicas == 3 && d.Status.Ready == 2, "spec status")
```

**Expected:** Desired is 3 while ready is 2.

The accepted object and the observed rollout are different evidence. A controller must reconcile the gap.

## 2. Distinguish omitted from explicit zero

Decode one absent replicas field and one replicas zero.

```go
var a, b Deployment
check(json.Unmarshal([]byte(`{"spec":{}}`), &a) == nil, "decode")
check(json.Unmarshal([]byte(`{"spec":{"replicas":0}}`), &b) == nil, "decode")
check(a.Spec.Replicas == nil && b.Spec.Replicas != nil && *b.Spec.Replicas == 0, "presence")
```

**Expected:** Only the explicit zero has a non-nil pointer.

Defaulting and an intentional scale-to-zero request have different meanings. A plain integer field would lose that distinction before validation.

## 3. Separate name and incarnation

Construct two objects sharing name but having different UIDs.

```go
a := Metadata{Name: "demo", Namespace: "lesson", UID: "old"}
b := Metadata{Name: "demo", Namespace: "lesson", UID: "new"}
check(a.Name == b.Name && a.UID != b.UID, "incarnation")
```

**Expected:** Their names match but identities differ.

Cleanup based only on name can delete a replacement object that the operation never owned.

## 4. Keep namespaces in a key

Build keys for the same name in two namespaces.

```go
a, b := "alpha/demo", "beta/demo"
check(a != b, "namespace key")
```

**Expected:** The keys are different.

Names are unique within a namespaced resource scope, not across the whole cluster.

## 5. Treat versions as opaque

Store a nonnumeric resourceVersion token and compare it for equality.

```go
m := Metadata{Version: "opaque-v7"}
check(m.Version == "opaque-v7", "opaque version")
```

**Expected:** The exact token is retained.

Do not increment, subtract or numerically order resourceVersion. Its supported meaning is defined by API operations.

## 6. Transfer readiness reasoning

Compare desired 3 with ready 3 and then ready 2.

```go
wanted := 3
check(wanted == 3 && 3 == wanted, "ready")
check(2 != wanted, "not ready")
```

**Expected:** Only the equal complete state satisfies this simplified predicate.

A real Deployment readiness check also considers generation and conditions. This count comparison is only one part of that contract.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
