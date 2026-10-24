# docker-039: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A namespace changes which operating-system objects a process can see. Linux provides namespaces for areas including processes, mounts, networking and users. A cgroup groups processes for accounting and resource controls. Visibility isolation and resource limits are different mechanisms, even though both contribute to a container environment.

The Open Container Initiative, or OCI, defines specifications for image and runtime interoperability. Docker tooling can use components such as containerd and an OCI runtime to manage execution. These layers explain why an image format, an engine API and a running process are related but not identical products.

The shared Linux kernel remains an important trust boundary. A container is not a separate guest kernel by default. Kernel vulnerabilities, privileged configuration and host mounts can affect isolation. Rootless mode and least privilege reduce specific risks but do not turn every process into a harmless mathematical function.

Trace a launch as client request, engine configuration, runtime setup of namespaces and cgroups, filesystem mounts, then the application process. A process still makes ordinary system calls. Its view and allowed operations depend on the setup around it.

Use read-only observations in the fixture. `/proc/self/status` can show process information, while cgroup details vary by host and cgroup version. Do not modify kernel settings or mount host control filesystems to make the lesson output match a screenshot.

## Exercise 1: Distinguish namespace and cgroup.

Both influence container behavior but solve different problems. A memory limit does not define which network interfaces a process can see.

**Expected:** Object visibility versus grouping and resource controls.

## Exercise 2: Predict whether the container has its own kernel.

On a desktop host that kernel may live in a Linux VM. The container boundary still does not create another guest kernel for each app.

**Expected:** Ordinary Linux containers share the engine environment kernel.

## Exercise 3: Draw the client-to-process runtime chain.

The chain helps place errors such as daemon connection failure, image unpacking failure and application exceptions at different layers.

**Expected:** Client, engine, runtime setup, mounts and application process.

## Exercise 4: Diagnose a missing cgroup path from an example.

Implementation details vary. Preserve the conceptual mechanism and record the observed platform instead of forcing one machine layout.

**Expected:** Inspect host and cgroup-version differences without changing kernel settings.

## Exercise 5: Explain OCI interoperability limits.

Image architecture, runtime capabilities and host configuration still matter. Test the actual supported engine path.

**Expected:** A shared specification does not guarantee every platform or feature is identical.

## Exercise 6: Describe the shared-kernel security implication.

Isolation reduces visibility and authority but depends on kernel enforcement. Do not describe a container as a universal hostile-code sandbox.

**Expected:** Least privilege and patching remain necessary parts of the trust model.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
