# k8s-005: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Pod is Kubernetes's scheduling and lifecycle unit for one or more containers that share certain resources. A container is a running process environment created from an image. An image is packaged filesystem/configuration content, while a tag is a name that can move unless its identity is pinned or independently recorded. The course preloads a reviewed local image and uses imagePullPolicy Never so Run does not fetch an arbitrary replacement.

Pod phase is a broad lifecycle summary. Running does not mean every container is ready to serve the application, and a container can restart while the Pod keeps the same UID. Readiness is a separate condition used by Service routing. Logs describe process output, while API status and ownership describe which process/object you are inspecting.

The browser source creates the fixed hello Deployment so the controller produces the Pod. It does not accept arbitrary Pod names or missing-image tags. A host-provided missing-image negative case belongs to a separate owned observation, and a broker rejection before create must not be mislabeled as a kubelet image failure.

## Exercise 1: Identify image and process contract

The source describes the requested image and process. Actual preload and runtime behavior require a host/image receipt and observed Pod. The port declaration alone does not create routing or host exposure.

**Expected:** Image 0.2.0, Never, fixed fixture server, port 8080 named http.

**Solution reasoning**

- **Approach:** Read the container block of the starter field by field: image, imagePullPolicy, command and the first ports entry.
- **Why it is correct:** These four fields fully determine which preloaded image tag the kubelet may use, that it must not pull, which fixture process starts and which port name later objects can reference.
- **Plausible wrong approach:** Quoting the lesson title or guessing from the file name skips the YAML, and would miss that `Never` forbids a registry pull rather than merely preferring a cache.
- **How to verify:** Each answer cites an exact path under `spec.template.spec.containers[0]` and reads 0.2.0, Never, the fixed server command and 8080 named http.

## Exercise 2: Trace broad and precise state

Pod phase is intentionally broad. Readiness controls whether the application is considered eligible for normal Service traffic, while process liveness and client correctness are separate questions.

**Expected:** The first Run fails its bounded readiness check without an application crash: the process can be Running while Ready stays False. After /ready is restored, a fresh Run can establish Ready.

**Solution reasoning**

- **Approach:** Classify phase and readiness as separate signals, then change only the readinessProbe path from /missing back to /ready.
- **Why it is correct:** The fixture server keeps running when /missing returns an error, so the phase stays Running while the Ready condition stays False until the probe succeeds.
- **Plausible wrong approach:** Calling the first Run a crash would send you to the command or image, yet restartCount stays unchanged because a readiness failure never restarts the container.
- **How to verify:** The first result names the failed readiness check, and the second Run reports the Ready condition True for a new Pod.

## Exercise 3: Diagnose the image boundary

The broker may reject source before the cluster sees it. A kubelet image-absence reason implies an accepted Pod reached node image handling. Preserving the phase prevents ineffective repairs such as changing application code for an image that never started.

**Expected:** Two different failure phases are named; neither is described as an application crash.

**Solution reasoning**

- **Approach:** Place each failure on the timeline: broker admission before any API object, or kubelet image handling after the Pod is accepted and scheduled.
- **Why it is correct:** An unapproved image is refused by the broker allowlist, while ErrImageNeverPull appears only when an accepted Pod with pull policy Never lands on a node lacking the image.
- **Plausible wrong approach:** Rebuilding application code treats both as runtime crashes, but in neither case did the container process start, so code changes cannot help.
- **How to verify:** State object created no and process started no for the broker case, object created yes and process started no for ErrImageNeverPull.

## Exercise 4: Read logs with identity

A reused name or previous container log can mislead diagnosis. UID and restart context explain which execution produced the line. No real secret or unrelated workload output belongs in the learner evidence packet.

**Expected:** An evidence record ties the line to the exact observed process instance.

**Solution reasoning**

- **Approach:** Attach Pod UID, container name and restartCount to the bounded excerpt before interpreting the line.
- **Why it is correct:** Pod names repeat across replacements and `--previous` can return output from an earlier container instance, so only those three fields pin the line to one process.
- **Plausible wrong approach:** Copying the newest lines by Pod name could mix output from a replaced Pod with the same generated name pattern, or a previous container after a restart.
- **How to verify:** A second reader finds the same UID, container name and restartCount in a readback; the excerpt contains no secrets or unrelated workloads.

## Exercise 5: Distinguish restart from replacement

A Deployment can replace a Pod, while the kubelet can restart a container inside an existing Pod. These events have different lifetime implications for ephemeral storage and owner relationships, developed in later chapters.

**Expected:** First is a container restart; second is a different Pod instance.

**Solution reasoning**

- **Approach:** Compare metadata.uid first and only then interpret restartCount within one Pod.
- **Why it is correct:** restartCount counts kubelet restarts of a container inside one Pod object, while a new UID means a controller created a different Pod with a fresh count of 0.
- **Plausible wrong approach:** Reading the drop from 1 to 0 as a counter reset inside one Pod hides the replacement and the loss of that Pod's emptyDir data.
- **How to verify:** Same UID with count 1 is a container restart; different UID with count 0 is a new Pod instance.

## Exercise 6: Prove the bounded baseline

The evidence should match the operation that ran. Do not copy a Service success claim from another lesson when this source contains no Service. Keep runtime qualification and the six-task explanation separate from a successful process status.

**Expected:** Controller/Ready Pod identities and owned cleanup are observed; Deployment-only run has no Service-client proof.

**Solution reasoning**

- **Approach:** List what this source creates (a Deployment and its Pods only) and map each claim to a named check in the Run result.
- **Why it is correct:** The Deployment-only starter has no Service, so the run can observe controller ownership, Ready Pod identities and cleanup but no Service routing or client response.
- **Plausible wrong approach:** Borrowing a Service success line from k8s-008 would claim traffic evidence for an object that this manifest never creates.
- **How to verify:** Every sentence in your statement points to a check name, and any Service or client claim without one is deleted.

## Boundary and troubleshooting review

Do not infer readiness from phase Running, infer a successful image pull from a tag name, or infer current process identity from a reused Pod name. An old saved image 0.1 source receives an explicit broker version refusal; that is a source-admission result, not an observed node pull failure.

Use the narrowest discriminating field: Waiting.reason for image availability, container termination state for exit behavior, Ready condition for routing eligibility and a client response for the application. A source review or synthetic trace is labeled as such until an actual owned observation exists.
