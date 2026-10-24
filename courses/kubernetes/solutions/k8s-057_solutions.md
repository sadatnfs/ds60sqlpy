# k8s-057: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

A headless Service has clusterIP None and does not provide the ordinary virtual-IP load-balancing abstraction. With a selector, DNS can return endpoint addresses so clients discover individual backends. This is useful when an application protocol needs peer identity rather than an anonymous interchangeable service endpoint.

A StatefulSet provides stable Pod identities and ordered-management semantics under its configuration. Stable names do not mean a Pod process never changes, and storage retention does not guarantee application replication or consistency. A replacement Pod can have a new UID while keeping a stable logical name.

Stateful systems often need bootstrap discovery before every peer is ready. publishNotReadyAddresses can alter which endpoints are published, but it also exposes clients to peers that are not ready for ordinary work. Use it only with a protocol that understands the distinction between discovery and serving.

The headless Service fixture names the same selector but sets clusterIP to None. Its A/AAAA answers identify Pod addresses directly. There is no virtual-IP proxy translating Service port 80 into targetPort 8080: a client using those addresses must connect to the actual endpoint listener 8080. A client using SRV discovery must honor the returned endpoint port and target. A/AAAA records carry addresses only, so those clients need the listener port from their application configuration. For this fixture, request http://network-study-headless:8080/version; the successful body is ds60-fixture-v1 plus a newline. The named-port SRV query uses _http._tcp.network-study-headless with the actual namespace and cluster domain, and a capable client honors each returned target/port. Merely requesting headless-name:80 would not reach this fixture’s 8080 listener.

A StatefulSet’s serviceName ties its network identity to a governing Service. DNS names depend on Pod identity, service, namespace and cluster domain.

A client receiving several addresses must implement its own selection, retries and protocol semantics. DNS returning three peers does not guarantee a quorum, leader election or replicated data. Those are application properties that require separate evidence.

## Exercise 1: Predict the DNS role of a headless Service.

The client sees peers rather than one ordinary virtual IP. It must handle their lifecycle according to its protocol.

**Expected:** Discovery can return individual backend addresses.

## Exercise 2: Distinguish StatefulSet name and Pod UID.

Use UIDs when proving replacement and ownership. Names alone do not establish process continuity.

**Expected:** A stable logical name can refer to a replacement instance.

## Exercise 3: Draw a stateful peer discovery sequence.

Discovery is only the first stage. Quorum and data correctness require protocol-specific checks.

**Expected:** Resolve peer addresses, establish identity and run the application protocol.

## Exercise 4: Diagnose treating headless DNS as automatic load balancing.

Multiple DNS answers do not implement the same contract as a Service virtual IP for every client.

**Expected:** The client owns address selection and connection behavior.

## Exercise 5: Explain publishNotReadyAddresses tradeoffs.

Bootstrap needs can justify this behavior, but ordinary clients must not assume every published address is ready.

**Expected:** Discovery may include peers not ready for normal serving.

## Exercise 6: Design a stateful replacement check.

A retained PVC object is not enough. The replacement must actually read the expected durable state.

**Expected:** Logical identity, new UID, intended volume and application-level data result.
