# k8s-039: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A namespace organizes namespaced API resources and supports scoped policy decisions. It is not a virtual machine, a separate kernel or a complete boundary against arbitrary hostile code. Multitenancy design starts by naming the actors and threats: accidental edits, credential misuse, resource exhaustion, network access, filesystem access and runtime escape have different controls.

The course combines a fixed source schema, an exact owned lease, namespace-scoped credentials, restricted container settings, allowed images and bounded cleanup. These controls reduce the permitted operation surface. The normal worker has no engine socket, no ambient cluster selection, no Secret access or arbitrary exec. Advanced host capabilities are separate precisely because they can cross the ordinary namespace boundary.

A threat review should map each behavior to a control and a negative test. Saying secure because namespaces are different is too vague. Conversely, a local parser rejection does not establish that RBAC, admission or network enforcement would independently deny the same request. Preserve the evidence layer for each result.

## Exercise 1: Write a threat model

The host operator has powers the learner deliberately lacks. Distinguishing those actors prevents a namespace boundary from being misrepresented as protection against the administrator who controls the host or credentials.

**Expected:** Actors and assets are explicit rather than a blanket secure claim.

**Solution reasoning**

- **Approach:** Name learner, host operator and unrelated tenant, their capabilities and each asset's owner.
- **Why it is correct:** Threats come from what each actor can do, so explicit capabilities show which paths need controls.
- **Plausible wrong approach:** Writing that the cluster is secure names no actor and gives nothing to test.
- **How to verify:** Each actor lists capabilities, and each asset has an owner.

## Exercise 2: Classify six adversarial fields

The rejected shapes are concrete and reviewable. A successful local negative test shows the broker source boundary, while independent API and runtime controls require their own evidence and should not be inferred automatically.

**Expected:** Every field has a named closed-schema or ownership rule.

**Solution reasoning**

- **Approach:** Map each of the six fields to the closed schema or ownership rule that rejects it.
- **Why it is correct:** The parser accepts only known fields and owned values, so each adversarial field fails a specific rule.
- **Plausible wrong approach:** Relying on Pod Security alone misses the foreign namespace and foreign ServiceAccount, which it does not check.
- **How to verify:** Every field cites one rejecting rule.

## Exercise 3: Review credential exposure

The effective boundary includes the process environment and mounts, not just the manifest form. A learner-facing API that rejects unsafe YAML is insufficient if the same process can directly reach an unrestricted engine socket.

**Expected:** No alternate path around the bounded operation API.

**Solution reasoning**

- **Approach:** Check learner-visible files for tokens, container engine sockets and kubeconfig paths.
- **Why it is correct:** Any of these would let a learner call the API or the engine directly and bypass the bounded operation API.
- **Plausible wrong approach:** Hiding the kubeconfig with file permissions while leaving its path in an artifact still points to it.
- **How to verify:** No credential, socket or kubeconfig path appears.

## Exercise 4: Separate resource and network controls

CPU limits constrain execution consumption, quotas constrain admitted object/resource totals, deadlines bound operations, and network policy governs supported traffic paths. Their effectiveness and failure modes must be tested separately.

**Expected:** Each constrains a different resource or traffic dimension.

**Solution reasoning**

- **Approach:** Name the dimension each control limits.
- **Why it is correct:** CPU limits cap compute per container, quota caps object counts and requests per namespace, deadlines cap time and NetworkPolicy caps traffic.
- **Plausible wrong approach:** Expecting quota to stop network scanning gives it a traffic role it does not have.
- **How to verify:** Four controls map to compute, object count, time and traffic.

## Exercise 5: Inspect cleanup identity defenses

Cleanup is itself a security-sensitive action. Ownership labels, nonce and UID preconditions prevent a stale operation from deleting a replacement or unrelated object after a race or partial failure.

**Expected:** Foreign object preserved and cleanup reports the mismatch.

**Solution reasoning**

- **Approach:** Compare the found object's UID and nonce with the receipt before deleting.
- **Why it is correct:** A same-name object with a different UID was created by someone else, so deleting it would harm another tenant.
- **Plausible wrong approach:** Deleting by name because it matches the expected name removes the foreign object.
- **How to verify:** The foreign object is kept, and cleanup reports the mismatch.

## Exercise 6: State residual assumptions

The conclusion should tell an instructor what was actually established and what would need a different design. It preserves useful assurance while avoiding an unsupported promise about hostile tenants or kernel vulnerabilities.

**Expected:** No arbitrary-code or VM-equivalent isolation claim; host trust and qualified controls are named.

**Solution reasoning**

- **Approach:** Write the isolation statement with trusted host assumptions, qualified controls and untested threats.
- **Why it is correct:** Containers share a kernel, so namespace controls do not equal virtual machine separation.
- **Plausible wrong approach:** Claiming tenants are fully isolated implies protection from kernel exploits nobody tested.
- **How to verify:** Untested threats are listed, and no VM-equivalent claim is made.

## Boundary and troubleshooting review

Report the allowed operations, forbidden surfaces, observed negative cases and remaining assumptions. A clear boundary statement can support safe classroom use without claiming general hostile multitenant hosting.

Do not widen permissions to demonstrate a forbidden action live. Do not collect another lease's tokens as evidence. An authorization denial can be observed using the scoped test identity and a known synthetic target without exposing credentials or unrelated data.
