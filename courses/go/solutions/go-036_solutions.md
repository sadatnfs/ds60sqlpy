# go-036: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

Labels attach identity and grouping information to objects. A selector expresses a membership rule, not an ownership proof. A Service selects matching Pods and exposes a stable service abstraction while actual endpoints change. Pods with the same labels can still belong to different controllers, and a broad selector can unintentionally combine workloads. Namespace scope, readiness and EndpointSlice state also affect usable service endpoints. This lesson models equality selectors and readiness filtering with tiny records. It does not emulate kube-proxy, DNS or packet routing; those mechanisms are taught and exercised in the Kubernetes networking path.

A map of required label pairs represents an AND of equality tests in this small model. Missing and empty-valued labels must be distinguished with comma-ok. Kubernetes additionally supports set-based selectors and API-specific selector forms. Stable application identity should be separate from rollout-specific labels when a Service must survive Deployment replacement. Never use label matching alone as permission to delete an object.

## 1. Match all required labels: predict an edited check

Copy worked example 1 into a scratch pad and change `matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` to `matches(map[string]string{"app!": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"})` inside its check. Before running, predict whether the check still passes and explain why; then restore it.

The unchanged code is worked example 1:

```go
check(matches(map[string]string{"app": "web", "tier": "frontend"}, map[string]string{"app": "web", "tier": "frontend"}), "match")
```

**Expected:** The changed run panics with `match` because the edited check no longer holds. Restoring the original line brings back the worked observation: the selector matches.

All selector pairs must match. Treating the requirements as OR would admit unintended workloads.

## 2. Reject a missing label: diagnose an edited check

A careless edit changed the check in worked example 2 so that it reads `matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})`. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it.

The unchanged code is worked example 2:

```go
check(!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"}), "missing")
```

**Expected:** Before the repair the program panics with `missing`; after it the line reads `!matches(map[string]string{"app": "web"}, map[string]string{"app": "web", "tier": "frontend"})` again and the selector does not match.

A missing required key is not a wildcard. Presence is part of the equality contract.

## 3. Distinguish empty value from absence

Require a present empty-valued label.

```go
check(matches(map[string]string{"flag": ""}, map[string]string{"flag": ""}), "empty present")
check(!matches(map[string]string{}, map[string]string{"flag": ""}), "empty absent")
```

**Expected:** A present empty label matches; absence does not.

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

Selection and readiness answer different questions. An object can belong to the workload without being eligible for traffic.

## 5. Inspect an overly broad selector

Use an empty equality selector against two unrelated labels.

```go
check(matches(map[string]string{"app": "web"}, nil) && matches(map[string]string{"app": "db"}, nil), "broad selector")
```

**Expected:** Both match this mathematical predicate.

This local predicate treats an empty conjunction as true. Real API semantics vary by resource and field, so consult the relevant API before using an empty selector.

## 6. Transfer rollout-stable identity

Match app=web across two different rollout labels.

```go
selector := map[string]string{"app": "web"}
check(matches(map[string]string{"app": "web", "revision": "a"}, selector) && matches(map[string]string{"app": "web", "revision": "b"}, selector), "rollout selector")
```

**Expected:** Both versions match the stable app selector.

The stable selector allows replacement backends. Whether both should receive traffic depends on rollout and readiness policy, not just matching labels.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.
