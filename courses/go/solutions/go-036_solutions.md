# go-036: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-036_solution.go` implements all six cases.

## Mechanism

Labels attach identity and grouping information to objects. A selector expresses a membership rule, not an ownership proof. A Service selects matching Pods and exposes a stable service abstraction while actual endpoints change. Pods with the same labels can still belong to different controllers, and a broad selector can unintentionally combine workloads. Namespace scope, readiness and EndpointSlice state also affect usable service endpoints. This lesson models equality selectors and readiness filtering with tiny records. It does not emulate kube-proxy, DNS or packet routing; those mechanisms are taught and exercised in the Kubernetes networking path.

A map of required label pairs represents an AND of equality tests in this small model. Missing and empty-valued labels must be distinguished with comma-ok. Kubernetes additionally supports set-based selectors and API-specific selector forms. Stable application identity should be separate from rollout-specific labels when a Service must survive Deployment replacement. Never use label matching alone as permission to delete an object.

## 1. Match all required labels: predict an edited check

Copy worked example 1, change `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` to `matches(map[string]string{"app!": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` inside its check and predict whether it still passes; then restore it.

The unchanged code is worked example 1:

```go
check(matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"}), "match")
```

**Expected:** The edited check panics with `match` even though `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` still holds.

**Verify:** Restoring `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` makes the check pass again with the worked observation: the selector matches.

All selector pairs must match. Treating the requirements as OR would admit unintended workloads.

## 2. Reject a missing label: diagnose an edited check

A careless edit rewrote the check in worked example 2 as `matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})`. Explain the failure, then restore it.

The unchanged code is worked example 2:

```go
check(!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"}), "missing")
```

**Expected:** The defective run panics with `missing`; after restoring `!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})`, the selector does not match.

**Verify:** The edited check fails with message `missing` for a state that `!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})` accepts.

A missing required key is not a wildcard. Presence is part of the equality contract.

## 3. Distinguish empty value from absence

Require a present empty-valued label.

```go
check(matches(map[string]string{"flag": ""}, map[string]string{"flag": ""}), "empty present")
check(!matches(map[string]string{}, map[string]string{"flag": ""}), "empty absent")
```

**Expected:** A present empty label matches; absence does not.

**Verify:** Your solution must keep `matches(map[string]string{"flag": ""}, map[string]string{"flag": ""})` true. Control: changing `check(matches(map[string]string{"flag": ""}, map[string]string{"flag": ""}), "empty present")` to `check(matches(map[string]string{"flag!": ""}, map[string]string{"flag": ""}), "empty present")` panics with message `empty present`; revert it.

Reading only the map zero value would collapse absence into empty text and incorrectly match the second case.

## 4. Filter readiness separately

Select two matching Pods but admit only the ready one as usable.

```go
pods := []PodView{{Labels: map[string]string{"app": "web"}, Ready: true}, {Labels: map[string]string{"app": "web"}, Ready: false}}
count := 0
for _, p := range pods {
	if matches(p.Labels, map[string]string{"app": "web"}) && p.Ready {
		count++
	}
}
check(count == 1, "ready backends")
```

**Expected:** Exactly one usable backend remains.

**Verify:** Your solution must keep `count == 1` true. Control: changing `if matches(p.Labels, map[string]string{"app": "web"}) && p.Ready {` to `if matches(p.Labels, map[string]string{"app": "web"}) || p.Ready {` panics with message `ready backends`; revert it.

Selection and readiness answer different questions. An object can belong to the workload without being eligible for traffic.

## 5. Inspect an overly broad selector

Use an empty equality selector against two unrelated labels.

```go
check(matches(map[string]string{"app": "web"}, nil) && matches(map[string]string{"app": "db"}, nil), "broad selector")
```

**Expected:** Both match this mathematical predicate.

**Verify:** Your solution must keep `matches(map[string]string{"app": "web"}, nil) && matches(map[string]string{"app": "db"}, nil)` true. Control: an input that falsifies it fails with message `broad selector`; revert it.

This local predicate treats an empty conjunction as true. Real API semantics vary by resource and field, so consult the relevant API before using an empty selector.

## 6. Transfer rollout-stable identity

Match app=web across two different rollout labels.

```go
selector := map[string]string{"app": "web"}
check(matches(map[string]string{"app": "web", "revision": "a"}, selector) && matches(map[string]string{"app": "web", "revision": "b"}, selector), "rollout selector")
```

**Expected:** Both versions match the stable app selector.

**Verify:** Your solution must keep `matches(map[string]string{"app": "web", "revision": "a"}, selector) && matches(map[string]string{"app": "web", "revision": "b"}, selector)` true. Control: changing `selector := map[string]string{"app": "web"}` to `selector := map[string]string{"app!": "web"}` panics with message `rollout selector`; revert it.

The stable selector allows replacement backends. Whether both should receive traffic depends on rollout and readiness policy, not just matching labels.

## Transfer after comparison

Service routing, Deployment ownership, NetworkPolicy and the controller watches in later lessons all depend on selectors. When a Service has no endpoints, check the namespace, the exact label keys and values, and readiness, in that order. When writing a controller, filter by owner reference too, so two workloads that share labels never claim each other's Pods.
