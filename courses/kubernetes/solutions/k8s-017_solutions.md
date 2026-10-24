# k8s-017: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A container security context describes requested process and filesystem restrictions. Running as a nonroot UID, dropping capabilities, disallowing privilege escalation and using a read-only root filesystem reduce different risks. Pod Security admission is a separate policy that can reject workloads not meeting a chosen standard. Neither a namespace name nor one security field creates complete isolation by itself.

The allowed browser workload uses runAsUser65532, runAsNonRoot true, RuntimeDefault seccomp, allowPrivilegeEscalation false, readOnlyRootFilesystem true and capabilities.drop ALL. Service-account token mounting is disabled. The parser rejects attempts to replace these values or add host namespaces, privileged mode and unapproved mounts.

This lesson distinguishes source checks, admission decisions and actual runtime identity. The configured UID is desired process identity; an observed runtime UID requires a qualified fixture or host observation. The current app's admitted baseline and ownership checks do not automatically prove every host/kernel security property.

## Exercise 1: Map each control

The controls reduce different attack or error surfaces. Understanding their roles helps diagnose a legitimate application permission issue without removing every restriction.

**Expected:** Each field is connected to its specific mechanism rather than one generic secure label.

## Exercise 2: Run the allowed baseline

The app proves its bounded workload checks. A runtime UID claim needs a dedicated observed field or fixed fixture result, not merely the YAML value. Do not broaden that receipt into a host-isolation guarantee.

**Expected:** Accepted source, observed workload readiness and owned cleanup are recorded.

## Exercise 3: Reject a privileged mutation

The course protects the operation at source admission. This is a valid negative result even though no privileged process ran. Preserve the phase rather than inventing a server rejection event.

**Expected:** Parser refusal before cluster mutation.

## Exercise 4: Reject host access

A secure-looking container context does not neutralize a host namespace or mount. The parser rejects those requests rather than trusting a learner to choose a harmless path.

**Expected:** All are outside the admitted browser contract.

## Exercise 5: Observe a host policy separately

The host capability must establish the admission configuration. A successful or denied API request then provides evidence about that policy under the current target. The worker receives no permission to relabel the namespace or install policy.

**Expected:** Policy version, namespace UID and actual admission reason accompany the result.

## Exercise 6: Write a bounded threat statement

A useful security explanation names mechanisms and limits. It should distinguish desired configuration, admission, container runtime behavior and application authorization rather than collapse them into an unsupported safe/unsafe binary.

**Expected:** For example, RBAC controls API access while network policy or application auth addresses different paths.

## Boundary and troubleshooting review

A read-only filesystem is not a ban on all writes when writable volumes exist. Nonroot is not an authorization policy for another namespace. RBAC does not govern every packet sent by a workload. A container shares a node kernel and is not automatically a separate virtual machine.

State which control rejects which behavior and what remains untested. If a negative source is refused locally, do not claim that a kernel-level action was attempted or blocked at runtime. The evidence level is part of the security explanation.
