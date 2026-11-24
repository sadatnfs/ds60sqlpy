# k8s-017: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A container security context describes requested process and filesystem restrictions. Running as a nonroot UID, dropping capabilities, disallowing privilege escalation and using a read-only root filesystem reduce different risks. Pod Security admission is a separate policy that can reject workloads not meeting a chosen standard. Neither a namespace name nor one security field creates complete isolation by itself.

The allowed browser workload uses runAsUser 65532, runAsNonRoot true, RuntimeDefault seccomp, allowPrivilegeEscalation false, readOnlyRootFilesystem true and capabilities.drop ALL. Service-account token mounting is disabled. The parser rejects attempts to replace these values or add host namespaces, privileged mode and unapproved mounts.

This lesson distinguishes source checks, admission decisions and actual runtime identity. The configured UID is desired process identity; an observed runtime UID requires a qualified fixture or host observation. The current app's admitted baseline and ownership checks do not automatically prove every host/kernel security property.

## Exercise 1: Map each control

The controls reduce different attack or error surfaces. Understanding their roles helps diagnose a legitimate application permission issue without removing every restriction.

**Expected:** Each field is connected to its specific mechanism rather than one generic secure label.

**Solution reasoning**

- **Approach:** Pair each securityContext field with the specific path it closes.
- **Why it is correct:** runAsNonRoot blocks UID 0, dropped capabilities remove kernel privileges, allowPrivilegeEscalation false blocks setuid gains, seccomp limits syscalls and readOnlyRootFilesystem blocks image writes.
- **Plausible wrong approach:** Labeling all five as generic hardening hides that, for example, dropping capabilities does nothing to stop writes to the root filesystem.
- **How to verify:** Five fields map to five different attack paths.

## Exercise 2: Run the allowed baseline

The app proves its bounded workload checks. A runtime UID claim needs a dedicated observed field or fixed fixture result, not merely the YAML value. Do not broaden that receipt into a host-isolation guarantee.

**Expected:** Accepted source, observed workload readiness and owned cleanup are recorded.

**Solution reasoning**

- **Approach:** Run the unchanged nonroot source and keep configured and observed identity in separate rows.
- **Why it is correct:** The manifest states runAsUser, but only a host readback shows the identity the process actually ran with.
- **Plausible wrong approach:** Copying runAsUser from the YAML into the observed row reports configuration as if it were runtime evidence.
- **How to verify:** Accepted source, readiness, cleanup and two identity rows with distinct sources are recorded.

## Exercise 3: Reject a privileged mutation

The course protects the operation at source admission. This is a valid negative result even though no privileged process ran. Preserve the phase rather than inventing a server rejection event.

**Expected:** The course parser refuses the source before any cluster request. Under Pod Security Admission, privileged: true violates the Baseline level and allowPrivilegeEscalation: true violates the Restricted level.

**Solution reasoning**

- **Approach:** Change one field in a scratch copy and submit it to the course parser.
- **Why it is correct:** The parser refuses either field locally, and Pod Security marks privileged true as a Baseline violation and allowPrivilegeEscalation true as a Restricted violation.
- **Plausible wrong approach:** Claiming Baseline would reject allowPrivilegeEscalation true misplaces that control, since only Restricted forbids it.
- **How to verify:** A refusal message exists, no create receipt exists and the matching Pod Security level is named.

## Exercise 4: Reject host access

A secure-looking container context does not neutralize a host namespace or mount. The parser rejects those requests rather than trusting a learner to choose a harmless path.

**Expected:** hostPath volumes, hostNetwork and hostPID violate the Baseline standard, so a namespace enforcing baseline or restricted rejects them at admission; the classroom parser rejects them even earlier.

**Solution reasoning**

- **Approach:** Classify hostPath, hostNetwork and hostPID against the Pod Security Standards controls.
- **Why it is correct:** All three expose the node: hostPath reaches its filesystem, hostNetwork its network stack and hostPID its process table, so Baseline forbids each.
- **Plausible wrong approach:** Assuming only Restricted blocks host access would let a baseline namespace admit them, which it does not.
- **How to verify:** Each variant cites its control and Baseline as the lowest forbidding level.

## Exercise 5: Observe a host policy separately

The host capability must establish the admission configuration. A successful or denied API request then provides evidence about that policy under the current target. The worker receives no permission to relabel the namespace or install policy.

**Expected:** Policy version, namespace UID and actual admission reason accompany the result.

**Solution reasoning**

- **Approach:** Read the enforce and enforce-version labels first, then send one allowed and one denied request.
- **Why it is correct:** Admission depends on the namespace's enforced level and version, so the result is meaningful only alongside those labels.
- **Plausible wrong approach:** Reporting a denial without the namespace labels cannot show which policy produced it.
- **How to verify:** Labels, namespace UID and the API server's denial reason are recorded together.

## Exercise 6: Write a bounded threat statement

A useful security explanation names mechanisms and limits. It should distinguish desired configuration, admission, container runtime behavior and application authorization rather than collapse them into an unsupported safe/unsafe binary.

**Expected:** For example, RBAC controls API access while network policy or application auth addresses different paths.

**Solution reasoning**

- **Approach:** Name what the fixed controls limit and one threat outside them with its control.
- **Why it is correct:** The securityContext limits what the container process can do on the node, not which API calls or network peers it can reach.
- **Plausible wrong approach:** Calling the workload secure overall implies coverage of API access and network paths these fields never touch.
- **How to verify:** The statement names one uncovered threat and the separate control, such as RBAC or a NetworkPolicy.

## Boundary and troubleshooting review

A read-only filesystem is not a ban on all writes when writable volumes exist. Nonroot is not an authorization policy for another namespace. RBAC does not govern every packet sent by a workload. A container shares a node kernel and is not automatically a separate virtual machine.

State which control rejects which behavior and what remains untested. If a negative source is refused locally, do not claim that a kernel-level action was attempted or blocked at runtime. The evidence level is part of the security explanation.
