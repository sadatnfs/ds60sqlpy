# k8s-001: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/k8s-001.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

A terminal displays requests and observations. A YAML file is saved desired-state text; it is not a running workload. Before a request changes a cluster, identify which owned disposable resource the request can affect. A context name is a convenient label for connection settings, not proof that the remote server or namespace still has the identity you expect.

The examples below are fictional reading fixtures, not real authorization receipts. The explicit host preparation operation issues an actual private lease and records cluster identity, namespace UID, ownership markers and expiry. The browser must not select an ambient current-context when that evidence is missing. A kubeconfig can contain credentials, so keep it outside source, portable learning notes and exports. [Kubernetes contexts](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/) describe connection selection; course ownership requires additional evidence.

- **terminal:** an interface to commands and their output streams
- **manifest:** saved desired-state text such as a YAML API request
- **context:** a named connection/user/namespace selection, not an ownership proof
- **UID:** a server-assigned immutable identity for one object instance
- **lease:** time-bounded permission to use explicitly owned lab resources

## Worked example / walkthrough

### Worked example 1: Inspect a fictional valid lease

A valid time comparison alone cannot establish that the selected cluster and namespace still match the receipt.

```text
fixture only, not authority
cluster_id=cluster-77
context=ds60-demo
namespace=lesson-a
namespace_uid=ns-101
expires_at=2026-10-22T12:30:00Z
inspection_time=2026-10-22T12:20:00Z
```

**Expected:** The illustrative times have10 minutes remaining, subject to identity checks.

### Worked example 2: Detect a replaced namespace

Deleting and recreating a namespace can reuse its name. A cleanup request for an old UID must not affect the replacement.

```text
receipt namespace_uid=ns-101
observed namespace_name=lesson-a
observed namespace_uid=ns-202
```

**Expected:** Reject: same name, different object instance.

## Exercises and explanatory solutions

### Exercise 1: Separate file from observation

**Inputs/evidence:** For k8s-001 Exercise 1, lessons/k8s-003.yaml and text apply accepted.

**Expected result/shape:** For k8s-001 Exercise 1, the YAML is editable desired state; the text is a tool observation.

**Verify:** For k8s-001 Exercise 1, name both categories and explain that acceptance does not prove readiness.

A saved manifest can be reviewed before any cluster exists. A response to apply says the API accepted a request, not that an application is serving traffic.

### Exercise 2: Check identity beyond names

**Inputs/evidence:** For k8s-001 Exercise 2, context ds60-demo, cluster-77, lesson-a, ns-101.

**Expected result/shape:** For k8s-001 Exercise 2, all four identity/selection values must match the host-issued receipt before a mutation.

**Verify:** For k8s-001 Exercise 2, list each compared field; do not accept a matching context name alone.

Connection names can be reused or redirected. The host receipt and observed namespace UID bind this lesson to its disposable target rather than the ambient current-context.

### Exercise 3: Reject expiry

**Inputs/evidence:** For k8s-001 Exercise 3, expires12:30Z; inspection12:31Z on the same date.

**Expected result/shape:** For k8s-001 Exercise 3, expired by1 minute; no mutation proceeds.

**Verify:** For k8s-001 Exercise 3, perform the explicit timestamp comparison and retain the refusal reason.

The fixture uses UTC instants to avoid local-time ambiguity. Re-running a command with ambient credentials is not a repair for an expired lease.

### Exercise 4: Reject replacement

**Inputs/evidence:** For k8s-001 Exercise 4, expected ns-101, observed ns-202, both named lesson-a.

**Expected result/shape:** For k8s-001 Exercise 4, identity mismatch; refuse apply and cleanup under the old receipt.

**Verify:** For k8s-001 Exercise 4, name the two unequal UIDs and state that no deletion is authorized.

The old lease does not own a newly created object merely because its name matches. This rule protects both failed-lab recovery and other learner work.

### Exercise 5: Keep credentials out of notes

**Inputs/evidence:** For k8s-001 Exercise 5, namespace UID, lease expiry, source hash, kubeconfig token.

**Expected result/shape:** For k8s-001 Exercise 5, export nonsecret receipts; exclude the credential/token.

**Verify:** For k8s-001 Exercise 5, list the excluded field and its private ephemeral storage boundary.

A useful handoff explains what target was used without granting access to it. Kubeconfig contents, bearer tokens and admin certificates are not progress notes.

### Exercise 6: Bound cleanup

**Inputs/evidence:** For k8s-001 Exercise 6, owned Deployment hello UID dep-1 versus an unrelated Deployment billing UID dep-2.

**Expected result/shape:** For k8s-001 Exercise 6, only the verified owned resource is eligible; no broad all-context deletion.

**Verify:** For k8s-001 Exercise 6, state the exact owned name/UID and reject the unrelated object.

Cleanup is another mutation and needs the same target/ownership checks as apply. A failed job does not grant permission to sweep the namespace or cluster.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.
