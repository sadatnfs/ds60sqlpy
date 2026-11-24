# k8s-025: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Helm renders parameterized chart templates and can manage release lifecycle through the Kubernetes API. Rendering a chart locally and installing a release are different operations. An install may create release metadata, execute lifecycle hooks or include cluster-scoped resources, so a successful template command is not permission to run the full lifecycle.

The vendored lesson-hello chart has no remote dependencies, plugins, hooks or CRDs. Its values schema restricts replicas to one or two and the image to the approved fixture 0.2.0. The only template is a fixed Deployment. A prepared pinned Helm binary can render this local input offline; the browser does not execute Helm commands.

The lesson emphasizes reviewing the rendered objects rather than trusting a chart name or a friendly values file. A template can hide resource kinds, annotations and field changes that are not obvious from one setting. The default expected JSON is a declared output target, not a fabricated Helm execution receipt.

## Exercise 1: Inventory the vendored chart

The inventory establishes which inputs the renderer can use. It should reveal hidden resource-producing files before a deployment action is considered.

**Expected:** One local template, no dependencies/plugins/hooks/CRDs.

**Solution reasoning**

- **Approach:** List Chart.yaml, values.yaml, values.schema.json, the single template and the expected output, and compare with a directory listing.
- **Why it is correct:** A chart with no dependencies, hooks or CRDs renders only what its one template declares.
- **Plausible wrong approach:** Inventorying from Chart.yaml alone misses a crds directory or a hook template that could install extra resources.
- **How to verify:** The listing matches: no charts or crds directory and exactly one template.

## Exercise 2: Render the default locally

The expected file is an independent reference. A real render should be observed and versioned rather than inferred from readable template syntax.

**Expected:** One Deployment with replicas 1 and approved image; record actual renderer receipt or unavailable status.

**Solution reasoning**

- **Approach:** Record helm version and diff helm template output against expected-default.json structurally.
- **Why it is correct:** helm template renders locally without contacting a cluster, so the output reflects only chart and default values.
- **Plausible wrong approach:** Using helm install to see the output sends resources to a cluster before review.
- **How to verify:** One Deployment with replicas 1 and the approved image, or the tool marked unavailable.

## Exercise 3: Review an allowed override

The schema limits input values, but the rendered output still needs review because a template could use one value in several fields. The simple fixture makes that relationship explicit.

**Expected:** Only spec.replicas changes.

**Solution reasoning**

- **Approach:** Render with replicas 2 and diff the full object against the default.
- **Why it is correct:** The template only reads replicas from values, so the override should change exactly one path.
- **Plausible wrong approach:** Checking replicas alone would not detect a template that also changes labels with the value.
- **How to verify:** spec.replicas is the only changed path.

## Exercise 4: Reject invalid values

The failure is a rendering/input-contract result, not a Kubernetes scheduling failure. Preserve the diagnostic and restore valid values rather than disabling validation.

**Expected:** Schema/review rejection before any cluster operation.

**Solution reasoning**

- **Approach:** Render each invalid scratch values file and record the schema rule that rejects it.
- **Why it is correct:** Helm validates values against values.schema.json before rendering, so out-of-range, unapproved or unknown values fail locally.
- **Plausible wrong approach:** Removing the schema to make the render succeed disables the check the exercise relies on.
- **How to verify:** Each file fails with a named schema rule, before any cluster operation.

## Exercise 5: Detect lifecycle resources

Hooks, CRDs and release storage change authority and cleanup needs. The lesson keeps them visible rather than relying on a chart's name or suppressing output that would reveal them.

**Expected:** The output is outside the normal worker contract and is not installed.

**Solution reasoning**

- **Approach:** Search the render for helm.sh/hook annotations and any kind other than Deployment.
- **Why it is correct:** Hooks run outside normal install ordering, and cluster-scoped kinds exceed the worker's namespaced permissions.
- **Plausible wrong approach:** Installing and checking afterward lets a hook run before anyone reviewed it.
- **How to verify:** Any hook or extra kind is flagged and the render is not installed.

## Exercise 6: Hand off a reviewed render

The handoff connects inputs to desired objects without pretending rendering grants deployment authority. Any host install requires its own scoped capability and lifecycle/cleanup evidence.

**Expected:** A reviewer can reproduce the local render and identify the exact owned runtime boundary.

**Solution reasoning**

- **Approach:** Record chart hash, values hash, renderer version and full diff, and keep apply evidence separate.
- **Why it is correct:** Hashes and the version pin every input, so a reviewer can reproduce the render offline.
- **Plausible wrong approach:** Recording only the release name ties the review to cluster state rather than reproducible inputs.
- **How to verify:** A reviewer reproduces the render from the hashes and version without a cluster.

## Boundary and troubleshooting review

Pin chart contents, dependency inputs, values, renderer version and rendered output identity. A chart version string alone can be reused or refer to changed bytes. Diff the complete output before applying, including security and namespace fields.

If Helm is unavailable, the live render row remains unavailable while the source/expected-output reasoning can be completed offline. A valid render is not API acceptance, reconciliation or application correctness. Those remain separate owned operations with their own cleanup receipts.
