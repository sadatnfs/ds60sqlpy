# k8s-024: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Kustomize transforms a base set of Kubernetes manifests through explicit overlays. It works with structured YAML rather than a general text-template language. Rendering produces desired objects for review; it does not by itself contact or modify a cluster. Server-side apply is a separate API operation that tracks field ownership among managers.

The vendored fixture contains one Deployment base and dev/test overlays that change only replica count. It uses local relative paths and no remote base. A prepared pinned renderer can produce output offline. The checked-in expected JSON records the intended result, but is not a claim that a renderer was executed on this host.

The browser does not run Kustomize or arbitrary apply commands. A reviewed rendered Deployment can fit the fixed manifest contract, while live field-manager conflict experiments need a stateful host capability with explicit ownership and target identity.

## Exercise 1: Locate the source of intent

The overlay expresses the intended environment difference. Local paths and a small resource set make review tractable and avoid a hidden network dependency.

**Expected:** One local Deployment base plus explicit dev1/test2 overrides.

## Exercise 2: Render with prepared tooling

The checked-in expected output is an independent target, not a fabricated execution transcript. A real render receipt should include tool identity and source hashes, especially when versions can change transformations.

**Expected:** Actual output is compared with expected JSON; missing tool is recorded as unavailable.

## Exercise 3: Compare the full diff

A successful renderer can still produce an unsafe or unintended object. The diff must cover the full output set so an extra resource or changed target is not hidden behind the expected count change.

**Expected:** Exactly one intended field path changes.

## Exercise 4: Interpret field ownership

Authorization can permit a request while field ownership still conflicts. The correct response is to coordinate which actor should manage the field or change the design, not assume force is harmless.

**Expected:** The same field has competing intent; manager identity and current UID/version are recorded.

## Exercise 5: Reject a namespace escape

The target must remain bound to the owned receipt. Neither a valid YAML parser nor a successful Kustomize command grants permission to apply elsewhere.

**Expected:** The output fails the course ownership/allowlist review before apply.

## Exercise 6: Preserve reproducibility

Keeping the transformation inputs and output connected prevents drift between declared and applied intent. Live acceptance remains a separate bounded host operation with UID-aware cleanup.

**Expected:** A reviewer can separate render, admission, reconciliation and application evidence.

## Boundary and troubleshooting review

A rendered file can be valid YAML and still contain an unsupported API, an unapproved image or a namespace escape. A server dry-run can provide admission evidence but is not a completed reconciliation. An apply response is still weaker than application verification.

Do not edit generated output as a hidden second source of truth without recording the change in the overlay. Retain the base/overlay identity, rendered diff and actual runtime receipt when a host apply is performed.
