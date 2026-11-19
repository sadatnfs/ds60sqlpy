# docker-024: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-024.md`.

## Exercise 1: Distinguish rootless mode from a non-root app USER.

**Expected answer:** Engine privilege versus process identity inside one container.

**Why:** Both can be useful, but they apply at different layers. An app USER instruction does not change the daemon installation.

## Exercise 2: Predict why low-port or resource behavior may differ.

**Expected answer:** Rootless networking and delegated controls can have limitations.

**Why:** Consult the chosen engine’s supported configuration and test required behavior. Do not assume rootful observations transfer unchanged.

## Exercise 3: Draw the daemon-socket authority path.

**Expected answer:** Socket access can permit host-impacting container requests.

**Why:** The risk comes from what the API can create and mount. A read-only-looking filesystem mount of a socket does not turn the daemon protocol into a read-only API.

## Exercise 4: Diagnose a lesson requiring engine access from the browser.

**Expected answer:** Move it to an explicit host lab with ownership boundaries.

**Why:** The learning objective does not justify exposing the engine to arbitrary lesson code. A host worksheet can teach the operation honestly.

## Exercise 5: Explain user namespace ID mapping.

**Expected answer:** Container numeric IDs map to a separate host range.

**Why:** Ownership must be interpreted through the mapping. Matching a container UID to a host filename owner by name alone is insufficient.

## Exercise 6: State a support claim for a new rootless setup.

**Expected evidence:** Actual app build, network, storage and cleanup observations.

**Why:** Configuration support on paper is weaker than runtime acceptance. Qualify the specific host setup without advertising untested engines or modes.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
