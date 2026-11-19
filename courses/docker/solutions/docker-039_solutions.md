# docker-039: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-039.md`.

## Exercise 1: Distinguish namespace and cgroup.

**Expected answer:** Object visibility versus grouping and resource controls.

**Why:** Both influence container behavior but solve different problems. A memory limit does not define which network interfaces a process can see.

## Exercise 2: Predict whether the container has its own kernel.

**Expected answer:** Ordinary Linux containers share the engine environment kernel.

**Why:** On a desktop host that kernel may live in a Linux VM. The container boundary still does not create another guest kernel for each app.

## Exercise 3: Draw the client-to-process runtime chain.

**Expected answer:** Client, engine, runtime setup, mounts and application process.

**Why:** The chain helps place errors such as daemon connection failure, image unpacking failure and application exceptions at different layers.

## Exercise 4: Diagnose a missing cgroup path from an example.

**Expected answer:** Inspect host and cgroup-version differences without changing kernel settings.

**Why:** Implementation details vary. Preserve the conceptual mechanism and record the observed platform instead of forcing one machine layout.

## Exercise 5: Explain OCI interoperability limits.

**Expected answer:** A shared specification does not guarantee every platform or feature is identical.

**Why:** Image architecture, runtime capabilities and host configuration still matter. Test the actual supported engine path.

## Exercise 6: Describe the shared-kernel security implication.

**Expected answer:** Least privilege and patching remain necessary parts of the trust model.

**Why:** Isolation reduces visibility and authority but depends on kernel enforcement. Do not describe a container as a universal hostile-code sandbox.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
