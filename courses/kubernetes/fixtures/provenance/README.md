# Synthetic offline signature fixture

This is a real RSA/SHA256 signature over attestation.json, created solely for this course. The public key identifies a synthetic course publisher by the local trust decision, not a real registry or organization. No private key is stored. The attestation names synthetic content; it is not an OCI image manifest or a Sigstore bundle.

The immutable receipt records the public-key digest and the authoring verifier. Verification must check both the original positive case and attestation-tampered.json. The tiny Python chapter check verifies content hashing only. Use a qualified OpenSSL-compatible CLI for actual signature verification, as shown in the guide. Do not regenerate or replace the key to make a failed verification pass.
