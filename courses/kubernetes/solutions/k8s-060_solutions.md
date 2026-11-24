# k8s-060: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Dual-stack networking supports IPv4 and IPv6 together. It requires compatible cluster configuration, node networking, CNI behavior and service allocation. Adding an IPv6 address to a manifest cannot supply a missing network family underneath it.

A dual-stack Service can have addresses in both families. The order and primary family are meaningful in the API. A client may receive A and AAAA DNS records and choose or race connection attempts according to its library. A successful IPv4 request does not prove IPv6 reachability, and a timeout in one family can affect perceived latency.

IPv6 notation uses colons, so literal addresses in URLs need brackets before a port. Documentation addresses are suitable for examples but are never live targets. Use actual owned assigned addresses only in an explicitly prepared lab.

Service ipFamilyPolicy can express SingleStack, PreferDualStack or RequireDualStack under supported conditions. ipFamilies and clusterIPs describe the requested or assigned families and addresses. RequireDualStack should fail when the cluster cannot satisfy it rather than silently establish a second network.

The supplied course application in docker/kubernetes/fixture.py binds IPv4 only at 0.0.0.0. Therefore dual-stack-service.yaml is an API-design fixture, not a working IPv6 application lab. Before claiming IPv6 acceptance, prepare a separately reviewed listener that actually accepts IPv6 and an appropriate client, in addition to the cluster/CNI capability. Do not infer application-family support from a Service having two allocated addresses. The separate maintained fixture at courses/kubernetes/fixtures/networking/dual-stack/ supplies an AF_INET6 listener with IPV6_V6ONLY disabled, a non-root image, workload/Service example and an explicit-family client. Follow its README for the successful end-to-end path after the owned dual-stack cluster is prepared. It serves /version with ds60-dualstack-v1, while the original fixture serves ds60-fixture-v1.

Check family-specific endpoints, DNS and request paths independently. A NetworkPolicy or firewall rule that covers only IPv4 may leave different behavior for IPv6. Security and observability should cover both intended paths.

## Exercise 1: Predict a RequireDualStack request on a single-stack cluster.

A declarative request is constrained by cluster capabilities. Report the missing capability instead of inventing a second address.

**Expected:** The intended requirement cannot be satisfied.

**Solution reasoning**

- **Approach:** Compare ipFamilyPolicy RequireDualStack with a cluster that has only one address family.
- **Why it is correct:** RequireDualStack demands addresses from both families, which a single-stack cluster cannot allocate.
- **Plausible wrong approach:** Expecting a silent fallback to one family confuses RequireDualStack with PreferDualStack.
- **How to verify:** The prediction says the requirement cannot be satisfied.

## Exercise 2: Distinguish A and AAAA records.

DNS availability and transport reachability are separate checks for each family.

**Expected:** IPv4 addresses versus IPv6 addresses.

**Solution reasoning**

- **Approach:** Match A records to IPv4 addresses and AAAA records to IPv6 addresses.
- **Why it is correct:** Clients request each record type separately, so one family can resolve while the other is missing.
- **Plausible wrong approach:** Checking only A records hides a missing IPv6 address.
- **How to verify:** The answer pairs A with IPv4 and AAAA with IPv6.

## Exercise 3: Build a family-specific acceptance table.

A single successful request may use only one family. Make coverage explicit.

**Expected:** DNS, Service, endpoints, policy and app response for both families.

**Solution reasoning**

- **Approach:** Build rows for DNS, Service clusterIPs, endpoints, policy and app response, with one column per family.
- **Why it is correct:** Each layer can work for one family and fail for the other, so both need separate evidence.
- **Plausible wrong approach:** One passing IPv4 test cannot show the IPv6 path works.
- **How to verify:** Every row has evidence for both families.

## Exercise 4: Diagnose IPv4 success with IPv6 timeout.

Do not treat the shared hostname as proof that both network paths work.

**Expected:** Inspect the IPv6 route, listener, endpoints and policy path.

**Solution reasoning**

- **Approach:** Check the IPv6 route, the app's IPv6 listener, IPv6 endpoints and IPv6 policy rules.
- **Why it is correct:** IPv4 success proves only the IPv4 path, and an app bound to IPv4 alone times out over IPv6.
- **Plausible wrong approach:** Blaming the Service because IPv4 works skips the family-specific layers.
- **How to verify:** The diagnosis covers route, listener, endpoints and policy for IPv6.

## Exercise 5: Explain bracketed IPv6 URL syntax.

Without the delimiters a parser cannot interpret the same structure as an IPv4 host:port string.

**Expected:** Brackets delimit the address before a colon-prefixed port.

**Solution reasoning**

- **Approach:** Wrap an IPv6 address in brackets before adding a colon and port in a URL.
- **Why it is correct:** IPv6 addresses contain colons, so brackets show where the address ends and the port starts.
- **Plausible wrong approach:** Writing the address without brackets makes the last group look like a port.
- **How to verify:** The answer shows the bracketed form and why it is needed.

## Exercise 6: Review dual-stack security coverage.

A policy that works for one address family does not automatically establish the other path’s exposure or isolation.

**Expected:** Intended allow/deny rules and observations cover both families.

**Solution reasoning**

- **Approach:** Compare each intended allow and deny rule against observations for both families.
- **Why it is correct:** A policy written with IPv4 CIDRs alone may leave IPv6 traffic unrestricted.
- **Plausible wrong approach:** Testing denial only over IPv4 can miss an open IPv6 path.
- **How to verify:** Rules and observations cover IPv4 and IPv6.
