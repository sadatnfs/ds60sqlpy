# k8s-056: explanatory solutions

Attempt each exercise first, then compare ([study guide](../STUDY-GUIDE.md#solutions-and-the-ai-tutor)).

## Mechanism review

Network address translation changes address or port fields as traffic crosses a boundary. Destination NAT changes where a packet is delivered; source NAT changes the apparent sender. Connection tracking can maintain state so replies follow the corresponding translated path. These mechanisms can make an application’s observed client address differ from the original caller.

Kubernetes traffic policies influence endpoint selection and source-address behavior, but exact paths depend on the Service type and implementation. externalTrafficPolicy Local can preserve source IP in common node-backed paths and restrict external traffic to local endpoints, with availability and load-distribution tradeoffs. It is not a universal declaration that every proxy will forward the original client address unchanged.

An HTTP proxy can also add forwarding headers. Those are application-layer claims, separate from the transport peer address. Trust them only from a configured proxy chain. A user-supplied header must not become an authoritative client identity merely because its name contains forwarded.

Track the source and destination tuple at each hop. A request arriving at nodeA may be forwarded to a Pod on nodeB, adding another route and potentially translation. A local-only policy can avoid that hop but requires an eligible local endpoint for the intended traffic.

The synthetic examples explain the tradeoff without asserting a particular provider behavior. A real source-IP test needs a known caller, a controlled server that reports its transport peer, and a documented proxy path. Do not infer it from a header alone.

## Exercise 1: Distinguish DNAT and SNAT.

Track the field that changes. Both can occur in one path, and replies depend on the resulting routing/state.

**Expected:** Destination rewrite versus source rewrite.

**Solution reasoning**

- **Approach:** Label DNAT as rewriting the destination and SNAT as rewriting the source of a packet.
- **Why it is correct:** kube-proxy uses DNAT to turn a Service address into a Pod address, while SNAT hides the original caller behind another address.
- **Plausible wrong approach:** Calling every translation NAT without saying which field changed hides why the backend sees a different peer.
- **How to verify:** The answer pairs DNAT with destination rewrite and SNAT with source rewrite.

## Exercise 2: Predict backend peer identity after SNAT.

Application logs must state which identity they record. A changed peer does not necessarily mean a different human caller.

**Expected:** It can be a node or proxy address rather than the original client.

**Solution reasoning**

- **Approach:** Predict the peer address the backend records after the source is rewritten.
- **Why it is correct:** With SNAT the backend sees the node or proxy that rewrote the packet, not the original client.
- **Plausible wrong approach:** Logging the peer address as the client IP after SNAT attributes every request to the node.
- **How to verify:** The prediction says the peer can be a node or proxy address.

## Exercise 3: Draw a five-tuple path through one translation.

A tuple-level trace is more precise than a vague statement that traffic goes through a Service.

**Expected:** Source/destination addresses and ports are named before and after.

**Solution reasoning**

- **Approach:** Write the source and destination address and port before and after the translation point.
- **Why it is correct:** Naming all four fields on both sides shows exactly which values one rewrite changed.
- **Plausible wrong approach:** Recording only destination addresses hides a source rewrite that changes what the backend logs.
- **How to verify:** Both tuples are written out with addresses and ports.

## Exercise 4: Diagnose missing traffic on a node with Local policy and no endpoint.

Do not assume every node can forward to any remote backend under a local-only policy.

**Expected:** Endpoint locality and upstream health selection matter.

**Solution reasoning**

- **Approach:** Check whether the node receiving traffic has a local endpoint under externalTrafficPolicy Local.
- **Why it is correct:** Local policy only forwards to endpoints on the same node, so a node without one drops or fails health checks for that traffic.
- **Plausible wrong approach:** Scaling the Deployment without checking placement may still leave that node with no endpoint.
- **How to verify:** The diagnosis names endpoint locality and upstream health check selection.

## Exercise 5: Explain why arbitrary forwarded headers are untrusted.

Use a defined proxy chain and application configuration. Otherwise logs or rate limits can accept spoofed identity.

**Expected:** Clients can supply them unless the trusted proxy boundary sanitizes them.

**Solution reasoning**

- **Approach:** State that any client can send X-Forwarded-For with any value.
- **Why it is correct:** Only a trusted proxy that strips or overwrites the header makes its value meaningful.
- **Plausible wrong approach:** Using the first header value as the client address lets a caller choose its own identity.
- **How to verify:** The answer requires a trusted proxy boundary that sanitizes the header.

## Exercise 6: Design a source-IP acceptance test.

Record the actual implementation and policy. A generic diagram does not prove what your cluster preserves.

**Expected:** Known caller, documented path, transport peer and trusted-header evidence.

**Solution reasoning**

- **Approach:** Use a known caller over a documented path, recording the transport peer and any trusted header.
- **Why it is correct:** Comparing what the backend sees with the known source shows whether translation or a proxy changed it.
- **Plausible wrong approach:** Testing from an unknown source leaves nothing to compare the recorded address against.
- **How to verify:** The test record has the caller, path, transport peer and trusted header evidence.
