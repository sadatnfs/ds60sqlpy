# k8s-045: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Containers in the same Pod share a network namespace. They can communicate through localhost and share the Pod’s port space. Containers in different Pods normally have different network namespaces and Pod addresses. This makes a Pod a unit of co-location and shared networking rather than merely a label grouping unrelated containers.

Loopback always refers to the caller’s network namespace. A sidecar in the same Pod can reach an application bound to 127.0.0.1:8080. A different Pod cannot reach that listener through the first Pod’s loopback address. To accept traffic on the Pod interface, the application generally listens on an appropriate non-loopback address, often 0.0.0.0 for IPv4.

A sidecar is a supporting container associated with an application Pod. It may proxy traffic, collect logs or perform another bounded role. Co-location introduces shared fate, startup and shutdown ordering, resource competition and port conflicts. A sidecar is not automatically a separate security or availability boundary.

The containerPort field documents a container’s intended port and can supply a name used elsewhere. It does not start a listener. Two containers in one Pod cannot both bind the same address/port combination independently. Their filesystem namespaces can still differ even though networking is shared.

An emptyDir volume is one way to share files within a Pod, but it is not implied by shared networking and does not survive Pod replacement. Keep the network and storage contracts distinct when explaining a sidecar design.

Since Kubernetes 1.33, native sidecar containers are stable. Declare the helper under `initContainers` with `restartPolicy: Always`. The kubelet starts it in init-container order before the application containers and moves on once it has started, or once its startupProbe succeeds when one is defined. It keeps running for the life of the Pod, is restarted if it exits, is stopped only after the application containers during Pod termination, and does not keep a Job's Pod from completing. A helper listed under `containers` has none of these ordering guarantees, which is why older sidecar designs needed startup polling and shutdown workarounds.

## Exercise 1: Predict same-Pod localhost access.

The Pod boundary determines the loopback scope. This is why a proxy sidecar can reach a loopback-only app.

**Expected:** The sidecar shares the app network namespace.

**Solution reasoning**

- **Approach:** Note that containers in one Pod share a single network namespace and therefore one loopback interface.
- **Why it is correct:** The sidecar's request to localhost reaches the app's listener because both run inside the same Pod network namespace.
- **Plausible wrong approach:** Assuming each container has its own loopback would predict the sidecar cannot reach a loopback-only app, which is wrong.
- **How to verify:** The prediction says the sidecar reaches the app over localhost.

## Exercise 2: Predict different-Pod localhost access.

Use the target Pod or Service address for inter-Pod traffic. Copying a same-Pod URL changes its meaning.

**Expected:** The client reaches its own Pod namespace.

**Solution reasoning**

- **Approach:** Note that the client Pod has its own network namespace and therefore its own loopback.
- **Why it is correct:** localhost in the client Pod refers to that Pod, so a request there never leaves it to reach the target.
- **Plausible wrong approach:** Copying a same-Pod localhost URL into another Pod's config changes its meaning silently.
- **How to verify:** The prediction says the client reaches its own Pod, and the fix names the target Pod or Service address.

## Exercise 3: Draw a sidecar and app port allocation.

Specify address and port for every listener so a collision is visible before runtime.

**Expected:** Distinct listeners share one Pod port space.

**Solution reasoning**

- **Approach:** List each container's listener with address and port and check for duplicates in the shared space.
- **Why it is correct:** All containers share one port space, so two listeners must differ in port or bind address.
- **Plausible wrong approach:** Assigning the same port per container because each has its own image ignores the shared namespace.
- **How to verify:** Each listener has a distinct address and port pair.

## Exercise 4: Diagnose two containers binding 0.0.0.0:8080.

The container boundary does not create a second network namespace inside the Pod. Assign distinct listener roles.

**Expected:** They compete for the same socket within one Pod namespace.

**Solution reasoning**

- **Approach:** Identify that both containers try to bind the same socket in one network namespace.
- **Why it is correct:** Only one process can bind 0.0.0.0:8080 there, so the second fails with an address in use error.
- **Plausible wrong approach:** Expecting each container to get its own 8080 assumes a separate network namespace per container.
- **How to verify:** The answer names the shared socket conflict and assigns distinct ports.

## Exercise 5: Explain containerPort versus a real listener.

A correct manifest can still run a program listening on another port. Observe the application rather than inferring from metadata.

**Expected:** One is declared metadata; the other is process behavior.

**Solution reasoning**

- **Approach:** Contrast the containerPort field in the spec with the port the process actually opens.
- **Why it is correct:** containerPort is declarative metadata and does not open or restrict any socket, so the process can listen elsewhere.
- **Plausible wrong approach:** Trusting containerPort to prove the app listens on 8080 skips observing the process.
- **How to verify:** The answer labels one as metadata and the other as observed process behavior.

## Exercise 6: Defend whether a helper belongs in a sidecar or separate Deployment.

Co-location is useful when tight coupling is intended. Independent scaling or failure isolation may favor a separate workload.

**Expected:** Consider shared lifecycle, scaling, networking and failure requirements.

**Solution reasoning**

- **Approach:** Weigh lifecycle, scaling, networking and failure isolation for the helper.
- **Why it is correct:** A sidecar shares the Pod's lifecycle and network, which suits a tightly coupled proxy but prevents scaling it independently.
- **Plausible wrong approach:** Putting every helper in a sidecar to save Services couples their failures and replica counts to the app.
- **How to verify:** The decision cites at least lifecycle, scaling, networking and failure as factors.
