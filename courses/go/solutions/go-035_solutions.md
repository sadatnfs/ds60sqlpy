# go-035: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Kubernetes exposes typed API resources through a declarative control plane. An object has an identity and metadata, desired configuration in spec, and observed information in status. A controller does not assume a successful API write means the requested real-world state already exists. metadata.uid distinguishes an object incarnation from a later object reusing the same name. generation tracks desired-state changes for resources that support that convention, while resourceVersion supports concurrency and watch semantics. Treat resourceVersion as opaque. This lesson decodes synthetic Deployment-shaped JSON to make these distinctions concrete without using credentials or contacting a cluster.

apiVersion identifies the API group and version; kind identifies an object kind. metadata.namespace plus name locates a namespaced object, while uid identifies its incarnation. Spec and status should have separate Go fields and responsibilities. Pointer fields can distinguish an omitted desired value from an explicit zero. JSON tags bind the Go representation to wire names. A struct here models only the selected fields and is not the full generated Kubernetes API type.

## 1. Decode desired and observed replicas: change one input

Copy worked example 1 into a scratch pad and change `"replicas":3` to `"replicas":4`. Before running, predict which check fails and which value it now sees; then run it and restore the original line.

The unchanged code is worked example 1:

```go
var d Deployment
err := json.Unmarshal([]byte(`{"apiVersion":"apps/v1","kind":"Deployment","metadata":{"name":"demo","namespace":"lesson","uid":"u1"},"spec":{"replicas":3},"status":{"readyReplicas":2}}`), &d)
check(err == nil && d.Spec.Replicas != nil && *d.Spec.Replicas == 3 && d.Status.Ready == 2, "spec status")
```

**Expected:** The changed run panics with `spec status` because `err == nil && d.Spec.Replicas != nil && *d.Spec.Replicas == 3 && d.Status.Ready == 2` no longer holds. Restoring the original line brings back the worked observation: desired is 3 while ready is 2.

The accepted object and the observed rollout are different evidence. A controller must reconcile the gap.

## 2. Distinguish omitted from explicit zero: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads ``check(json.Unmarshal([]byte(`{"spec":{"replicas":1}}`), &b) == nil, "decode")``. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
var a, b Deployment
check(json.Unmarshal([]byte(`{"spec":{}}`), &a) == nil, "decode")
check(json.Unmarshal([]byte(`{"spec":{"replicas":0}}`), &b) == nil, "decode")
check(a.Spec.Replicas == nil && b.Spec.Replicas != nil && *b.Spec.Replicas == 0, "presence")
```

**Expected:** Before the repair the program panics with `presence`; after it the line reads ``check(json.Unmarshal([]byte(`{"spec":{"replicas":0}}`), &b) == nil, "decode")`` again and only the explicit zero has a non-nil pointer.

Defaulting and an intentional scale-to-zero request have different meanings. A plain integer field would lose that distinction before validation.

## 3. Separate name and incarnation

Decode two objects that share namespace and name but carry different UIDs.

```go
var a, b Deployment
errA := json.Unmarshal([]byte(`{"metadata":{"name":"demo","namespace":"lesson","uid":"old"}}`), &a)
errB := json.Unmarshal([]byte(`{"metadata":{"name":"demo","namespace":"lesson","uid":"new"}}`), &b)
check(errA == nil && errB == nil, "decode")
check(a.Metadata.Name == b.Metadata.Name && a.Metadata.UID != b.Metadata.UID, "incarnation")
```

**Expected:** Their names match but their identities differ.

Cleanup based only on name can delete a replacement object that the operation never owned.

## 4. Keep namespaces in a key

Build keys with one function for the same name in two namespaces.

```go
key := func(m Metadata) string { return m.Namespace + "/" + m.Name }
a := Metadata{Name: "demo", Namespace: "alpha"}
b := Metadata{Name: "demo", Namespace: "beta"}
check(key(a) == "alpha/demo" && key(a) != key(b), "namespace key")
```

**Expected:** The key is alpha/demo for the first object and differs from the second object's key.

Names are unique within a namespaced resource scope, not across the whole cluster.

## 5. Treat versions as opaque

Decode resourceVersion tokens 10 and 9 and compare them as the strings they are.

```go
var a, b Metadata
errA := json.Unmarshal([]byte(`{"resourceVersion":"10"}`), &a)
errB := json.Unmarshal([]byte(`{"resourceVersion":"9"}`), &b)
check(errA == nil && errB == nil, "decode")
check(a.Version == "10" && a.Version != b.Version && a.Version < b.Version, "opaque version")
```

**Expected:** Both tokens are retained exactly; they differ, and string order even places 10 before 9, so only equality is meaningful.

Do not increment, subtract or numerically order resourceVersion. Its supported meaning is defined by API operations, and comparing tokens as text produces an order with no meaning.

## 6. Transfer readiness reasoning

Apply one readiness predicate to desired 3 with ready 3 and then ready 2.

```go
complete := func(d Deployment) bool { return d.Spec.Replicas != nil && d.Status.Ready == *d.Spec.Replicas }
want := 3
var d Deployment
d.Spec.Replicas = &want
d.Status.Ready = 3
check(complete(d), "ready")
d.Status.Ready = 2
check(!complete(d), "not ready")
```

**Expected:** Only the equal complete state satisfies this simplified predicate.

A real Deployment readiness check also considers generation and conditions. This count comparison is only one part of that contract.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
