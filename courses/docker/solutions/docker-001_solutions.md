# docker-001: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

A process is a running program together with its memory, open files and operating-system identity. An image is a packaged filesystem plus startup configuration. A container is a running or stopped instance created from an image, with its own writable layer and isolation settings. Docker is tooling that asks a container runtime to create and manage those instances. These words name different objects with different lifetimes.

An image is not a miniature running computer. Starting two containers from one image starts two sets of processes. They initially see the same image files but acquire distinct writable changes. Stopping a container stops its processes; it does not erase the image or automatically remove named volumes. Removing an image is not a reliable or appropriate way to remove application data.

Linux containers share the engine’s Linux kernel. On macOS and a Windows WSL 2 setup, the engine lives in a Linux environment managed by the desktop product or distribution. The application therefore follows Linux process and path rules even when your browser is on another operating system. A VM isolates a whole guest kernel; a container primarily isolates processes using the host kernel. Neither word alone tells you the strength of a deployment’s security boundary.

Read `docker run --rm IMAGE COMMAND` from left to right. `run` creates a new container and starts its main process. `--rm` asks Docker to remove that container after it exits. `IMAGE` selects a filesystem and defaults; the remaining arguments replace the default command when the image permits. This is different from `docker start NAME`, which restarts an existing container. A printed line is process output, while the exit status tells you whether that invocation reported success.

Use the maintained fixture image after its explicit build. The examples use `ds60-docker-study:local`, a local tag created by the fixture. They do not require an unknown image to be fetched. An image tag is a convenient name; later chapters explain why it is not an immutable identity.

## Exercise 1: Predict what remains after the short process exits.

The removal flag applies to the created container, not to every object derived from its image. An image can be reused by another run without retaining that earlier process or writable layer.

**Expected:** The local image remains; the --rm container is removed.

## Exercise 2: Draw two containers created from one image.

Do not draw one process shared between the containers. Sharing read-only image layers saves storage; it does not merge memory, process IDs or mutable application state.

**Expected:** One shared image description, two process groups and two writable layers.

## Exercise 3: Classify source code, image tag, container and volume.

Source is build input, a tag names an image, a container is an instance, and a volume is separately managed storage. Naming these objects correctly makes later cleanup commands predictable.

**Expected:** Four objects with separate creation and deletion events.

## Exercise 4: Explain why an exited container can still appear in docker ps -a.

The main process ending changes container state. Unless automatic removal was requested or a later removal occurs, Docker retains its metadata and writable layer so you can inspect the outcome.

**Expected:** Stopped state is distinct from object removal.

## Exercise 5: Compare a Linux container on macOS with a native macOS process.

CPU architecture and the kernel environment both matter. A Linux container does not gain macOS application frameworks merely because a macOS browser connects to its published port.

**Expected:** The container calls a Linux kernel in the engine environment.

## Exercise 6: Explain what evidence proves a web application is serving.

An image existing proves only packaging. Container state adds process evidence. The request adds the actual application behavior at a particular endpoint, which remains a separate claim.

**Expected:** A running process plus a bounded HTTP request and expected response.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
