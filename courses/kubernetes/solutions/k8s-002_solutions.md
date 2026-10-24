# k8s-002: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/k8s-002.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

An image is a packaged filesystem/configuration template. A container is an instance created from image content; it normally runs one main application process and can exit or restart. Two container instances can use the same image. A tag is a mutable human-readable reference, while a digest identifies content. The course will preload one exact fixture image and record its digest; reading a tag in YAML is not proof of cached content.

A port is an endpoint number within a network namespace. A container listening on8080 is different from a host forwarding127.0.0.1:8765 to it. Inside another container, 127.0.0.1 refers to that container itself. Inside a Kubernetes namespace, a Service name selects a cluster routing path. Declaring containerPort does not create a listening server or a host port. This lesson traces supplied evidence and performs no engine or network action.

- **image:** the packaged content used to create containers
- **container:** a running or stopped instance, separate from its image
- **digest:** a content identity recorded after actual image preparation
- **port mapping:** an explicit forwarding relation between network endpoints
- **loopback:** an address referring to the current network namespace, not every machine

## Worked example / walkthrough

### Worked example 1: One image, two instances

Restarting or replacing one instance need not rebuild its immutable image content.

```text
image content I1
container C1 from I1: running
container C2 from I1: exited
```

**Expected:** One image identity and two separate instance states.

### Worked example 2: Trace a host-to-container mapping

The mapping is an explicit host arrangement. Writing containerPort8080 into YAML alone does not establish it.

```text
browser -> 127.0.0.1:8765 on host
forwarding rule -> container app:8080
process listens on8080
```

**Expected:** The browser uses8765; the process listens on8080.

## Exercises and explanatory solutions

### Exercise 1: Count images and containers

**Inputs/evidence:** For k8s-002 Exercise 1, C1 and C2 both useI1.

**Expected result/shape:** For k8s-002 Exercise 1, 1 image, 2 containers, independent running/exited states.

**Verify:** For k8s-002 Exercise 1, count image identities and instance identities separately.

Instances can share packaged content without sharing process state. An exited container is not evidence that the image file vanished.

### Exercise 2: Resolve the browser endpoint

**Inputs/evidence:** For k8s-002 Exercise 2, host 127.0.0.1:8765 forwards to app:8080.

**Expected result/shape:** For k8s-002 Exercise 2, the host browser connects to127.0.0.1:8765.

**Verify:** For k8s-002 Exercise 2, trace both sides without changing the application listening port.

The forwarding rule translates the destination. Using host8080 is unsupported unless another explicit mapping exists.

### Exercise 3: Separate declaration and listener

**Inputs/evidence:** For k8s-002 Exercise 3, declared8080; process not running.

**Expected result/shape:** For k8s-002 Exercise 3, no working listener established by the declaration.

**Verify:** For k8s-002 Exercise 3, name the missing running application evidence.

Metadata documents an intended port for tools/controllers. It does not start a process or make an exited application healthy.

### Exercise 4: Interpret replacement

**Inputs/evidence:** For k8s-002 Exercise 4, oldC1, newC3, contentI1.

**Expected result/shape:** For k8s-002 Exercise 4, container identity changes; image identity staysI1.

**Verify:** For k8s-002 Exercise 4, record both instance IDs and the same digest receipt.

Identity lets a learner distinguish application restart/reconciliation from an image update. A new Pod name alone does not prove new application content.

### Exercise 5: Handle a missing offline image

**Inputs/evidence:** For k8s-002 Exercise 5, fixture tag declared but no matching cached content.

**Expected result/shape:** For k8s-002 Exercise 5, visible image-start failure; no network pull is attempted by this policy.

**Verify:** For k8s-002 Exercise 5, classify missing preload and preserve progress rather than substituting an arbitrary public image.

Offline mode depends on preparation. A correct manifest cannot manufacture missing image bytes, and switching to Always would change the lesson network contract.

### Exercise 6: Transfer the client path

**Inputs/evidence:** For k8s-002 Exercise 6, Service hello on8080; client has its own loopback.

**Expected result/shape:** For k8s-002 Exercise 6, http://hello:8080/version, not host 127.0.0.1:8765.

**Verify:** For k8s-002 Exercise 6, explain both network namespaces and the Service DNS name.

The client must exercise Service routing and the application response. Host port-forwarding can inspect a process but cannot substitute for this in-cluster path.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.
