# k8s-048: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

DNS maps names to records such as IP addresses. Kubernetes cluster DNS creates service records according to namespace and cluster domain. A short name can resolve differently depending on the caller’s namespace and search configuration. A fully qualified service name makes the intended scope clearer.

For a typical cluster domain cluster.local, a Service named api in namespace study has a name like api.study.svc.cluster.local. The cluster domain is configurable, so do not hardcode it as a universal fact in a reusable client. A DNS answer establishes name resolution, not a listening process or healthy application.

Caching affects how quickly clients observe changes. Resolver libraries and applications can cache differently, and long-lived connections can continue using an existing destination without a new DNS lookup. Diagnose the actual client behavior before concluding that a DNS record update should have moved every request immediately.

A Pod’s dnsPolicy and dnsConfig influence resolver behavior. Search suffixes and ndots can cause multiple queries for one short-looking name. NetworkPolicy that blocks DNS can break service discovery even when direct IP transport works.

The fixture’s names are synthetic. Optional host observations should inspect the relevant Pod’s resolver and issue a bounded lookup from the intended namespace. Do not use a successful lookup on the laptop as proof of what a Pod’s resolver sees.

## Exercise 1: Predict a short-name lookup from another namespace.

Caller context changes name expansion. Use an appropriately qualified name when crossing namespaces.

**Expected:** It may search that namespace rather than the intended study service.

## Exercise 2: State the configurable part of the FQDN.

Read the prepared environment’s configuration. Teaching defaults should be labeled as examples.

**Expected:** The cluster domain is not universally cluster.local.

## Exercise 3: Draw resolution and connection as separate phases.

This prevents a valid DNS result from being overclaimed as service health.

**Expected:** DNS record, transport connection and application response have distinct evidence.

## Exercise 4: Diagnose direct-IP success with name failure.

The app listener can be correct while discovery fails. Do not change its port before locating the DNS problem.

**Expected:** Investigate resolver configuration, DNS reachability and policy.

## Exercise 5: Explain stale behavior after endpoint changes.

Inspect the client lifecycle and resolver policy. Repeatedly changing records without evidence can make the incident harder to interpret.

**Expected:** Caching or existing connections can delay fresh destination use.

## Exercise 6: Design robust service discovery for a client.

A client must handle transient discovery and transport failures while respecting operation retry safety.

**Expected:** Known namespace/domain, bounded resolution/connection and safe reconnect behavior.
