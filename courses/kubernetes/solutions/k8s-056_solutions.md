# k8s-056: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Network address translation changes address or port fields as traffic crosses a boundary. Destination NAT changes where a packet is delivered; source NAT changes the apparent sender. Connection tracking can maintain state so replies follow the corresponding translated path. These mechanisms can make an application’s observed client address differ from the original caller.

Kubernetes traffic policies influence endpoint selection and source-address behavior, but exact paths depend on the Service type and implementation. externalTrafficPolicy Local can preserve source IP in common node-backed paths and restrict external traffic to local endpoints, with availability and load-distribution tradeoffs. It is not a universal declaration that every proxy will forward the original client address unchanged.

An HTTP proxy can also add forwarding headers. Those are application-layer claims, separate from the transport peer address. Trust them only from a configured proxy chain. A user-supplied header must not become an authoritative client identity merely because its name contains forwarded.

Track the source and destination tuple at each hop. A request arriving at nodeA may be forwarded to a Pod on nodeB, adding another route and potentially translation. A local-only policy can avoid that hop but requires an eligible local endpoint for the intended traffic.

The synthetic examples explain the tradeoff without asserting a particular provider behavior. A real source-IP test needs a known caller, a controlled server that reports its transport peer, and a documented proxy path. Do not infer it from a header alone.

## Exercise 1: Distinguish DNAT and SNAT.

Track the field that changes. Both can occur in one path, and replies depend on the resulting routing/state.

**Expected:** Destination rewrite versus source rewrite.

## Exercise 2: Predict backend peer identity after SNAT.

Application logs must state which identity they record. A changed peer does not necessarily mean a different human caller.

**Expected:** It can be a node or proxy address rather than the original client.

## Exercise 3: Draw a five-tuple path through one translation.

A tuple-level trace is more precise than a vague statement that traffic goes through a Service.

**Expected:** Source/destination addresses and ports are named before and after.

## Exercise 4: Diagnose missing traffic on a node with Local policy and no endpoint.

Do not assume every node can forward to any remote backend under a local-only policy.

**Expected:** Endpoint locality and upstream health selection matter.

## Exercise 5: Explain why arbitrary forwarded headers are untrusted.

Use a defined proxy chain and application configuration. Otherwise logs or rate limits can accept spoofed identity.

**Expected:** Clients can supply them unless the trusted proxy boundary sanitizes them.

## Exercise 6: Design a source-IP acceptance test.

Record the actual implementation and policy. A generic diagram does not prove what your cluster preserves.

**Expected:** Known caller, documented path, transport peer and trusted-header evidence.
