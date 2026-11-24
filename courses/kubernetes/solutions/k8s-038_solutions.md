# k8s-038: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A digest identifies bytes under a hash algorithm. It can detect a change when compared with an independently trusted expected digest, but it does not tell you who published the bytes. A signature adds a claim verifiable under a public key. That still leaves a trust question: why is this key authorized to speak for the publisher or artifact you care about?

The local fixture contains a real RSA/SHA256 signature, a public key, an attestation and a tampered copy. The signing private key was used only in memory during authoring and is not included. This demonstrates actual offline cryptographic verification of a synthetic statement. It is not an OCI image signature, a Sigstore bundle, a certificate chain or evidence that a real organization published an image.

The attestation states a digest for synthetic fixture bytes. Verification has two joins: the signature must validate the attestation under the chosen public key, and the attested content digest must match the actual artifact being evaluated. A valid signature over an unrelated artifact is not authorization to run the current image. Admission enforcement is another boundary: successfully verifying a file offline does not mean the cluster will require that verification.

## Exercise 1: Identify trust inputs

A signature check is meaningful only relative to a trust decision. The course fixes a synthetic public key so the mathematical verification can be tested while making clear that no real organizational publisher identity is established.

**Expected:** Four distinct roles with an independently chosen trust key.

**Solution reasoning**

- **Approach:** Separate payload, signature, public key and expected digest, and note where the key came from.
- **Why it is correct:** A signature only means something if the verifying key was obtained independently of the artifact.
- **Plausible wrong approach:** Taking the public key from the same bundle as the payload lets an attacker supply both.
- **How to verify:** Four roles are listed, and the key has an independent source.

## Exercise 2: Check content integrity

The digest comparison must use an independent expected value. Computing a fresh digest and merely printing it is not an integrity check, because there is nothing trusted to compare it against.

**Expected:** Different content produces a different expected comparison result.

**Solution reasoning**

- **Approach:** Hash the original and changed byte sequences with the declared algorithm.
- **Why it is correct:** A cryptographic hash changes completely when any byte changes, so the two digests differ.
- **Plausible wrong approach:** Comparing visible text could miss a whitespace or encoding change.
- **How to verify:** The two digests differ, and only the original matches the expected one.

## Exercise 3: Verify the positive signature

This is the cryptographic positive control. The standard-library chapter checker cannot replace it because it only computes hashes. Keep the tool version and trust input fingerprint with the receipt for reproducibility.

**Expected:** Exit 0 plus successful verification output, with tool identity recorded.

**Solution reasoning**

- **Approach:** Run the qualified CLI against attestation.json with the fixed key and signature, recording tool and exit.
- **Why it is correct:** Exit 0 with a success message means the signature matches the payload bytes under that key.
- **Plausible wrong approach:** Treating any output text as success ignores a nonzero exit hidden behind a warning.
- **How to verify:** Command, exit 0 and tool version are recorded.

## Exercise 4: Verify the tamper negative

The negative control catches a verifier invocation that accidentally ignores the signature or checks the wrong file. Re-signing the modified file or replacing the public key would destroy the intended experiment.

**Expected:** Nonzero exit and verification failure.

**Solution reasoning**

- **Approach:** Repeat the exact command against attestation-tampered.json.
- **Why it is correct:** The changed payload no longer matches the signature, so verification fails with a nonzero exit.
- **Plausible wrong approach:** Regenerating the signature for the tampered file makes it verify and erases the negative control.
- **How to verify:** Only the payload changed, and the run exits nonzero.

## Exercise 5: Join signature subject to artifact

A signature authenticates a statement under its trust assumptions. Deployment authorization also requires matching that statement to the artifact being deployed and applying the intended policy, rather than accepting any valid signature.

**Expected:** The signed subject digest must match the actual artifact under the correct format contract.

**Solution reasoning**

- **Approach:** Compare the subject digest inside the signed statement with artifactB's actual digest.
- **Why it is correct:** The signature binds the statement, and the statement names artifactA's digest, so it says nothing about B.
- **Plausible wrong approach:** Accepting B because the signature verifies ignores what the signed statement is about.
- **How to verify:** The subject digest differs from artifactB's digest.

## Exercise 6: State enforcement and offline limits

The report should state exactly which algorithm, key and payload were tested. It should not claim registry provenance, transparency-log validation or enforced cluster protection without the corresponding real materials and runtime receipts.

**Expected:** Synthetic RSA fixture only; real image and cluster policy qualification remain separate.

**Solution reasoning**

- **Approach:** List what this local RSA check cannot prove: registry provenance, cluster admission and identity of a real image.
- **Why it is correct:** The check verifies one file locally; a cluster enforces nothing unless an admission policy checks images.
- **Plausible wrong approach:** Claiming images are now verified at deploy time assumes an admission controller that was never configured.
- **How to verify:** The list names all three limits.

## Boundary and troubleshooting review

An OCI image digest identifies a registry manifest or index under the image-distribution contract, not the arbitrary synthetic string used here. Multi-platform indices and platform-specific manifests also need explicit interpretation. The current course image tag 0.2.0 remains a runtime allowlist identity, not a signature-based admission policy.

A full image-provenance lab requires prewarmed real image digest and signature/bundle material, an offline-qualified verification tool and a host policy that binds the verified subject to the submitted image. Those capabilities are not supplied by this synthetic signature exercise. Never fetch new trust data silently or replace a failed trusted key with one found in the rejected artifact.
