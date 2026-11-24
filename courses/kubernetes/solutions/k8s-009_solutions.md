# k8s-009: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A ConfigMap stores nonsecret configuration as named key-value data. It separates configuration from an image, but it does not define how a running process notices a change. An environment variable is captured when the container process starts. A projected ConfigMap file can be refreshed by the kubelet, while the application still needs to reread or reload that file.

The contract-2 fixture consumes one synthetic message through both routes. DS60_MESSAGE references hello-config/message, and a read-only volume projects the same key to /config/message. The server reads its environment for /message and reads the file on each /file-message request. Values are restricted to hello or reviewer, so this lesson handles no credentials or arbitrary environment variables.

The browser can verify both values in a fresh one-shot Run. It cannot patch a live ConfigMap and preserve the existing Pod across Runs. The update comparison is therefore an explicit stateful host experiment or a synthetic trace, not an inference from two separately created browser workloads.

## Exercise 1: Map names and keys

These names play different roles. The volume link connects a Pod declaration to a container mount, while the key selects data from the ConfigMap. A wrong key can break configuration even if the object name exists.

**Expected:** Both consumers reference the same namespaced key; mount path is read-only /config/message.

**Solution reasoning**

- **Approach:** Trace hello-config and key message into both consumers: the configMapKeyRef env entry and the lesson-config volume mounted at /config.
- **Why it is correct:** The env entry and the volume both name the same ConfigMap and key, while the volume name links the Pod volume to a read-only container mount.
- **Plausible wrong approach:** Matching only the ConfigMap name would miss a wrong key, which leaves the env var unresolved and blocks container start even though the object exists.
- **How to verify:** Every reference resolves inside the manifest and the projected file path is /config/message with readOnly true.

## Exercise 2: Run the initial value contract

The fixed client independently checks the data visible through both application routes. A Ready Pod alone would not prove that either configuration path was consumed. The result remains a fresh one-shot observation.

**Expected:** Fresh client verifies /version plus /message=reviewer and /file-message=reviewer, then owned cleanup.

**Solution reasoning**

- **Approach:** Add the ConfigMap, the DS60_MESSAGE reference and the read-only volume, then Run under a fresh contract-2 lease.
- **Why it is correct:** The fixed client calls `/message` for the environment path and `/file-message` for the mounted path, so both consumers must return reviewer.
- **Plausible wrong approach:** Treating a Ready Pod as success ignores that readiness only checks `/ready` and says nothing about which configuration either path loaded.
- **How to verify:** The result shows three passing checks for `/version`, `/message` and `/file-message` plus cleanup of the ConfigMap, Deployment and Service.

## Exercise 3: Predict an environment update

Kubernetes does not rewrite an existing process environment when its source ConfigMap changes. Restarting or rolling out a new Pod can consume the new value, but that is a distinct state transition with new process evidence.

**Expected:** Existing environment remains hello until a new process starts.

**Solution reasoning**

- **Approach:** Hold the process fixed and ask what reads the environment and when.
- **Why it is correct:** The kubelet resolves configMapKeyRef once when the container starts, so the running process keeps hello after the ConfigMap changes.
- **Plausible wrong approach:** Expecting `/message` to switch to reviewer after an edit assumes live environment updates, which Kubernetes never performs for a running process.
- **How to verify:** Pod UID and restartCount are unchanged, and the environment value stays hello until a new process starts.

## Exercise 4: Observe file and reload stages

The fixture rereads per request, but other applications may cache. A bounded observation records actual propagation instead of assuming an exact refresh delay. If the capability is absent, retain the synthetic reasoning rather than inventing a live transcript.

**Expected:** After observed projection, the file may be reviewer; application changes only if it rereads/reloads as designed.

**Solution reasoning**

- **Approach:** Record three observations with timestamps: the ConfigMap value from the API, the bytes in /config/message and the application's HTTP answer.
- **Why it is correct:** Volume projections are refreshed by the kubelet on its own sync cycle, and the fixture rereads the file per request, so each stage can lag the previous one.
- **Plausible wrong approach:** Assuming the file updates immediately or on a fixed delay would turn a guess into a transcript; any timing claim must come from an owned observation.
- **How to verify:** Each record cites its source and time, and absent the host capability the record stays labeled synthetic.

## Exercise 5: Reject unsupported injection

The lesson does not broaden the worker into an arbitrary Pod executor. A source refusal establishes the boundary before workload creation, and should not be mislabeled as a cluster configuration error.

**Expected:** Broker rejection before API mutation; the approved fixed reference still parses.

**Solution reasoning**

- **Approach:** Add one unsupported field at a time in a scratch copy and Run each, then restore the approved source.
- **Why it is correct:** The broker allowlist refuses secretKeyRef, hostPath, subPath and arbitrary env before any API request, so no object is created.
- **Plausible wrong approach:** Describing a refusal as a ConfigMap error blames the cluster for a rejection the course adapter produced before submission.
- **How to verify:** Each refusal message is recorded with no create receipt, and the restored source still passes the parse step.

## Exercise 6: Explain a safe configuration release

A reproducible configuration change needs the desired file plus observed application behavior. A rollback should restore the intended configuration and verify it, not merely delete objects by name or assume the old process still exists.

**Expected:** Record includes ConfigMap version/UID, Pod generation/UID, observed routes and restored source if rollback is needed.

**Solution reasoning**

- **Approach:** Write before and after rows with ConfigMap UID and resourceVersion, Pod UIDs and the routes observed, plus the source to restore.
- **Why it is correct:** Because env values bind at start, a release needs new Pods, and rollback needs the exact prior ConfigMap content and fresh Pods consuming it.
- **Plausible wrong approach:** Deleting objects by name to roll back cannot tell an old Pod from a replacement and leaves no evidence that the old message is served again.
- **How to verify:** A reviewer can roll back using only the recorded UIDs, resourceVersion and restored source, then confirm `/message` returns the old value.

## Boundary and troubleshooting review

If the API shows reviewer but the mounted file still says hello, investigate projection timing and mount details. If the file says reviewer but the application returns hello, investigate application caching/reload. If an environment variable remains hello in the same process, that is expected snapshot behavior rather than a broken ConfigMap.

The synthetic values and fixed endpoints are intentionally narrow. ConfigMaps are not secret storage, and base64 or a read-only mount would not make sensitive data confidential. The app's fresh-run checks prove the initial values it observed, not every future update or reload behavior.
