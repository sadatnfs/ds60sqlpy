# k8s-005: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A Pod is Kubernetes's scheduling and lifecycle unit for one or more containers that share certain resources. A container is a running process environment created from an image. An image is packaged filesystem/configuration content, while a tag is a name that can move unless its identity is pinned or independently recorded. The course preloads a reviewed local image and uses imagePullPolicy Never so Run does not fetch an arbitrary replacement.

Pod phase is a broad lifecycle summary. Running does not mean every container is ready to serve the application, and a container can restart while the Pod keeps the same UID. Readiness is a separate condition used by Service routing. Logs describe process output, while API status and ownership describe which process/object you are inspecting.

The browser source creates the fixed hello Deployment so the controller produces the Pod. It does not accept arbitrary Pod names or missing-image tags. A host-provided missing-image negative case belongs to a separate owned observation, and a broker rejection before create must not be mislabeled as a kubelet image failure.

## Exercise 1: Identify image and process contract

The source describes the requested image and process. Actual preload and runtime behavior require a host/image receipt and observed Pod. The port declaration alone does not create routing or host exposure.

**Expected:** Image0.2.0, Never, fixed fixture server, port8080 named http.

## Exercise 2: Trace broad and precise state

Pod phase is intentionally broad. Readiness controls whether the application is considered eligible for normal Service traffic, while process liveness and client correctness are separate questions.

**Expected:** Process running, readiness unproved, no ready-routing claim.

## Exercise 3: Diagnose the image boundary

The broker may reject source before the cluster sees it. A kubelet image-absence reason implies an accepted Pod reached node image handling. Preserving the phase prevents ineffective repairs such as changing application code for an image that never started.

**Expected:** Two different failure phases are named; neither is described as an application crash.

## Exercise 4: Read logs with identity

A reused name or previous container log can mislead diagnosis. UID and restart context explain which execution produced the line. No real secret or unrelated workload output belongs in the learner evidence packet.

**Expected:** An evidence record ties the line to the exact observed process instance.

## Exercise 5: Distinguish restart from replacement

A Deployment can replace a Pod, while the kubelet can restart a container inside an existing Pod. These events have different lifetime implications for ephemeral storage and owner relationships, developed in later chapters.

**Expected:** First is a container restart; second is a different Pod instance.

## Exercise 6: Prove the bounded baseline

The evidence should match the operation that ran. Do not copy a Service success claim from another lesson when this source contains no Service. Keep runtime qualification and the six-task explanation separate from a successful process status.

**Expected:** Controller/Ready Pod identities and owned cleanup are observed; Deployment-only run has no Service-client proof.

## Boundary and troubleshooting review

Do not infer readiness from phase Running, infer a successful image pull from a tag name, or infer current process identity from a reused Pod name. An old saved image0.1 source receives an explicit broker version refusal; that is a source-admission result, not an observed node pull failure.

Use the narrowest discriminating field: Waiting.reason for image availability, container termination state for exit behavior, Ready condition for routing eligibility and a client response for the application. A source review or synthetic trace is labeled as such until an actual owned observation exists.
