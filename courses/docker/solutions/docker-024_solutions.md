# docker-024: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-024.md).

## Exercise 1: Distinguish rootless mode from a non-root app USER.

**Expected answer:** Engine privilege versus process identity inside one container.

**Why:** Both can be useful, but they apply at different layers. An app USER instruction does not change the daemon installation.

**Approach:** Place each setting at its layer: rootless mode is how the daemon runs on the host; USER 10001:10001 is who server.py runs as inside one container.

**Why this is correct:** The Dockerfile cannot change how the engine was installed, and a rootless daemon still runs whatever USER the image sets.

**A plausible wrong approach:** Claiming the fixture is rootless because of its USER line confuses the process identity with the engine's privilege.

**How to verify:** docker info lists rootless among its security options only when the daemon runs that way, regardless of image USER.

## Exercise 2: Predict why low-port or resource behavior may differ.

**Expected answer:** Rootless networking and delegated controls can have limitations.

**Why:** Consult the chosen engine’s supported configuration and test required behavior. Do not assume rootful observations transfer unchanged.

**Approach:** Expect differences where rootless engines rely on user-level helpers: binding ports below 1024 and applying cgroup limits like cpus.

**Why this is correct:** Without host root, networking runs through a user-mode helper and cgroup limits depend on delegation set up by the host.

**A plausible wrong approach:** Copying a rootful setup and assuming 127.0.0.1:18080 and mem_limit behave identically skips the check that matters.

**How to verify:** Run the fixture on the rootless engine and confirm the port answers and docker stats reflects the limits.

## Exercise 3: Draw the daemon-socket authority path.

**Expected answer:** Socket access can permit host-impacting container requests.

**Why:** The risk comes from what the API can create and mount. A read-only-looking filesystem mount of a socket does not turn the daemon protocol into a read-only API.

**Approach:** Draw the chain from the mounted socket to the engine API to any new container the API can start, including one mounting the host root.

**Why this is correct:** The socket accepts API calls; a :ro flag on the socket's mount does not limit those calls.

**A plausible wrong approach:** Approving the socket mount because it is marked read-only gives the container control of the engine.

**How to verify:** Confirm compose.yaml has no docker.sock mount; a review search for that path should find nothing.

## Exercise 4: Diagnose a lesson requiring engine access from the browser.

**Expected answer:** Move it to an explicit host lab with ownership boundaries.

**Why:** The learning objective does not justify exposing the engine to arbitrary lesson code. A host worksheet can teach the operation honestly.

**Approach:** Recognize that a browser lesson asking for docker commands would route arbitrary learner code to engine control.

**Why this is correct:** The classroom API runs only declared lesson runtimes; giving lessons the engine would cross that boundary.

**A plausible wrong approach:** Mounting the socket into the lesson runtime to make the exercise work exposes the host to any code a learner types.

**How to verify:** Move the steps to a host worksheet the learner runs themselves; the classroom configuration still has no engine path.

## Exercise 5: Explain user namespace ID mapping.

**Expected answer:** Container numeric IDs map to a separate host range.

**Why:** Ownership must be interpreted through the mapping. Matching a container UID to a host filename owner by name alone is insufficient.

**Approach:** Read the mapping as a shift: container UID 10001 corresponds to a host UID inside a configured subordinate range, not to host UID 10001.

**Why this is correct:** Files the app creates appear on the host under the mapped number, so ownership checks must apply the offset.

**A plausible wrong approach:** Matching a host user named app to the container's app user by name ignores both the name lookup and the range shift.

**How to verify:** Create a file from the container and list it with ls -n on the host; the owner is the mapped number.

## Exercise 6: State a support claim for a new rootless setup.

**Expected evidence:** Actual app build, network, storage and cleanup observations.

**Why:** Configuration support on paper is weaker than runtime acceptance. Qualify the specific host setup without advertising untested engines or modes.

**Approach:** Record what actually ran on the new setup: the build, the healthy app, the peer request, a volume write and scoped cleanup.

**Why this is correct:** Rootless limits show up in practice, so passing runs are what support the setup, not the documentation's feature list.

**A plausible wrong approach:** Announcing rootless support because the engine's docs list it skips the networking and storage checks that may fail.

**How to verify:** Each claim in the support note links to one observed result on that host and engine version.

## Check your transfer

The job gains full control of the host engine, which in practice means root on that host: it can start a privileged container that mounts `/`, read other jobs' containers and volumes, and change images that later deployments use. Alternatives include a rootless BuildKit builder, a remote buildx builder dedicated to CI, or a disposable virtual machine per job. Acceptance should show the job can build and push its image yet cannot list unrelated containers. If the job could not list containers through the socket, the socket would not be the real engine endpoint.
