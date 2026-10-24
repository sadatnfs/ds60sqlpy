# k8s-020: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Network diagnosis should proceed through distinct layers:the client's namespace/DNS context, name resolution, Service selection and port mapping, transport connection, and application response. A failure at one layer can produce a similar user-visible symptom to another, but the evidence needed to distinguish them differs.

The browser's positive fixture uses an in-cluster client to reach hello on port8080 and request /version. It does not publish a host port or depend on an external network service. Wrong-port, DNS and arbitrary-route experiments are separate scoped host fixtures because the browser client command and Service port are fixed.

A successful HTTP404 already shows that some HTTP server answered; it is not a DNS failure. A timeout after name resolution leaves several transport/backend possibilities and should not be labeled NetworkPolicy denial without enforcement evidence. Use the most specific observation available and retain uncertainty where the evidence does not identify a unique cause.

## Exercise 1: Name the layers

The layered model prevents changing application code for a name-resolution failure or blaming DNS for a returned404. It also identifies which evidence is still missing when a timeout is ambiguous.

**Expected:** Each layer has a distinct observation and possible failure.

## Exercise 2: Verify the allowed path

The client checks the intended local fixture route independently of readiness. The observed result is bounded to that source and target and does not establish arbitrary network connectivity.

**Expected:** Owned backend identity and exact /version response pass, with cleanup.

## Exercise 3: Classify NXDOMAIN

The trace should include the requested name and client context. A typo or namespace mismatch differs from DNS infrastructure failure, so retain the actual response rather than assuming the broadest cause.

**Expected:** Investigate name, namespace and DNS context before backend application state.

## Exercise 4: Classify a transport failure

Several mechanisms can produce the symptom. The next check should distinguish them within the owned target, not widen the scan or disable controls. Policy enforcement needs its own positive/negative traffic comparison.

**Expected:** Inspect ports, eligible endpoints and qualified policy evidence; cause remains conditional until discriminated.

## Exercise 5: Classify HTTP failures

A returned status and body provide more specific evidence than a generic unavailable report. The correct repair depends on whether the requested route or the responding application identity is wrong.

**Expected:** Route mismatch versus application-contract mismatch.

## Exercise 6: Design a finite host transfer

A transfer exercise can broaden understanding without broadening the worker allowlist. It needs an owned scope and actual observations; the worksheet should leave execution unavailable when that capability is absent.

**Expected:** Explicit target, allowed client, timeout, expected layer failure and cleanup are recorded.

## Boundary and troubleshooting review

Do not scan unrelated addresses or use an external endpoint to test a local lesson. A host port-forward is another host capability with its own scope and lifecycle; it is not implied by a ClusterIP Service. The current browser path uses the in-cluster client instead.

A positive one-shot request establishes only its observed path and payload. Production availability, network isolation and DNS reliability require broader evidence. A negative case should remain within a finite timeout and cleanup scope.
