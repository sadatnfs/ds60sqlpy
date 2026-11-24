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

**Solution reasoning**

- **Approach:** Check that the requested DNS name appears in the certificate's subject alternative names.
- **Why it is correct:** Clients validate the name they asked for against the certificate, regardless of which IP answered.
- **Plausible wrong approach:** Assuming the right IP is enough ignores that hostname verification is name based.
- **How to verify:** The prediction says the requested name must match the certificate identity.

## Exercise 2: Locate the TLS termination point.

Everything after that point has a separate transport policy. Draw the upstream hop explicitly.

**Expected:** The component that decrypts the client connection.

**Solution reasoning**

- **Approach:** Find the component that holds the private key and decrypts the client's TLS session.
- **Why it is correct:** Termination happens where the key lives, such as the Ingress proxy, and traffic beyond it may be plain or re-encrypted.
- **Plausible wrong approach:** Assuming the app terminates TLS because the client sees HTTPS can be wrong when a proxy holds the key.
- **How to verify:** The answer names the decrypting component.

## Exercise 3: Design a no-secret TLS evidence record.

Useful validation does not require publishing sensitive material. Keep credentials in the prepared private channel.

**Expected:** Names, certificate metadata and status without private key bytes.

**Solution reasoning**

- **Approach:** Record host names, issuer, validity dates, SAN entries and Secret name, leaving out key bytes.
- **Why it is correct:** This metadata is enough to check identity and expiry without exposing what an attacker would need.
- **Plausible wrong approach:** Pasting the full Secret YAML into notes copies the private key with it.
- **How to verify:** The record has names, certificate metadata and status, with no key bytes.

## Exercise 4: Diagnose certificate mismatch separately from 404.

Repair the first failing layer. Changing backend selectors cannot fix an invalid certificate name.

**Expected:** Identity validation versus HTTP routing/content.

**Solution reasoning**

- **Approach:** Classify a handshake failure as identity validation and a 404 as an HTTP response from a routed component.
- **Why it is correct:** A certificate mismatch stops the connection before any HTTP request, while a 404 means routing ran.
- **Plausible wrong approach:** Fixing routes to cure a certificate error changes a layer that was never reached.
- **How to verify:** The two failures are diagnosed at different layers.

## Exercise 5: Explain why base64 Secret data is not encrypted protection.

Protection depends on access controls, storage encryption and operational handling. Never treat encoded text as safe to publish.

**Expected:** Encoding is reversible representation, not confidentiality.

**Solution reasoning**

- **Approach:** Decode a Secret value with base64 to show anyone with read access gets the plaintext.
- **Why it is correct:** Base64 is a reversible encoding, so protection must come from RBAC and encryption at rest.
- **Plausible wrong approach:** Treating encoded Secret data as encrypted encourages wider read access than intended.
- **How to verify:** The answer calls the encoding reversible and not confidential.

## Exercise 6: Plan a two-hop trust policy.

The design should say where encryption is required and which peer each component trusts, then test those claims separately.

**Expected:** Client-facing identity and upstream identity are both explicit.

**Solution reasoning**

- **Approach:** State the identity clients validate at the proxy and the identity the proxy validates upstream.
- **Why it is correct:** Each hop is a separate TLS session with its own certificate and trust settings.
- **Plausible wrong approach:** Securing only the client hop and assuming the upstream is trusted leaves the second hop unverified.
- **How to verify:** Both client-facing and upstream identities are written down.
