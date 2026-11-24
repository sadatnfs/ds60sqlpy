# k8s-012: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Troubleshooting starts by separating observations from hypotheses. A condition, event or log can narrow a failure, but no single status word explains every unavailable application. Build a short timeline from source submission through API acceptance, scheduling, container start, readiness and client behavior. Locate the first boundary that has not been established.

This worksheet compares three explicit synthetic cases: missing configuration, an incorrect readiness path and a failed finite Job. It also names which cases the browser can reproduce directly. Wrong readiness and fixed task failure have bounded current operations; the missing-config example is a host/static case because the broker rejects inconsistent ConfigMap references before apply.

The purpose is a disciplined diagnosis and minimal repair, not a collection of broad commands against every namespace. Use only the owned target and preserve relevant object UIDs so a replacement or unrelated workload cannot silently enter the evidence.

## Exercise 1: Order the evidence phases

The sequence prevents searching application logs before a container was configured or treating a Service response as guaranteed by object creation. Real timestamps can overlap across controllers, but the evidence dependencies remain useful.

**Expected:** A trace identifies the first missing or failed boundary for each case.

**Solution reasoning**

- **Approach:** Lay out the five boundaries as a dependency chain and, for each case, stop at the first boundary with no supporting evidence.
- **Why it is correct:** Each stage needs the previous one: a container cannot start before the Pod is scheduled, and a client response needs a Ready endpoint first.
- **Plausible wrong approach:** Opening application logs first for every case fails for case A, where the container was never created and there are no logs to read.
- **How to verify:** Each case has one first failed boundary and every later boundary is marked not reached.

## Exercise 2: Diagnose missing configuration

The general Kubernetes failure occurs during container configuration. The current broker catches some inconsistent references earlier, so a browser refusal must be labeled as a different phase. The host fixture is required to observe the kubelet condition.

**Expected:** Inspect referenced ConfigMap name/key and availability; do not claim the process crashed.

**Solution reasoning**

- **Approach:** Read the configMapKeyRef in the Pod spec and check that the named ConfigMap and key exist in the same namespace.
- **Why it is correct:** A missing ConfigMap or key stops the kubelet at container configuration with CreateContainerConfigError, before any process runs.
- **Plausible wrong approach:** Calling case A a crash and raising restart tolerance changes nothing, because restartCount stays 0 and no process ever exited.
- **How to verify:** The check quotes the ConfigMap name and key exactly as the spec does and needs no application log.

## Exercise 3: Diagnose the probe path

The application can be running while the readiness URL is wrong. Changing unrelated selectors or resource limits does not explain the observed 404. A new bounded run should preserve its own source and identity receipt.

**Expected:** Change /missing to the admitted /ready path; then require new Ready and client evidence.

**Solution reasoning**

- **Approach:** Change only readinessProbe.httpGet.path from /missing to /ready and predict the two confirming observations.
- **Why it is correct:** The fixture serves 200 on /ready and 404 on /missing, so the process runs normally but stays unready until the probe path is fixed.
- **Plausible wrong approach:** Editing the Service selector or resource limits leaves the 404 untouched, so the Pod remains NotReady and the client still gets no endpoint.
- **How to verify:** A new Run shows the Ready condition True and a successful client response, with one field changed.

## Exercise 4: Diagnose finite work

The fixed task can start successfully and still fail its own contract. Increasing an unrelated Deployment count would not repair it. A retry policy also cannot turn a deterministic injected failure into a correct result without changing the intended input.

**Expected:** Task exit 2 and terminal Failed condition identify the injected application outcome.

**Solution reasoning**

- **Approach:** Read the Job's terminal condition together with the task container's terminated exit code.
- **Why it is correct:** Exit code 2 from a started container with condition Failed means the task itself reported failure, not the controller or the image.
- **Plausible wrong approach:** Raising backoffLimit retries the same deterministic input, so every attempt exits 2 and the Job still fails, only later.
- **How to verify:** The record cites Failed and exit 2 together, and shows neither DeadlineExceeded nor an image waiting reason.

## Exercise 5: Write a minimal incident timeline

A reviewable timeline separates what was seen from what was inferred and what was actually changed. It should make a failed hypothesis useful evidence rather than erase it after a later successful attempt.

**Expected:** Each claim cites a bounded field/line and object identity; synthetic facts are labeled.

**Solution reasoning**

- **Approach:** Write four rows for one case: what you observed, what you inferred, the one change you made and the condition that would accept it.
- **Why it is correct:** Separating observation from hypothesis lets a reviewer see which field or log line supported each step and which belief was later disproved.
- **Plausible wrong approach:** Rewriting the timeline after the fix to show only the successful step erases the failed hypothesis that ruled out a cause.
- **How to verify:** Every row cites an object UID and a bounded field or line, and synthetic rows are labeled.

## Exercise 6: Verify recovery and cleanup

Recovery needs evidence at the failed layer plus the intended application result. Cleanup has its own identity and deadline contract, especially after timeout or cancellation. A same-name replacement must remain untouched.

**Expected:** Relevant controller/application checks pass and only recorded owned UIDs are removed.

**Solution reasoning**

- **Approach:** List the check that failed originally plus the end-to-end client result, then the UIDs you created and nothing else.
- **Why it is correct:** Recovery is proven at the layer that broke, and cleanup is safe only against identities you recorded at creation.
- **Plausible wrong approach:** Deleting every object labeled app=hello would remove same-name replacements or another learner's objects the run never created.
- **How to verify:** Post-repair checks pass, and the delete list matches the creation record UID for UID.

## Boundary and troubleshooting review

A large dump of every namespace, log and Secret is not a better diagnosis and exceeds the course scope. Start from the owned source, identity and first discriminating condition. Do not turn a source-admission refusal into a fabricated cluster event or copy synthetic fixture timestamps into a live incident report.

The offline reference classifies supplied facts only. It does not discover a real incident or establish that a proposed repair was applied. Keep predicted outcomes, actual observations and confirmed recovery as separate entries.
