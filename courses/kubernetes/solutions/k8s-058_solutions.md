# k8s-058: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

NetworkPolicy describes allowed network relationships for selected Pods. It requires a network implementation that enforces the API. Creating the object on a cluster without enforcement does not prove isolation. The policy is primarily about supported network traffic, not HTTP user identity or arbitrary application authorization.

Policies are additive. Once a Pod is isolated for a direction, the union of applicable allow rules determines permitted traffic for that direction. There is no general ordered deny rule that overrides a later allow in the ordinary API. A policy can select all Pods in one namespace with an empty podSelector, while namespace scope remains important.

Selector composition is subtle. A single peer containing both namespaceSelector and podSelector requires both conditions. Separate peers represent alternatives. Confusing these forms can allow far more callers than intended. This lesson makes that Boolean logic explicit with a small synthetic matrix.

A policy’s podSelector selects the destination Pods for ingress rules. Each from item describes an allowed source. Ports constrain the destination transport port. Namespace labels are selected on Namespace objects, not copied from Pod labels by assumption.

For a connection between two Pods, the source Pod’s egress policy and the destination Pod’s ingress policy must both permit it when those directions are isolated. A direction with no applicable isolation does not restrict that connection through NetworkPolicy. Reply traffic belonging to a permitted connection is implicitly allowed; that does not authorize an unrelated new reverse-direction connection.

The fixture provides an allow-client policy as a manual-only example. It does not claim that the ordinary local kind network enforces NetworkPolicy. The offline checker validates selector logic and fields; a live test requires both an allowed and a denied owned client under a known enforcing implementation.

## Exercise 1: Predict the AND selector result for a wrong namespace.

Both predicates in one peer must hold. This is a precise Boolean boundary, not a formatting detail.

**Expected:** It does not match even if the Pod role is tester.

**Solution reasoning**

- **Approach:** Evaluate the namespaceSelector and podSelector in one peer entry as both required.
- **Why it is correct:** Two selectors in the same from item are combined with AND, so a Pod in the wrong namespace fails even with role tester.
- **Plausible wrong approach:** Reading them as OR would admit any tester Pod from any namespace.
- **How to verify:** The prediction says the caller does not match.

## Exercise 2: Compare separate peers with a combined peer.

Review the indentation and list structure carefully. YAML shape changes the access relationship.

**Expected:** Separate entries create alternatives; combined selectors narrow one peer.

**Solution reasoning**

- **Approach:** Compare two list items in from with one item holding both selectors.
- **Why it is correct:** Separate items are alternatives combined with OR, while one item with both selectors narrows to callers matching both.
- **Plausible wrong approach:** A single dash in the YAML decides the meaning, so misplacing it silently widens or narrows access.
- **How to verify:** The answer says separate entries create alternatives and combined selectors narrow one peer.

## Exercise 3: Build an allowed/denied flow matrix.

A matrix exposes gaps before live testing. Include at least one near-miss case for each selector.

**Expected:** Caller namespace, Pod labels, target port and expected result are explicit.

**Solution reasoning**

- **Approach:** Write rows of caller namespace, Pod labels, target port and expected allow or deny result.
- **Why it is correct:** Policy decisions depend on all three inputs, so a matrix shows every case the rules must handle.
- **Plausible wrong approach:** Listing only allowed callers leaves the denied cases untested.
- **How to verify:** Each row names namespace, labels, port and result.

## Exercise 4: Diagnose a policy object with unrestricted actual traffic.

API acceptance is weaker than isolation evidence. Inspect the complete applicable policy set and the CNI capability.

**Expected:** The implementation may not enforce policy or another allow rule may apply.

**Solution reasoning**

- **Approach:** Check whether the CNI enforces NetworkPolicy, then look for another policy allowing the flow.
- **Why it is correct:** The API accepts policy objects even when nothing enforces them, and allow rules from several policies add together.
- **Plausible wrong approach:** Editing the policy repeatedly when no enforcer exists will never change traffic.
- **How to verify:** The diagnosis names the enforcing implementation and other allow rules.

## Exercise 5: Explain additive allow semantics.

Do not assume a default-deny policy overrides a separate broad allow. Evaluate the combined result.

**Expected:** Multiple policies can broaden the union of permitted flows.

**Solution reasoning**

- **Approach:** Explain that a Pod's allowed traffic is the union of all policies selecting it.
- **Why it is correct:** Policies only add allows, and none can deny what another one permits.
- **Plausible wrong approach:** Adding a narrower policy to restrict a broad one has no effect.
- **How to verify:** The answer says multiple policies can broaden the permitted set.

## Exercise 6: Design real isolation acceptance.

The denied case is essential. A successful allowed request alone cannot prove that isolation exists.

**Expected:** One allowed and one denied owned flow under a named enforcing CNI.

**Solution reasoning**

- **Approach:** Run one owned flow that should pass and one that should fail, naming the enforcing CNI.
- **Why it is correct:** An allowed flow alone cannot show isolation, because everything passes without enforcement.
- **Plausible wrong approach:** Testing only the allowed flow passes on a cluster with no enforcement at all.
- **How to verify:** Both outcomes are observed under a named CNI.
