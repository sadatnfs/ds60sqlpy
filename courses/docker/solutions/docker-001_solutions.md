# docker-001: explanatory solutions

Compare after your own attempt or an explicit reveal. These explain the supplied teaching fixtures; they are not engine results. The mechanism is explained in `courses/docker/guides/docker-001.md`.

## Exercise 1: Predict what remains after the short process exits.

**Expected answer:** The local image remains; the --rm container is removed.

**Why:** The removal flag applies to the created container, not to every object derived from its image. An image can be reused by another run without retaining that earlier process or writable layer.

## Exercise 2: Draw two containers created from one image.

**Expected answer:** One shared image description, two process groups and two writable layers.

**Why:** Do not draw one process shared between the containers. Sharing read-only image layers saves storage; it does not merge memory, process IDs or mutable application state.

## Exercise 3: Classify source code, image tag, container and volume.

**Expected answer:** Four objects with separate creation and deletion events.

**Why:** Source is build input, a tag names an image, a container is an instance, and a volume is separately managed storage. Naming these objects correctly makes later cleanup commands predictable.

## Exercise 4: Explain why an exited container can still appear in docker ps -a.

**Expected answer:** Stopped state is distinct from object removal.

**Why:** The main process ending changes container state. Unless automatic removal was requested or a later removal occurs, Docker retains its metadata and writable layer so you can inspect the outcome.

## Exercise 5: Compare a Linux container on macOS with a native macOS process.

**Expected answer:** The container calls a Linux kernel in the engine environment.

**Why:** CPU architecture and the kernel environment both matter. A Linux container does not gain macOS application frameworks merely because a macOS browser connects to its published port.

## Exercise 6: Explain what evidence proves a web application is serving.

**Expected answer:** A running process plus a bounded HTTP request and expected response.

**Why:** An image existing proves only packaging. Container state adds process evidence. The request adds the actual application behavior at a particular endpoint, which remains a separate claim.

## Check your transfer

A useful answer names the exact object, the phase when a setting takes effect, the expected normal result and an observation that would disprove it. A production system additionally needs ownership, lifecycle, data recovery and operational review.
