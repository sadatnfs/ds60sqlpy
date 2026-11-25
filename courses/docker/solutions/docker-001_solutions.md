# docker-001: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-001.md).

## Exercise 1: Predict what remains after the short process exits.

**Expected answer:** The local image remains; the --rm container is removed.

**Why:** The removal flag applies to the created container, not to every object derived from its image. An image can be reused by another run without retaining that earlier process or writable layer.

**Approach:** Separate the two objects that the run touched: the image tagged ds60-docker-study:local and the container that the --rm flag created for one python -c call.

**Why this is correct:** The build wrote the image once; the run only borrowed it. When print(2 + 3) returns, the container's only process ends and --rm deletes that container, leaving the tag untouched.

**A plausible wrong approach:** Assuming --rm cleans up everything the run used leads learners to rebuild before every run. The flag never reaches the image store, so the rebuild is wasted work.

**How to verify:** After the run, docker image ls ds60-docker-study still lists the local tag, while docker ps -a --filter ancestor=ds60-docker-study:local returns no rows.

## Exercise 2: Draw two containers created from one image.

**Expected answer:** One shared image description, two process groups and two writable layers.

**Why:** Do not draw one process shared between the containers. Sharing read-only image layers saves storage; it does not merge memory, process IDs or mutable application state.

**Approach:** Draw one box for the image's read-only layers, then two separate boxes on top, each holding its own process tree and its own thin writable layer.

**Why this is correct:** Each docker run creates a new container with a fresh writable layer and a new PID namespace. Only the read-only image layers are referenced by both.

**A plausible wrong approach:** Drawing a single python process with two names suggests that a variable set in one container is visible in the other. Separate namespaces and writable layers make that impossible.

**How to verify:** Start two short runs that each print os.getpid(); both can report PID 1, which is only possible because each container has its own PID namespace.

## Exercise 3: Classify source code, image tag, container and volume.

**Expected answer:** Four objects with separate creation and deletion events.

**Why:** Source is build input, a tag names an image, a container is an instance, and a volume is separately managed storage. Naming these objects correctly makes later cleanup commands predictable.

**Approach:** Write each object with the event that creates it and the command that removes it: edit server.py, docker build, docker run or compose up, and docker volume create.

**Why this is correct:** server.py lives on the host, ds60-docker-study:local is an image reference, each run produces a container, and study-data is a named volume declared in compose.yaml.

**A plausible wrong approach:** Treating the tag as the container leads to docker rm ds60-docker-study:local, which fails because rm expects a container name or ID, not an image reference.

**How to verify:** List each object with its own inventory command: ls for source, docker image ls, docker ps -a and docker volume ls. Each object appears in exactly one listing.

## Exercise 4: Explain why an exited container can still appear in docker ps -a.

**Expected answer:** Stopped state is distinct from object removal.

**Why:** The main process ending changes container state. Unless automatic removal was requested or a later removal occurs, Docker retains its metadata and writable layer so you can inspect the outcome.

**Approach:** Reason from the main process lifecycle: when it ends, the engine records an exit code and keeps the container object unless --rm or docker rm removes it.

**Why this is correct:** docker ps -a shows all containers, including those in the exited state. The stopped record holds the exit code, logs and writable layer for later inspection.

**A plausible wrong approach:** Concluding that the process is still running because the name is listed confuses docker ps -a with docker ps. Only the default listing filters to running containers.

**How to verify:** Run a container without --rm, then compare docker ps and docker ps -a; the STATUS column for the second shows Exited with the recorded code.

## Exercise 5: Compare a Linux container on macOS with a native macOS process.

**Expected answer:** The container calls a Linux kernel in the engine environment.

**Why:** CPU architecture and the kernel environment both matter. A Linux container does not gain macOS application frameworks merely because a macOS browser connects to its published port.

**Approach:** Compare what each program calls underneath: the containerized python binary is a Linux ELF executable that makes Linux system calls inside the engine's virtual machine.

**Why this is correct:** On macOS, Docker Desktop runs a Linux kernel in a lightweight VM. Containers share that kernel, not the macOS one, so macOS APIs are unavailable inside them.

**A plausible wrong approach:** Expecting an image built for linux/arm64 to run any macOS arm64 binary fails, because matching CPU architecture is not enough when the operating system interface differs.

**How to verify:** Run uname -s through docker run against the local image; it reports Linux, while the same command in a macOS terminal reports Darwin.

## Exercise 6: Explain what evidence proves a web application is serving.

**Expected answer:** A running process plus a bounded HTTP request and expected response.

**Why:** An image existing proves only packaging. Container state adds process evidence. The request adds the actual application behavior at a particular endpoint, which remains a separate claim.

**Approach:** Stack three claims in order: the image exists, the container's main process is running, and a request to the published endpoint returns the expected body.

**Why this is correct:** Only the last layer tests behavior. The fixture's GET / should return JSON with the APP_MESSAGE text, which no image or process listing can show.

**A plausible wrong approach:** Treating a running status from docker ps as proof skips the request. A server bound to the wrong interface or crashing per request still shows a running container.

**How to verify:** From the host, send curl --max-time 3 http://127.0.0.1:18080/ and confirm a 200 response whose message field matches the compose environment value.

## Check your transfer

There are two stopped containers, one image and two separate copies of `/tmp/n`, each in its own container's writable layer. The image is unchanged because writes never flow back into it. The removal fails with a conflict that names a container still using the image, because stopped containers keep a reference to the image they were created from. Remove the two containers first, by ID, and the image removal then succeeds. If `docker ps -a --filter ancestor=ds60-docker-study:local` showed only one container, or a fresh container from the image could read `/tmp/n`, this explanation would be wrong.
