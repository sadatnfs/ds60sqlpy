# k8s-048: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

DNS maps names to records such as IP addresses. Kubernetes cluster DNS creates service records according to namespace and cluster domain. A short name can resolve differently depending on the caller’s namespace and search configuration. A fully qualified service name makes the intended scope clearer.

For a typical cluster domain cluster.local, a Service named api in namespace study has a name like api.study.svc.cluster.local. The cluster domain is configurable, so do not hardcode it as a universal fact in a reusable client. A DNS answer establishes name resolution, not a listening process or healthy application.

Caching affects how quickly clients observe changes, but what can go stale depends on the Service type. A ClusterIP Service name keeps resolving to the same virtual IP while its endpoints change, so DNS caching does not delay endpoint changes there; staleness comes from long-lived connections that stay on their original backend. A headless Service returns Pod addresses directly, so a cached answer can keep sending new connections to a removed Pod until the record's TTL expires and the client resolves again. Resolver libraries and applications cache differently. Diagnose the actual client behavior before concluding that a DNS record update should have moved every request immediately.

A Pod’s dnsPolicy and dnsConfig influence resolver behavior. Search suffixes and ndots can cause multiple queries for one short-looking name. NetworkPolicy that blocks DNS can break service discovery even when direct IP transport works.

The fixture’s names are synthetic. Optional host observations should inspect the relevant Pod’s resolver and issue a bounded lookup from the intended namespace. Do not use a successful lookup on the laptop as proof of what a Pod’s resolver sees.

## Exercise 1: Predict a short-name lookup from another namespace.

Caller context changes name expansion. Use an appropriately qualified name when crossing namespaces.

**Expected:** It may search that namespace rather than the intended study service.

**Solution reasoning**

- **Approach:** Expand the short name using the caller Pod's resolv.conf search list.
- **Why it is correct:** The first search entry is the caller's own namespace, so a short name resolves there first.
- **Plausible wrong approach:** Assuming short names search every namespace would find the study Service from anywhere.
- **How to verify:** The prediction says the lookup may target the caller's namespace, and the fix uses a qualified name.

## Exercise 2: State the configurable part of the FQDN.

Read the prepared environment’s configuration. Teaching defaults should be labeled as examples.

**Expected:** The cluster domain is not universally cluster.local.

**Solution reasoning**

- **Approach:** Identify the cluster domain suffix as configurable and read it from the environment.
- **Why it is correct:** The kubelet's clusterDomain sets the suffix, and cluster.local is only a common default.
- **Plausible wrong approach:** Hardcoding cluster.local in clients breaks on clusters that chose another domain.
- **How to verify:** The answer names the cluster domain as configurable and labels cluster.local as an example.

## Exercise 3: Draw resolution and connection as separate phases.

This prevents a valid DNS result from being overclaimed as service health.

**Expected:** DNS record, transport connection and application response have distinct evidence.

**Solution reasoning**

- **Approach:** Draw DNS lookup, TCP connection and HTTP response as three phases with their own evidence.
- **Why it is correct:** A name can resolve while the connection or the application fails, so each phase needs its own observation.
- **Plausible wrong approach:** Calling the service healthy because DNS returned an address overclaims from the first phase.
- **How to verify:** Three phases each have distinct evidence.

## Exercise 4: Diagnose direct-IP success with name failure.

The app listener can be correct while discovery fails. Do not change its port before locating the DNS problem.

**Expected:** Investigate resolver configuration, DNS reachability and policy.

**Solution reasoning**

- **Approach:** Compare success by IP with failure by name and focus on resolution.
- **Why it is correct:** Since the IP works, the listener and path are fine, and the fault lies in resolver config, DNS reachability or a policy blocking DNS.
- **Plausible wrong approach:** Changing the application port fixes nothing that resolution depends on.
- **How to verify:** The next checks are resolver configuration, DNS reachability and policy.

## Exercise 5: Explain stale behavior after endpoint changes.

Inspect the client lifecycle and resolver policy. Repeatedly changing records without evidence can make the incident harder to interpret.

**Expected:** For a ClusterIP Service, existing connections keep their old backend because the name still resolves to the same virtual IP; for a headless Service, cached Pod address records can also send new connections to a removed Pod.

**Solution reasoning**

- **Approach:** Separate a ClusterIP Service from a headless Service when explaining stale behavior.
- **Why it is correct:** A ClusterIP name keeps resolving to one virtual IP, so only long-lived connections stick; headless names return Pod IPs that clients may cache.
- **Plausible wrong approach:** Rapidly recreating DNS records without checking client caching adds changes and obscures the cause.
- **How to verify:** The answer covers both Service types and names client lifecycle or resolver caching as the evidence.

## Exercise 6: Design robust service discovery for a client.

A client must handle transient discovery and transport failures while respecting operation retry safety.

**Expected:** Known namespace/domain, bounded resolution/connection and safe reconnect behavior.

**Solution reasoning**

- **Approach:** Specify a qualified name, bounded resolution and connection timeouts and reconnect that respects retry safety.
- **Why it is correct:** Discovery and connection can fail briefly, and a bounded retry recovers without repeating unsafe operations.
- **Plausible wrong approach:** Retrying every failed request without limit can duplicate a non-idempotent write.
- **How to verify:** The design lists namespace and domain, bounded timeouts and safe reconnects.
