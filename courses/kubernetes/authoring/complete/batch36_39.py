from author import author, hello, BASE
import json, yaml

cm = {
    "apiVersion": "v1",
    "kind": "ConfigMap",
    "metadata": {"name": "recovery-record"},
    "data": {"marker": "synthetic-v1", "purpose": "teaching metadata only; not a data backup"},
}
author(
    36,
    """Kubernetes stores API state in its control-plane data store. An etcd snapshot can preserve that stored state, including object specifications and potentially sensitive values. It does not automatically copy the bytes inside an application's persistent volume. A restored Deployment or PVC object and a restored application file are therefore different recovery outcomes.

This chapter uses two synthetic inventories: an API snapshot describing a workload and its claim, and an independent data backup containing a marker. A complete recovery exercise must inspect both. A PVC can exist after API restoration while the underlying data is absent, inaccessible or from a different point in time. Likewise, correct bytes alone do not prove the application or its access controls were restored correctly.

Actual snapshot and restore operations are host-owned procedures for a dedicated synthetic cluster. The course worker does not gain etcd credentials or control-plane filesystem access. Snapshots may contain Secrets even when this particular exercise uses dummy data, so private backup material never belongs in portable progress exports, lesson fixtures or chat output.""",
    [
        (
            "Define backup scope and consistency",
            """Start with an inventory of what must be recovered: API definitions, controller versions, application configuration, volume data and any external dependencies. For each item, identify its source of truth and backup mechanism. An API snapshot is not an application-consistent database backup merely because the database Pod is represented in Kubernetes.

A live data backup may need application quiescing, transaction logs or a database-native procedure. This synthetic marker exercise avoids pretending to model those systems. Its explicit assumption is that the fixed marker is durable and unchanged at the capture point. The backup records bytes and a SHA256 digest, but a digest proves byte equality only against the recorded reference.

Record capture time, source identities, tool/version and restore prerequisites. A backup that cannot be restored in the available environment is incomplete operational protection. Check access restrictions and retention separately from checksum integrity; a valid backup can still be exposed to the wrong reader.""",
        ),
        (
            "Restore into an isolated target and verify both layers",
            """The host procedure must identify source and destination cluster ownership before any restore. It uses a dedicated destination and fixed operations, rather than replacing the active context or writing over a shared cluster. Control-plane restore has version-specific details, including controller cache and revision behavior, that belong to the qualified runbook and tooling.

After API restoration, inspect the expected workload and claim relationships. Then restore the application marker using the separate data procedure and verify its hash through a read-only application path. A control-plane snapshot cannot supply missing volume bytes by itself. Keep the API-object and data-hash checks as separate pass/fail rows.

Finally test the ordinary service path and least-privilege access expectations. Recovery should not silently disable admission or grant broad credentials to make the application appear healthy. Retain the exact source/target mapping and cleanup plan, but keep private snapshots and credentials out of the public evidence packet.""",
        ),
        (
            "Recognize incomplete recovery",
            """If the API object exists but the marker hash is wrong, recovery has not met the application-data contract. If the marker is correct but the Service route is broken, recovery has not met the serving contract. A Ready Pod alone proves neither complete restoration nor acceptable data loss.

Never use a live production snapshot as a convenient classroom fixture. The synthetic rehearsal makes scope visible while avoiding personal or organizational data. A passed rehearsal establishes the tested procedure and version combination, not universal restore compatibility.""",
        ),
    ],
    [
        (
            "Separate two backup inventories",
            """API inventory: Deployment hello, PVC data-store-0, their specifications and stored metadata. Data inventory: marker bytes b'synthetic-v1' and its recorded SHA256. Only the second inventory contains the marker bytes.""",
            "Restoring the API inventory alone cannot satisfy the marker-data check.",
        ),
        (
            "Diagnose a partial restore",
            """Synthetic destination has the expected Deployment and claim. Its marker is b'empty-replacement' rather than b'synthetic-v1'. The Pod is Ready. The data hash comparison fails.""",
            "The recovery is incomplete despite API presence and readiness; the independent data restore is required.",
        ),
    ],
    [
        (
            "Build the source inventory",
            "Assign API objects and persistent marker bytes to their backup sources.",
            "Two distinct sources and restore checks.",
            "Ask where each byte is actually stored.",
            "The API data store records Kubernetes state, while workload data can live in a separate storage system. Treating the claim object as the file backup confuses a reference to storage with the contents of that storage.",
        ),
        (
            "Record a synthetic data checksum",
            "Hash the fixed marker and compare it with a changed marker.",
            "Equal bytes match; changed bytes fail the reference digest.",
            "Keep the reference independent from the restored copy.",
            "Recomputing both expected and actual from the restored file would make the check meaningless. The expected digest belongs to the captured backup record, and the read-only verification must inspect the restored application path.",
        ),
        (
            "Define consistency assumptions",
            "State why the immutable marker is simpler than a live transactional database.",
            "No claim of database-consistent backup or log replay.",
            "Concurrent writes change the backup problem.",
            "The fixture deliberately holds data constant so the learner can isolate restoration boundaries. A real database requires its own consistency and recovery design, which cannot be inferred from a successful marker copy.",
        ),
        (
            "Evaluate the partial restore",
            "Accept API objects but reject the wrong data hash in the supplied trace.",
            "Overall recovery fails until both API and data gates pass.",
            "Ready does not mean correct data.",
            "The separate failure row prevents a misleading success report. It also points to the correct repair path: investigate or repeat the qualified data restoration, rather than merely restarting an already Ready Pod.",
        ),
        (
            "Protect backup material",
            "Classify private snapshots, credentials and public receipt fields.",
            "No snapshots or secrets in portable progress; only bounded metadata and synthetic checksums.",
            "API snapshots can include sensitive objects.",
            "Operational evidence should identify the procedure and outcome without copying the source of sensitive data. Access, encryption and retention belong to the host backup contract and are distinct from the classroom checksum exercise.",
        ),
        (
            "Review target isolation and cleanup",
            "Document the dedicated source/destination ownership and eventual disposal.",
            "No restore into an ambient or shared target; exact owned cleanup.",
            "A restore is a state replacement operation.",
            "The host must prove the intended destination before executing a restore and retain a recovery path for failures. The lesson worksheet alone never authorizes arbitrary control-plane changes or deletion of unrelated volumes.",
        ),
    ],
    [cm],
    """
import hashlib

def digest(value):return hashlib.sha256(value).hexdigest()
def recovered(api_objects,marker,expected):return {'Deployment/hello','PVC/data-store-0'}<=set(api_objects) and digest(marker)==expected

def main():
    expected=digest(b'synthetic-v1');objects=['Deployment/hello','PVC/data-store-0']
    assert not recovered(objects,b'empty-replacement',expected)
    assert not recovered([],b'synthetic-v1',expected)
    assert recovered(objects,b'synthetic-v1',expected)
    print('k8s-036 independent synthetic API/data gates passed; no snapshot or restore executed')

if __name__ == "__main__":
    main()
""",
    capability="dedicated synthetic control-plane snapshot/restore plus independent application-data backup",
    refs=[
        "[Operating etcd for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)",
        "[etcd disaster recovery](https://etcd.io/docs/v3.6/op-guide/recovery/)",
    ],
)

author(
    37,
    """A Kubernetes upgrade is a compatibility and state-transition problem, not merely a change to a version string. The API server, kubelet, kubectl, controllers, networking and storage components have supported version relationships. The Kubernetes version-skew policy describes bounds for core components, while a deployment tool or extension can impose additional restrictions.

This course uses a replacement-cluster rehearsal: the host prepares two separately owned, pinned clusters, called source and destination in the evidence packet. Synthetic manifests and data are rendered and tested against each. The exercise does not perform an in-place production upgrade and does not demonstrate high-availability control-plane maintenance. A small kind environment is useful for API and fixture compatibility, but its results have that explicit scope.

The normal runtime currently qualifies one pinned stack. A second stack is unavailable until the host supplies its exact node-image digest, tool versions and compatibility receipt. Never invent a destination version or download one during a lesson. The offline matrix uses symbolic versions A and B so that a teaching trace cannot be confused with a tested release pair.""",
    [
        (
            "Build a compatibility matrix before migration",
            """For each rendered object, record apiVersion, kind and any feature-dependent fields. Ask whether both API servers serve that version and whether schema/defaulting behavior changes. A YAML file that parses locally can still be rejected by the destination API. A server dry-run can check important request paths, but it does not prove a controller or application will function.

Include CRD schemas, conversion behavior, controller images, admission policies, Gateway/CNI and storage-driver contracts when the workload uses them. The application can fail even when every built-in object is accepted. A deprecated API still served on source may be removed on destination; changing apiVersion may require field and behavior changes rather than a text substitution.

Consult the version-skew policy for the exact component releases before the host qualifies a pair. Do not infer compatibility because two versions share the same major number. Record actual tools and server versions in the receipt, and distinguish supported combinations from combinations that merely happened to start.""",
        ),
        (
            "Rehearse replacement with reversible routing",
            """Render the same reviewed application intent for source and destination. Verify the intended differences, such as owned namespace identity, without carrying stale UIDs or status fields as desired configuration. Restore only synthetic data into the destination and compare the independent marker hash.

Run destination admission, controller, application and data checks before considering traffic movement. A successful API dry-run is an early gate, not final acceptance. If a required controller is missing, mark the destination blocked rather than disabling the feature or granting a learner broad permissions.

Keep source available until the declared acceptance and rollback window is complete. The routing change needs its own qualified path and identity checks. A rollback after new writes may have a data-consistency problem even if the old cluster is still running; this immutable-marker rehearsal does not model bidirectional live writes.""",
        ),
        (
            "Keep version claims evidence-based",
            """The example matrix is a method for organizing evidence, not a certification for arbitrary Kubernetes releases. A passed A/B marker test says nothing about untested plugins, workload APIs or production failure domains.

Do not treat replacement as a universal substitute for an upgrade procedure. Production systems require their own maintenance order, availability, storage, rollback and support decisions. Here the deliverable is a concrete compatibility packet for a bounded synthetic workload and exact host-qualified versions.""",
        ),
    ],
    [
        (
            "Read a four-gate matrix",
            """Synthetic A: API pass,controller pass,application pass,data pass. Synthetic B before preparation: API pass,controller unavailable,application unavailable,data not restored. The second row is not accepted merely because its API gate passed.""",
            "B remains unavailable until all required capability and acceptance rows have evidence.",
        ),
        (
            "Find a migration defect",
            """After data restore, B accepts the Deployment and serves /version, but the marker digest differs from A's captured digest. The destination is not promoted. Correct the qualified restore and rerun the independent data gate.""",
            "Application response and data compatibility are separate; promotion remains blocked by the wrong digest.",
        ),
    ],
    [
        (
            "List exact version inputs",
            "Name server,node image,client,controller and storage/network versions needed in a receipt.",
            "A concrete pinned stack rather than a generic latest label.",
            "Extensions have compatibility contracts too.",
            "The core skew policy is only one part of the environment. A reproducible rehearsal identifies the actual components and immutable artifacts so another host can understand what was tested and what remains outside scope.",
        ),
        (
            "Audit API usage",
            "Extract apiVersion and kind from the reviewed manifests and identify destination checks.",
            "Every used API/feature has a server acceptance row.",
            "Local YAML parsing is not API discovery.",
            "This inventory exposes removed APIs and feature fields before application testing. A simple textual version replacement can miss changed schemas or semantics, so validation needs the actual destination API contract.",
        ),
        (
            "Evaluate the incomplete matrix",
            "Read B with API pass but controller unavailable.",
            "Destination not accepted; controller capability remains missing.",
            "One successful layer does not stand in for all layers.",
            "The matrix prevents an early check from being inflated into overall readiness. A missing controller is explicit work for the host qualification process, not an excuse to invent its effects in a worksheet.",
        ),
        (
            "Compare synthetic data",
            "Check destination marker against the independently captured source hash.",
            "Mismatch blocks promotion even when /version succeeds.",
            "Keep data lineage separate from image/version output.",
            "The application can run with empty or wrong storage. The marker is a small but concrete data contract that catches this class of migration defect without pretending to represent a full database migration.",
        ),
        (
            "Design a rollback boundary",
            "Explain when source can be released and what new destination writes would change.",
            "Source retained through the stated window; mutable-data rollback is outside this immutable fixture.",
            "Routing reversal does not reverse data history.",
            "The controlled example has a fixed marker, so rollback reasoning is simple. A real write-producing workload requires a plan for divergence and data compatibility, which cannot be solved by keeping an old cluster name alone.",
        ),
        (
            "Write the qualification conclusion",
            "Distinguish replacement rehearsal from in-place upgrade and production HA.",
            "Only the exact tested stack and synthetic workload gates are claimed.",
            "Name untested plugins and failure modes.",
            "The conclusion should be useful without exaggeration: it can establish specific API and application compatibility, expose missing capabilities and preserve a repeatable packet, while leaving broader production upgrade design to its own procedure.",
        ),
    ],
    hello(True),
    """
REQUIRED={'api','controller','application','data'}
def accepted(row):return all(row.get(k)=='pass' for k in REQUIRED)

def main():
    a={k:'pass' for k in REQUIRED}
    b={'api':'pass','controller':'unavailable','application':'unavailable','data':'missing'}
    assert accepted(a) and not accepted(b)
    assert not accepted({**a,'data':'wrong-hash'})
    assert accepted({**a,'stack':'qualified-symbolic-B'})
    print('k8s-037 synthetic compatibility gates passed; no version pair or upgrade qualified')

if __name__ == "__main__":
    main()
""",
    capability="two separately owned pinned stacks with API/controller/storage compatibility receipts",
    refs=[
        "[Kubernetes version skew policy](https://kubernetes.io/releases/version-skew-policy/)",
        "[Kubernetes API deprecation guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)",
        "[kind node-image documentation](https://kind.sigs.k8s.io/docs/user/quick-start/#creating-a-cluster)",
    ],
)

provenance = BASE / "fixtures/provenance"
(provenance / "README.md").write_text("""# Synthetic offline signature fixture

This is a real RSA/SHA256 signature over attestation.json, created solely for this course. The public key identifies a synthetic course publisher by the local trust decision, not a real registry or organization. No private key is stored. The attestation names synthetic content; it is not an OCI image manifest or a Sigstore bundle.

The immutable receipt records the public-key digest and the authoring verifier. Verification must check both the original positive case and attestation-tampered.json. The tiny Python chapter check verifies content hashing only. Use a qualified OpenSSL-compatible CLI for actual signature verification, as shown in the guide. Do not regenerate or replace the key to make a failed verification pass.
""")
author(
    38,
    """A digest identifies bytes under a hash algorithm. It can detect a change when compared with an independently trusted expected digest, but it does not tell you who published the bytes. A signature adds a claim verifiable under a public key. That still leaves a trust question: why is this key authorized to speak for the publisher or artifact you care about?

The local fixture contains a real RSA/SHA256 signature, a public key, an attestation and a tampered copy. The signing private key was used only in memory during authoring and is not included. This demonstrates actual offline cryptographic verification of a synthetic statement. It is not an OCI image signature, a Sigstore bundle, a certificate chain or evidence that a real organization published an image.

The attestation states a digest for synthetic fixture bytes. Verification has two joins: the signature must validate the attestation under the chosen public key, and the attested content digest must match the actual artifact being evaluated. A valid signature over an unrelated artifact is not authorization to run the current image. Admission enforcement is another boundary: successfully verifying a file offline does not mean the cluster will require that verification.""",
    [
        (
            "Inspect the signed statement and trust input",
            """[The fixture directory](../fixtures/provenance/README.md) contains attestation.json, attestation.sig, publisher-public.txt, attestation-tampered.json and receipt.json. JSON formatting is part of the signed byte sequence here. Changing whitespace can invalidate this signature because the scheme signs the exact file bytes rather than a canonicalized semantic object.

The public-key SHA256 in the receipt identifies the exact trusted verification input for this exercise. A malicious actor who can replace both an artifact and the trusted public key can produce a self-consistent new pair. Trust roots therefore must come from a reviewed channel independent of the untrusted artifact. A checksum stored next to an untrusted file has the same limitation if both can be replaced.

The synthetic attestation includes a publisher label for teaching. The label is not independently authenticated by a real organization or transparency service. Treat the key as a local course trust root only. Production provenance may include signer identity, build process, source revision and policy constraints, all requiring their own validation.""",
        ),
        (
            "Run actual offline signature verification",
            """If an OpenSSL-compatible CLI has already been qualified on your host, run the following command from the repository root. It is identical in POSIX and PowerShell because it contains no shell-specific expansion. Do not install a tool during an offline lesson.

```text
openssl dgst -sha256 -verify courses/kubernetes/fixtures/provenance/publisher-public.txt -signature courses/kubernetes/fixtures/provenance/attestation.sig courses/kubernetes/fixtures/provenance/attestation.json
```

Expected: verification succeeds and the process exit code is0. Run the same command with attestation-tampered.json as the final argument. Expected: verification fails and the exit code is nonzero. In POSIX inspect `$?` immediately after the command; in PowerShell inspect `$LASTEXITCODE`. Do not judge success from a banner alone.

The authoring receipt records both outcomes using LibreSSL3.3.6's OpenSSL-compatible command. This is an actual local cryptographic test, distinct from the standard-library hash checker linked below. A different qualified verifier should repeat both controls before being used for live policy decisions.""",
        ),
        (
            "Connect verification to deployment cautiously",
            """An OCI image digest identifies a registry manifest or index under the image-distribution contract, not the arbitrary synthetic string used here. Multi-platform indices and platform-specific manifests also need explicit interpretation. The current course image tag0.2.0 remains a runtime allowlist identity, not a signature-based admission policy.

A full image-provenance lab requires prewarmed real image digest and signature/bundle material, an offline-qualified verification tool and a host policy that binds the verified subject to the submitted image. Those capabilities are not supplied by this synthetic signature exercise. Never fetch new trust data silently or replace a failed trusted key with one found in the rejected artifact.""",
        ),
    ],
    [
        (
            "Compare hashing and publisher trust",
            """Compute SHA256 of b'fixture-bytes-v1'. A matching expected digest establishes byte equality under the algorithm. A second file can carry the same printed publisher label while having a different digest or an invalid signature.""",
            "Content integrity and publisher authorization are separate checks; a label or digest alone does not establish authorship.",
        ),
        (
            "Verify original and tampered signed bytes",
            """Use the two CLI invocations above with the same public key and signature. Only the input attestation changes from schema1 to schema2. The original succeeds and the modified file fails.""",
            "The tamper control demonstrates that verification depends on the signed bytes; this is a synthetic publisher test, not real image provenance certification.",
        ),
    ],
    [
        (
            "Identify trust inputs",
            "List payload,signature,public key and expected content digest.",
            "Four distinct roles with an independently chosen trust key.",
            "Do not obtain the trusted key from the untrusted payload itself.",
            "A signature check is meaningful only relative to a trust decision. The course fixes a synthetic public key so the mathematical verification can be tested while making clear that no real organizational publisher identity is established.",
        ),
        (
            "Check content integrity",
            "Compare the original synthetic content hash with a changed byte sequence.",
            "Different content produces a different expected comparison result.",
            "Hash the exact bytes with the declared algorithm.",
            "The digest comparison must use an independent expected value. Computing a fresh digest and merely printing it is not an integrity check, because there is nothing trusted to compare it against.",
        ),
        (
            "Verify the positive signature",
            "Run the qualified CLI over attestation.json with the fixed key/signature.",
            "Exit0 plus successful verification output, with tool identity recorded.",
            "Use the exact signed file bytes.",
            "This is the cryptographic positive control. The standard-library chapter checker cannot replace it because it only computes hashes. Keep the tool version and trust input fingerprint with the receipt for reproducibility.",
        ),
        (
            "Verify the tamper negative",
            "Repeat against attestation-tampered.json without changing key or signature.",
            "Nonzero exit and verification failure.",
            "Hold trust inputs constant.",
            "The negative control catches a verifier invocation that accidentally ignores the signature or checks the wrong file. Re-signing the modified file or replacing the public key would destroy the intended experiment.",
        ),
        (
            "Join signature subject to artifact",
            "Explain why a valid signed statement about artifactA does not approve artifactB.",
            "The signed subject digest must match the actual artifact under the correct format contract.",
            "Verification is not transferable to arbitrary bytes.",
            "A signature authenticates a statement under its trust assumptions. Deployment authorization also requires matching that statement to the artifact being deployed and applying the intended policy, rather than accepting any valid signature.",
        ),
        (
            "State enforcement and offline limits",
            "Compare this local signature check with OCI/Sigstore provenance and admission enforcement.",
            "Synthetic RSA fixture only; real image and cluster policy qualification remain separate.",
            "Local verification does not install an admission rule.",
            "The report should state exactly which algorithm, key and payload were tested. It should not claim registry provenance, transparency-log validation or enforced cluster protection without the corresponding real materials and runtime receipts.",
        ),
    ],
    hello(),
    """
import hashlib,json
from pathlib import Path

def main():
    base=Path(__file__).resolve().parents[1]/'fixtures/provenance'
    statement=json.loads((base/'attestation.json').read_text())
    content=b'fixture-bytes-v1'
    assert hashlib.sha256(content).hexdigest()==statement['content_sha256']
    assert hashlib.sha256(content+b'!').hexdigest()!=statement['content_sha256']
    assert (base/'attestation.json').read_bytes()!=(base/'attestation-tampered.json').read_bytes()
    assert b'PRIVATE KEY' not in (base/'publisher-public.txt').read_bytes()
    print('k8s-038 content-hash checks passed; use the documented qualified CLI for signature verification')

if __name__ == "__main__":
    main()
""",
    capability="qualified offline image-digest/signature verification and separate host admission enforcement",
    refs=[
        "[OpenSSL dgst verification](https://docs.openssl.org/3.0/man1/openssl-dgst/)",
        "[OCI image descriptor digest](https://github.com/opencontainers/image-spec/blob/main/descriptor.md)",
        "[Sigstore verification overview](https://docs.sigstore.dev/cosign/verifying/verify/)",
    ],
)

author(
    39,
    """A namespace organizes namespaced API resources and supports scoped policy decisions. It is not a virtual machine, a separate kernel or a complete boundary against arbitrary hostile code. Multitenancy design starts by naming the actors and threats: accidental edits, credential misuse, resource exhaustion, network access, filesystem access and runtime escape have different controls.

The course combines a fixed source schema, an exact owned lease, namespace-scoped credentials, restricted container settings, allowed images and bounded cleanup. These controls reduce the permitted operation surface. The normal worker has no engine socket, no ambient cluster selection, no Secret access or arbitrary exec. Advanced host capabilities are separate precisely because they can cross the ordinary namespace boundary.

A threat review should map each behavior to a control and a negative test. Saying secure because namespaces are different is too vague. Conversely, a local parser rejection does not establish that RBAC, admission or network enforcement would independently deny the same request. Preserve the evidence layer for each result.""",
    [
        (
            "Map threats to independent boundaries",
            """An attempt to choose another namespace should fail the owned-target/source contract and lack cross-namespace authorization. An attempt to create privileged containers or hostPath mounts should fail the closed manifest schema and relevant host admission policy. An attempt to read another tenant's Secret belongs to authorization and credential scope, not to network routing alone.

Resource requests, limits, quotas and operation deadlines address different forms of consumption. A CPU limit does not bound the number of API objects an unrestricted caller can create. A namespace quota does not prove a process cannot reach a network destination. A finite allowlisted operation can be reasoned about more concretely than arbitrary shell execution.

NetworkPolicy requires an enforcing network implementation and paired traffic tests. Application authentication remains separate. The fact that a packet reaches a Service says nothing about whether the caller should receive a particular record. Storage access modes likewise do not replace data authorization or encrypted backup handling.""",
        ),
        (
            "Review adversarial inputs without executing them",
            """Use supplied field-level counterexamples: metadata.namespace set to foreign, securityContext.privileged true, volume hostPath, image unapproved, serviceAccountName other-tenant, or a command invoking an arbitrary shell. The normal adapter should reject these inputs before scheduling. The exercise inspects rejection reasons; it does not run the malicious workload to see what happens.

A defense-in-depth review asks which additional layer would apply if the first parser were bypassed. Host policy and credentials should remain narrow, but do not claim that a layer was tested without its own independent fixture. The runtime's UID and nonce checks also protect observation and cleanup from same-name foreign objects.

Privileged host operators and engine administrators are a distinct trust domain. Namespace controls cannot constrain someone who already controls the container engine or cluster host. Keep those credentials outside learner processes and logs. The classroom's owned kind isolation is an operational scope boundary, not a proof of resistance to every kernel-level attack.""",
        ),
        (
            "Make the conclusion useful and bounded",
            """Report the allowed operations, forbidden surfaces, observed negative cases and remaining assumptions. A clear boundary statement can support safe classroom use without claiming general hostile multitenant hosting.

Do not widen permissions to demonstrate a forbidden action live. Do not collect another lease's tokens as evidence. An authorization denial can be observed using the scoped test identity and a known synthetic target without exposing credentials or unrelated data.""",
        ),
    ],
    [
        (
            "Assign controls to proposed actions",
            """foreign namespace: source/lease binding plus RBAC. hostPath: manifest allowlist plus admission/runtime policy. Secret read: RBAC and credential scope. CPU exhaustion: resource/operation bounds. Cross-Pod traffic: enforcing network policy plus application authorization as needed.""",
            "Each threat names a relevant control; no single namespace setting covers the entire matrix.",
        ),
        (
            "Distinguish evidence layers",
            """Synthetic result A: hostPath YAML refused locally. Result B: independent server admission test refuses privileged container. Result C: paired traffic clients confirm an allowed/denied path in a qualified CNI.""",
            "A,B,C are three separate controls. None should be relabeled as proof that every other layer was exercised.",
        ),
    ],
    [
        (
            "Write a threat model",
            "Name learner,host operator and unrelated tenant, with their trusted capabilities.",
            "Actors and assets are explicit rather than a blanket secure claim.",
            "Start with who can submit what.",
            "The host operator has powers the learner deliberately lacks. Distinguishing those actors prevents a namespace boundary from being misrepresented as protection against the administrator who controls the host or credentials.",
        ),
        (
            "Classify six adversarial fields",
            "Map foreign namespace,privileged,hostPath,unapproved image,foreign service account and shell command to rejections.",
            "Every field has a named closed-schema or ownership rule.",
            "Inspect fields rather than executing the payload.",
            "The rejected shapes are concrete and reviewable. A successful local negative test shows the broker source boundary, while independent API and runtime controls require their own evidence and should not be inferred automatically.",
        ),
        (
            "Review credential exposure",
            "Explain why tokens,engine sockets and ambient kubeconfig stay outside learner artifacts.",
            "No alternate path around the bounded operation API.",
            "A hidden broad credential can defeat a narrow UI.",
            "The effective boundary includes the process environment and mounts, not just the manifest form. A learner-facing API that rejects unsafe YAML is insufficient if the same process can directly reach an unrestricted engine socket.",
        ),
        (
            "Separate resource and network controls",
            "Compare CPU limits,quota,deadlines and NetworkPolicy.",
            "Each constrains a different resource or traffic dimension.",
            "Do not substitute one control for another.",
            "CPU limits constrain execution consumption, quotas constrain admitted object/resource totals, deadlines bound operations, and network policy governs supported traffic paths. Their effectiveness and failure modes must be tested separately.",
        ),
        (
            "Inspect cleanup identity defenses",
            "Compare a same-name object with a different UID/nonce to the operation receipt.",
            "Foreign object preserved and cleanup reports the mismatch.",
            "Names can be reused by another operation.",
            "Cleanup is itself a security-sensitive action. Ownership labels, nonce and UID preconditions prevent a stale operation from deleting a replacement or unrelated object after a race or partial failure.",
        ),
        (
            "State residual assumptions",
            "Write the final classroom isolation statement and untested threats.",
            "No arbitrary-code or VM-equivalent isolation claim; host trust and qualified controls are named.",
            "A bounded allowed workload is a smaller claim.",
            "The conclusion should tell an instructor what was actually established and what would need a different design. It preserves useful assurance while avoiding an unsupported promise about hostile tenants or kernel vulnerabilities.",
        ),
    ],
    hello(),
    """
CONTROLS={'foreign-namespace':'lease+RBAC','privileged':'schema+admission','hostPath':'schema+admission','unapproved-image':'schema+image-allowlist','foreign-service-account':'schema+RBAC','shell':'fixed-command'}

def owned(expected,obj):return all(obj.get(k)==v for k,v in expected.items())

def main():
    assert len(CONTROLS)==6 and all(CONTROLS.values())
    expected={'uid':'u1','nonce':'n1','owner':'lesson'}
    assert owned(expected,dict(expected))
    assert not owned(expected,{**expected,'uid':'u2'})
    assert not owned(expected,{**expected,'nonce':'foreign'})
    print('k8s-039 threat mapping and identity model passed; no adversarial workload executed')

if __name__ == "__main__":
    main()
""",
    capability="exclusive synthetic threat fixtures with separate parser, RBAC, admission and CNI evidence",
    refs=[
        "[Kubernetes multitenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)",
        "[Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)",
        "[RBAC good practices](https://kubernetes.io/docs/concepts/security/rbac-good-practices/)",
    ],
)
