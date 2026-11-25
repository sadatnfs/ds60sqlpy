# docker-039: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-039.md).

## Exercise 1: Distinguish namespace and cgroup.

**Expected answer:** Object visibility versus grouping and resource controls.

**Why:** Both influence container behavior but solve different problems. A memory limit does not define which network interfaces a process can see.

**Approach:** Map each setting to its mechanism: --network none and the PID view come from namespaces; mem_limit and cpus come from cgroups.

**Why this is correct:** Namespaces decide what a process can see; cgroups count and limit what it uses.

**A plausible wrong approach:** Expecting mem_limit 128m to hide host network interfaces mixes a resource control with a visibility control.

**How to verify:** The worked example's output shows a PID and a cgroup path; changing the network flag alters interfaces but not the cgroup.

## Exercise 2: Predict whether the container has its own kernel.

**Expected answer:** Ordinary Linux containers share the engine environment kernel.

**Why:** On a desktop host that kernel may live in a Linux VM. The container boundary still does not create another guest kernel for each app.

**Approach:** Run uname -r inside the container and on the engine host or VM and compare.

**Why this is correct:** Both report the same kernel because containers share it; on a desktop that kernel belongs to the engine's Linux VM.

**A plausible wrong approach:** Believing the fixture has its own kernel leads to wrong guesses about isolation and patching.

**How to verify:** The kernel versions match between container and engine environment.

## Exercise 3: Draw the client-to-process runtime chain.

**Expected answer:** Client, engine, runtime setup, mounts and application process.

**Why:** The chain helps place errors such as daemon connection failure, image unpacking failure and application exceptions at different layers.

**Approach:** Draw client, engine API, image unpack and mounts, the OCI runtime, and finally python server.py.

**Why this is correct:** Each error belongs to one stage: cannot connect is the client to engine, unpack errors are the image, and tracebacks are the app.

**A plausible wrong approach:** Reading every failure as an application bug sends a daemon connection error to code review.

**How to verify:** Classify three sample errors to their stage, and the matching log source confirms each.

## Exercise 4: Diagnose a missing cgroup path from an example.

**Expected answer:** Inspect host and cgroup-version differences without changing kernel settings.

**Why:** Implementation details vary. Preserve the conceptual mechanism and record the observed platform instead of forcing one machine layout.

**Approach:** Check which cgroup version the host uses and how the engine lays it out before matching a path from an example.

**Why this is correct:** Paths differ between cgroup v1 and v2 and between engines; the mechanism is the same.

**A plausible wrong approach:** Changing kernel boot settings to match the example's layout alters the host for a cosmetic difference.

**How to verify:** Record the observed path and cgroup version; the limit still appears in the container's cgroup files.

## Exercise 5: Explain OCI interoperability limits.

**Expected answer:** A shared specification does not guarantee every platform or feature is identical.

**Why:** Image architecture, runtime capabilities and host configuration still matter. Test the actual supported engine path.

**Approach:** Separate what OCI standardizes, image and runtime formats, from what it leaves to each platform: architectures, features and host setup.

**Why this is correct:** An OCI image for linux/amd64 still needs a compatible host, and a runtime may not support every option.

**A plausible wrong approach:** Promising the fixture runs anywhere OCI is supported skips architecture and feature checks.

**How to verify:** Run acceptance on each claimed engine and platform and record the results.

## Exercise 6: Describe the shared-kernel security implication.

**Expected answer:** Least privilege and patching remain necessary parts of the trust model.

**Why:** Isolation reduces visibility and authority but depends on kernel enforcement. Do not describe a container as a universal hostile-code sandbox.

**Approach:** Note that every container's syscalls reach the same kernel, so a kernel bug can cross the boundary.

**Why this is correct:** That is why the fixture also drops capabilities, runs as 10001 and needs a patched kernel.

**A plausible wrong approach:** Running untrusted code because it is in a container treats namespaces as a full sandbox.

**How to verify:** The trust note lists the fixture's least-privilege settings and kernel patching as required parts.

## Check your transfer

On Linux the kernel release printed inside the container matched the host's, so every container shares that kernel; namespaces only limit what each process can see, and cgroups only meter what it can use. A kernel vulnerability reachable from inside one container can therefore affect the host and its neighbors. Mitigations are a patched kernel, dropped capabilities, the default seccomp profile and no-new-privileges as the fixture uses, or a stronger boundary such as a VM per tenant. A differing release on a Linux host would mean a VM-based runtime.
