# k8s-045: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Containers in the same Pod share a network namespace. They can communicate through localhost and share the Pod’s port space. Containers in different Pods normally have different network namespaces and Pod addresses. This makes a Pod a unit of co-location and shared networking rather than merely a label grouping unrelated containers.

Loopback always refers to the caller’s network namespace. A sidecar in the same Pod can reach an application bound to 127.0.0.1:8080. A different Pod cannot reach that listener through the first Pod’s loopback address. To accept traffic on the Pod interface, the application generally listens on an appropriate non-loopback address, often 0.0.0.0 for IPv4.

A sidecar is a supporting container associated with an application Pod. It may proxy traffic, collect logs or perform another bounded role. Co-location introduces shared fate, startup and shutdown ordering, resource competition and port conflicts. A sidecar is not automatically a separate security or availability boundary.

The containerPort field documents a container’s intended port and can supply a name used elsewhere. It does not start a listener. Two containers in one Pod cannot both bind the same address/port combination independently. Their filesystem namespaces can still differ even though networking is shared.

An emptyDir volume is one way to share files within a Pod, but it is not implied by shared networking and does not survive Pod replacement. Keep the network and storage contracts distinct when explaining a sidecar design.

## Exercise 1: Predict same-Pod localhost access.

The Pod boundary determines the loopback scope. This is why a proxy sidecar can reach a loopback-only app.

**Expected:** The sidecar shares the app network namespace.

## Exercise 2: Predict different-Pod localhost access.

Use the target Pod or Service address for inter-Pod traffic. Copying a same-Pod URL changes its meaning.

**Expected:** The client reaches its own Pod namespace.

## Exercise 3: Draw a sidecar and app port allocation.

Specify address and port for every listener so a collision is visible before runtime.

**Expected:** Distinct listeners share one Pod port space.

## Exercise 4: Diagnose two containers binding 0.0.0.0:8080.

The container boundary does not create a second network namespace inside the Pod. Assign distinct listener roles.

**Expected:** They compete for the same socket within one Pod namespace.

## Exercise 5: Explain containerPort versus a real listener.

A correct manifest can still run a program listening on another port. Observe the application rather than inferring from metadata.

**Expected:** One is declared metadata; the other is process behavior.

## Exercise 6: Defend whether a helper belongs in a sidecar or separate Deployment.

Co-location is useful when tight coupling is intended. Independent scaling or failure isolation may favor a separate workload.

**Expected:** Consider shared lifecycle, scaling, networking and failure requirements.
