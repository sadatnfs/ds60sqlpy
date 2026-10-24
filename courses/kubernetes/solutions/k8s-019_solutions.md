# k8s-019: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Secret is a Kubernetes object for data that requires restricted handling. Its data field uses base64 encoding, which is a reversible representation rather than encryption. Access control, encryption-at-rest configuration, transport security and application handling are separate controls. Verify those actual controls instead of inferring confidentiality from the object kind.

This lesson uses only the public markers DUMMY_LESSON_ONLY and DUMMY_LESSON_ROTATED. The current browser worker has no Secret permission and does not accept Secret manifests or Secret references. Live mount behavior is available only through a teacher-provided synthetic fixture in a separate scoped host capability. No real credential is needed or should be collected.

Configuration lifetime still matters. A Secret-derived environment value is captured when a process starts. A projected Secret file can refresh asynchronously, but application reload behavior determines when the process uses new bytes. Encoding does not change those lifecycle semantics.

## Exercise 1: Decode the authored marker

The result demonstrates that base64 is reversible. It should not be described as decryption or as proof of a security boundary. The literal marker is intentionally harmless teaching data.

**Expected:** Exact DUMMY_LESSON_ONLY round trip.

## Exercise 2: Name the security controls

A representation format cannot replace authorization or storage protection. The actual cluster configuration and permitted identities determine exposure. The worksheet should not infer unobserved controls from the Secret kind.

**Expected:** Five distinct mechanisms and their evidence are described.

## Exercise 3: Verify the normal-worker denial

The broker combines scoped RBAC with a closed workload schema. This prevents treating denied API read as sufficient while allowing an arbitrary mounting workload. A host synthetic fixture is a separately provisioned teaching capability.

**Expected:** Both are outside the normal operation; no privilege broadening or real-value collection occurs.

## Exercise 4: Compare environment and projected file

The same lifecycle distinction as ConfigMaps applies. A process-start snapshot is not rewritten, and a refreshed file can remain unused by a caching application. Report actual observations or label the trace synthetic.

**Expected:** Environment A persists; file may become B after observed projection; application use depends on reload.

## Exercise 5: Design nonsecret evidence

The record should support the lifecycle and access claim while minimizing exposure. Do not generalize a dummy-marker hash into a safe way to publish low-entropy real secrets.

**Expected:** Source/Pod identity, access outcome, reload behavior and synthetic equality evidence.

## Exercise 6: Clean up the synthetic fixture

The host owns the temporary fixture and its data-retention policy. Cleanup must preserve replacements and unrelated objects. A missing worksheet or stopped browser is not evidence that the Secret was deleted.

**Expected:** Only recorded synthetic object UIDs are removed; normal worker permissions remain unchanged.

## Boundary and troubleshooting review

Base64 decoding is intentionally easy. A successful round trip proves representation fidelity, not confidentiality. A mounted file's restrictive mode does not establish server-side encryption, and an encrypted data store does not repair excessive API permissions.

The offline check makes no Secret API request. The normal browser refusal must not be bypassed through another namespace, exec command or ambient administrator context. Keep the synthetic host-lab capability and its observations explicit.
