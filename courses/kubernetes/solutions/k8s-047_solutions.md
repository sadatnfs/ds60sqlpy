# k8s-047: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A ClusterIP Service gives clients a stable virtual endpoint for a changing set of backends. The selector usually identifies Pods by labels. The Service port is what clients address; targetPort identifies the backend listener, either numerically or through a named container port. A Service does not select an image name or Deployment name directly.

Layer 4 routing concerns transport connections such as TCP. It does not normally choose a backend by HTTP path or rewrite an application URL. HTTP-aware routing belongs to a proxy or controller with that capability. A long-lived TCP connection can continue using one backend even if individual requests are numerous.

A Service can exist with no eligible endpoints. Its ClusterIP allocation is not a health certificate. Read the selector, matching Pod labels, readiness and EndpointSlices, then issue a fresh request from the intended caller. Each observation narrows a different possible failure.

The fixture uses Service port 80 and named targetPort http, resolving to containerPort 8080 on the selected Pod. Named ports help avoid duplicating a number but still need a matching declaration and real listener. Protocol defaults and transport type should be explicit when teaching non-TCP workloads.

A selectorless Service can be paired with manually managed EndpointSlices, but it has a different ownership model and extra restrictions. This introductory fixture uses selectors so the controller maintains endpoints. Do not manually edit controller-owned slices to hide a wrong selector.

## Exercise 1: Predict client and backend ports.

The two fields belong to different sides of the mapping. The app listener must match the resolved target.

**Expected:** Client 80 and backend 8080.

## Exercise 2: Change only the Service selector in a synthetic record.

The Service object can remain valid. Controller-derived endpoint evidence reveals the mismatch.

**Expected:** The matching endpoint set becomes empty.

## Exercise 3: Trace a fresh TCP request through the Service.

A connection-level path is more precise than saying the Service sends traffic to a Deployment.

**Expected:** Caller, virtual destination, chosen endpoint and listener are named.

## Exercise 4: Diagnose a ClusterIP with no ready endpoints.

Allocation and backend eligibility are separate. A public load balancer would not fix an empty backend set.

**Expected:** Inspect selector matches and readiness before external routing.

## Exercise 5: Explain why HTTP path routing is not provided by this Service.

An HTTP-aware proxy needs a separate configuration and implementation. Keep transport and application routing distinct.

**Expected:** Layer 4 connection selection does not interpret URL paths.

## Exercise 6: Design a stable endpoint for replacing Pods.

Verify replacement with UIDs when needed. Stable access does not mean the same Pod handled every request.

**Expected:** Clients use Service discovery while backend identities can change.
