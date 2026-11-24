# k8s-019: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Secret is a Kubernetes object for data that requires restricted handling. Its data field uses base64 encoding, which is a reversible representation rather than encryption. Access control, encryption-at-rest configuration, transport security and application handling are separate controls. Verify those actual controls instead of inferring confidentiality from the object kind.

This lesson uses only the public markers DUMMY_LESSON_ONLY and DUMMY_LESSON_ROTATED. The current browser worker has no Secret permission and does not accept Secret manifests or Secret references. Live mount behavior is available only through a teacher-provided synthetic fixture in a separate scoped host capability. No real credential is needed or should be collected.

Configuration lifetime still matters. A Secret-derived environment value is captured when a process starts. A projected Secret file can refresh asynchronously, but application reload behavior determines when the process uses new bytes. Encoding does not change those lifecycle semantics.

## Exercise 1: Decode the authored marker

The result demonstrates that base64 is reversible. It should not be described as decryption or as proof of a security boundary. The literal marker is intentionally harmless teaching data.

**Expected:** Exact DUMMY_LESSON_ONLY round trip.

**Solution reasoning**

- **Approach:** Base64-decode only the supplied value and re-encode the result to compare.
- **Why it is correct:** Base64 is a reversible encoding, so a correct decode re-encodes to the exact original bytes.
- **Plausible wrong approach:** Trimming or adding a trailing newline before encoding changes the bytes and the round trip no longer matches.
- **How to verify:** Decoded text is DUMMY_LESSON_ONLY and its encoding equals the supplied value byte for byte.

## Exercise 2: Name the security controls

A representation format cannot replace authorization or storage protection. The actual cluster configuration and permitted identities determine exposure. The worksheet should not infer unobserved controls from the Secret kind.

**Expected:** Five distinct mechanisms and their evidence are described.

**Solution reasoning**

- **Approach:** List encoding, RBAC, encryption at rest, TLS transport and application handling with the threat each one addresses.
- **Why it is correct:** These act at different points: who can read the object, how etcd stores it, how bytes travel and what the process does with them.
- **Plausible wrong approach:** Treating base64 as protection gives it a threat it never stops, since anyone can decode it.
- **How to verify:** Five distinct mechanisms appear, and base64 is paired with no threat.

## Exercise 3: Verify the normal-worker denial

The broker combines scoped RBAC with a closed workload schema. This prevents treating denied API read as sufficient while allowing an arbitrary mounting workload. A host synthetic fixture is a separately provisioned teaching capability.

**Expected:** Both are outside the normal operation; no privilege broadening or real-value collection occurs.

**Solution reasoning**

- **Approach:** Check direct Secret reads and arbitrary Secret mounts against the worker contract.
- **Why it is correct:** The normal worker is not granted Secret access, so both attempts fall outside the operation by design.
- **Plausible wrong approach:** Requesting a broader role to make the test pass would change the contract the exercise is checking.
- **How to verify:** Both attempts are classified as outside the contract, and no extra permission is requested.

## Exercise 4: Compare environment and projected file

The same lifecycle distinction as ConfigMaps applies. A process-start snapshot is not rewritten, and a refreshed file can remain unused by a caching application. Report actual observations or label the trace synthetic.

**Expected:** Environment A persists; file may become B after observed projection; application use depends on reload.

**Solution reasoning**

- **Approach:** Assign environment, projected file and application output to three separate observations.
- **Why it is correct:** Environment variables are fixed at container start, while the kubelet can refresh a mounted Secret file, so A and B can coexist.
- **Plausible wrong approach:** Expecting the environment variable to change to B assumes the kubelet rewrites a running process's environment.
- **How to verify:** Environment shows A, file is observed separately and output depends on whether the app rereads the file.

## Exercise 5: Design nonsecret evidence

The record should support the lifecycle and access claim while minimizing exposure. Do not generalize a dummy-marker hash into a safe way to publish low-entropy real secrets.

**Expected:** Source/Pod identity, access outcome, reload behavior and synthetic equality evidence.

**Solution reasoning**

- **Approach:** Keep identities, access outcomes, reload behavior and synthetic equality checks, and no real values.
- **Why it is correct:** A reviewer can confirm the mechanism worked from outcomes and synthetic comparisons without seeing any credential.
- **Plausible wrong approach:** Saving the mounted file to prove the test ran stores secret material in the evidence record.
- **How to verify:** Every retained field is an identity, an outcome or a synthetic value.

## Exercise 6: Clean up the synthetic fixture

The host owns the temporary fixture and its data-retention policy. Cleanup must preserve replacements and unrelated objects. A missing worksheet or stopped browser is not evidence that the Secret was deleted.

**Expected:** Only recorded synthetic object UIDs are removed; normal worker permissions remain unchanged.

**Solution reasoning**

- **Approach:** List the synthetic Secret and workload UIDs from the creation record and delete only those.
- **Why it is correct:** Deleting by recorded UID cannot remove another learner's or a same-name object, and leaves worker permissions untouched.
- **Plausible wrong approach:** Deleting every Secret in the namespace would remove objects this fixture never created.
- **How to verify:** Each deleted UID appears in the creation record, and worker permissions are unchanged.

## Boundary and troubleshooting review

Base64 decoding is intentionally easy. A successful round trip proves representation fidelity, not confidentiality. A mounted file's restrictive mode does not establish server-side encryption, and an encrypted data store does not repair excessive API permissions.

The offline check makes no Secret API request. The normal browser refusal must not be bypassed through another namespace, exec command or ambient administrator context. Keep the synthetic host-lab capability and its observations explicit.
