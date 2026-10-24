# k8s-038: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A digest identifies bytes under a hash algorithm. It can detect a change when compared with an independently trusted expected digest, but it does not tell you who published the bytes. A signature adds a claim verifiable under a public key. That still leaves a trust question: why is this key authorized to speak for the publisher or artifact you care about?

The local fixture contains a real RSA/SHA256 signature, a public key, an attestation and a tampered copy. The signing private key was used only in memory during authoring and is not included. This demonstrates actual offline cryptographic verification of a synthetic statement. It is not an OCI image signature, a Sigstore bundle, a certificate chain or evidence that a real organization published an image.

The attestation states a digest for synthetic fixture bytes. Verification has two joins: the signature must validate the attestation under the chosen public key, and the attested content digest must match the actual artifact being evaluated. A valid signature over an unrelated artifact is not authorization to run the current image. Admission enforcement is another boundary: successfully verifying a file offline does not mean the cluster will require that verification.

## Exercise 1: Identify trust inputs

A signature check is meaningful only relative to a trust decision. The course fixes a synthetic public key so the mathematical verification can be tested while making clear that no real organizational publisher identity is established.

**Expected:** Four distinct roles with an independently chosen trust key.

## Exercise 2: Check content integrity

The digest comparison must use an independent expected value. Computing a fresh digest and merely printing it is not an integrity check, because there is nothing trusted to compare it against.

**Expected:** Different content produces a different expected comparison result.

## Exercise 3: Verify the positive signature

This is the cryptographic positive control. The standard-library chapter checker cannot replace it because it only computes hashes. Keep the tool version and trust input fingerprint with the receipt for reproducibility.

**Expected:** Exit0 plus successful verification output, with tool identity recorded.

## Exercise 4: Verify the tamper negative

The negative control catches a verifier invocation that accidentally ignores the signature or checks the wrong file. Re-signing the modified file or replacing the public key would destroy the intended experiment.

**Expected:** Nonzero exit and verification failure.

## Exercise 5: Join signature subject to artifact

A signature authenticates a statement under its trust assumptions. Deployment authorization also requires matching that statement to the artifact being deployed and applying the intended policy, rather than accepting any valid signature.

**Expected:** The signed subject digest must match the actual artifact under the correct format contract.

## Exercise 6: State enforcement and offline limits

The report should state exactly which algorithm, key and payload were tested. It should not claim registry provenance, transparency-log validation or enforced cluster protection without the corresponding real materials and runtime receipts.

**Expected:** Synthetic RSA fixture only; real image and cluster policy qualification remain separate.

## Boundary and troubleshooting review

An OCI image digest identifies a registry manifest or index under the image-distribution contract, not the arbitrary synthetic string used here. Multi-platform indices and platform-specific manifests also need explicit interpretation. The current course image tag0.2.0 remains a runtime allowlist identity, not a signature-based admission policy.

A full image-provenance lab requires prewarmed real image digest and signature/bundle material, an offline-qualified verification tool and a host policy that binds the verified subject to the submitted image. Those capabilities are not supplied by this synthetic signature exercise. Never fetch new trust data silently or replace a failed trusted key with one found in the rejected artifact.
