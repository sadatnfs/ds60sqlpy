# docker-024: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Rootless mode runs the engine and containers without a root daemon under the user’s identity. User namespaces map container user IDs to different host IDs. These mechanisms can reduce host privilege exposure, but they alter networking, storage and resource-control details that must be qualified on the chosen host.

Root inside a container is not automatically identical to host root under every configuration. It is also not automatically harmless. Capabilities, namespace mappings, mounts and daemon access determine what the process can do. The engine socket is especially important because an authorized client can ask the daemon to create containers with powerful host access.

The teaching application should not receive that socket. Docker lessons run as explicit host commands in a learner-owned project. Ordinary browser execution cannot install an engine, create sibling containers or inspect unrelated workloads. This separation is part of the product design.

Rootless mode is an engine installation choice, not a Compose flag that magically converts an already running rootful daemon. Inspect the engine’s documented mode and test the app’s required capabilities. Do not require a learner to reconfigure their working engine for this chapter.

Compare the trust paths: browser code talks to a limited classroom endpoint; host Docker client talks to the daemon; daemon creates processes and mounts. Mounting the daemon socket into the classroom would connect those paths and expand browser code’s authority far beyond a lesson pad.

## Exercise 1: Distinguish rootless mode from a non-root app USER.

Both can be useful, but they apply at different layers. An app USER instruction does not change the daemon installation.

**Expected:** Engine privilege versus process identity inside one container.

## Exercise 2: Predict why low-port or resource behavior may differ.

Consult the chosen engine’s supported configuration and test required behavior. Do not assume rootful observations transfer unchanged.

**Expected:** Rootless networking and delegated controls can have limitations.

## Exercise 3: Draw the daemon-socket authority path.

The risk comes from what the API can create and mount. A read-only-looking filesystem mount of a socket does not turn the daemon protocol into a read-only API.

**Expected:** Socket access can permit host-impacting container requests.

## Exercise 4: Diagnose a lesson requiring engine access from the browser.

The learning objective does not justify exposing the engine to arbitrary lesson code. A host worksheet can teach the operation honestly.

**Expected:** Move it to an explicit host lab with ownership boundaries.

## Exercise 5: Explain user namespace ID mapping.

Ownership must be interpreted through the mapping. Matching a container UID to a host filename owner by name alone is insufficient.

**Expected:** Container numeric IDs map to a separate host range.

## Exercise 6: State a support claim for a new rootless setup.

Configuration support on paper is weaker than runtime acceptance. Qualify the specific host setup without advertising untested engines or modes.

**Expected:** Actual app build, network, storage and cleanup observations.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
