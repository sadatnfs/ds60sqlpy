# k8s-055: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

TLS protects a transport connection through encryption and peer authentication according to a trust model. A server certificate binds a public key to identities such as DNS names. The client must validate the requested name, certificate chain and validity conditions. Encryption without meaningful identity verification does not establish the intended server.

TLS termination means a component decrypts the client connection and may open another connection upstream. A load balancer, Ingress controller or Gateway can terminate TLS. The proxy-to-application hop then has its own protocol and trust requirements. Client-to-proxy encryption does not automatically encrypt the upstream hop.

SNI communicates the requested server name during the TLS handshake so a listener can select an appropriate certificate. HTTP Host routing occurs after a successful HTTP-capable connection. A certificate mismatch and an HTTP 404 are failures at different stages and need different diagnosis.

Kubernetes commonly stores certificate/key material in a Secret referenced by the controller configuration. Secret base64 encoding is not encryption. Do not include a private key in a lesson fixture or print Secret data during inspection. The fixture uses no real certificate and does not request one from an external authority.

For a real owned lab, validate the hostname, listener protocol, certificate reference, controller support and upstream policy. Never teach disabling certificate verification as the normal solution to a mismatched name. A self-signed teaching certificate needs an explicitly scoped trust setup, not global trust changes.

## Exercise 1: Predict whether a matching IP is enough for a DNS certificate.

An IP route and an authenticated DNS identity are different properties. Use the intended name and certificate relationship.

**Expected:** The requested name must satisfy certificate identity validation.

## Exercise 2: Locate the TLS termination point.

Everything after that point has a separate transport policy. Draw the upstream hop explicitly.

**Expected:** The component that decrypts the client connection.

## Exercise 3: Design a no-secret TLS evidence record.

Useful validation does not require publishing sensitive material. Keep credentials in the prepared private channel.

**Expected:** Names, certificate metadata and status without private key bytes.

## Exercise 4: Diagnose certificate mismatch separately from 404.

Repair the first failing layer. Changing backend selectors cannot fix an invalid certificate name.

**Expected:** Identity validation versus HTTP routing/content.

## Exercise 5: Explain why base64 Secret data is not encrypted protection.

Protection depends on access controls, storage encryption and operational handling. Never treat encoded text as safe to publish.

**Expected:** Encoding is reversible representation, not confidentiality.

## Exercise 6: Plan a two-hop trust policy.

The design should say where encryption is required and which peer each component trusts, then test those claims separately.

**Expected:** Client-facing identity and upstream identity are both explicit.
