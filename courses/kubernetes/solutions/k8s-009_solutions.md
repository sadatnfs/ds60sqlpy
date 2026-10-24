# k8s-009: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

A ConfigMap stores nonsecret configuration as named key-value data. It separates configuration from an image, but it does not define how a running process notices a change. An environment variable is captured when the container process starts. A projected ConfigMap file can be refreshed by the kubelet, while the application still needs to reread or reload that file.

The contract-2 fixture consumes one synthetic message through both routes. DS60_MESSAGE references hello-config/message, and a read-only volume projects the same key to /config/message. The server reads its environment for /message and reads the file on each /file-message request. Values are restricted to hello or reviewer, so this lesson handles no credentials or arbitrary environment variables.

The browser can verify both values in a fresh one-shot Run. It cannot patch a live ConfigMap and preserve the existing Pod across Runs. The update comparison is therefore an explicit stateful host experiment or a synthetic trace, not an inference from two separately created browser workloads.

## Exercise 1: Map names and keys

These names play different roles. The volume link connects a Pod declaration to a container mount, while the key selects data from the ConfigMap. A wrong key can break configuration even if the object name exists.

**Expected:** Both consumers reference the same namespaced key; mount path is read-only /config/message.

## Exercise 2: Run the initial value contract

The fixed client independently checks the data visible through both application routes. A Ready Pod alone would not prove that either configuration path was consumed. The result remains a fresh one-shot observation.

**Expected:** Fresh client verifies /version plus /message=reviewer and /file-message=reviewer, then owned cleanup.

## Exercise 3: Predict an environment update

Kubernetes does not rewrite an existing process environment when its source ConfigMap changes. Restarting or rolling out a new Pod can consume the new value, but that is a distinct state transition with new process evidence.

**Expected:** Existing environment remains hello until a new process starts.

## Exercise 4: Observe file and reload stages

The fixture rereads per request, but other applications may cache. A bounded observation records actual propagation instead of assuming an exact refresh delay. If the capability is absent, retain the synthetic reasoning rather than inventing a live transcript.

**Expected:** After observed projection, the file may be reviewer; application changes only if it rereads/reloads as designed.

## Exercise 5: Reject unsupported injection

The lesson does not broaden the worker into an arbitrary Pod executor. A source refusal establishes the boundary before workload creation, and should not be mislabeled as a cluster configuration error.

**Expected:** Broker rejection before API mutation; the approved fixed reference still parses.

## Exercise 6: Explain a safe configuration release

A reproducible configuration change needs the desired file plus observed application behavior. A rollback should restore the intended configuration and verify it, not merely delete objects by name or assume the old process still exists.

**Expected:** Record includes ConfigMap version/UID, Pod generation/UID, observed routes and restored source if rollback is needed.

## Boundary and troubleshooting review

If the API shows reviewer but the mounted file still says hello, investigate projection timing and mount details. If the file says reviewer but the application returns hello, investigate application caching/reload. If an environment variable remains hello in the same process, that is expected snapshot behavior rather than a broken ConfigMap.

The synthetic values and fixed endpoints are intentionally narrow. ConfigMaps are not secret storage, and base64 or a read-only mount would not make sensitive data confidential. The app's fresh-run checks prove the initial values it observed, not every future update or reload behavior.
