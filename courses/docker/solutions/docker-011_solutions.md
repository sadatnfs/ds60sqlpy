# docker-011: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-011.md).

## Exercise 1: Identify the project and service names.

**Expected answer:** Project ds60-docker-study and service app.

**Why:** The project groups engine resources; the service describes an application role. A container ID is a third identity that can change after recreation.

**Approach:** Read the names from their sources: -p ds60-docker-study sets the project, and the services: key in compose.yaml defines app and client.

**Why this is correct:** The project prefixes resource names such as the network and volume, the service is the role, and each container has its own ID.

**A plausible wrong approach:** Treating the container ID as the stable name fails after recreation, because the ID changes while the project and service stay the same.

**How to verify:** docker compose -p ds60-docker-study ps lists app under the project, and ps -q app shows the current container ID.

## Exercise 2: Predict what config --quiet changes.

**Expected answer:** It validates the model without creating runtime resources.

**Why:** Static model validation is valuable early evidence, but it cannot prove port availability, image execution, volume permissions or endpoint correctness.

**Approach:** Predict the effect from what the command reads: config --quiet parses compose.yaml, applies interpolation and checks the schema.

**Why this is correct:** It exits zero for a valid file and creates nothing, so it is safe to run before any build or start.

**A plausible wrong approach:** Treating a clean config result as proof the stack works fails, because port 18080 may be busy or the volume may reject writes.

**How to verify:** After config --quiet, docker compose -p ds60-docker-study ps -a lists no containers for the project if none existed before.

## Exercise 3: Write the project lifecycle command sequence.

**Expected evidence:** Validate, build, up with readiness, inspect, then down.

**Why:** Each step adds evidence and has a defined effect. Keeping the project option on every command prevents a directory-name change from accidentally selecting a different project.

**Approach:** Order the commands as worked examples 1 and 2 do: config --quiet, build, up -d --wait, ps, then down, each with -p ds60-docker-study.

**Why this is correct:** Each command adds one kind of evidence, from a valid model through a healthy service, and the fixed project flag keeps every command on the same resources.

**A plausible wrong approach:** Omitting -p means Compose derives the project from the directory name, so a renamed copy silently creates a second project.

**How to verify:** Every ps listing during the session shows the same project name, and down reports removing only that project's container and network.

## Exercise 4: Diagnose an unexpected resource collision.

**Expected answer:** Inspect project identity and existing owned resources before changes.

**Why:** A reused project name or host port can collide with another copy. Renaming or deleting blindly may affect work you did not create; establish ownership first.

**Approach:** Before changing anything, list resources by project label and check what already holds host port 18080.

**Why this is correct:** A collision means another stack is using the same project name or port. Only after identifying the owner is it safe to rename or stop.

**A plausible wrong approach:** Running docker rm -f on whatever holds the port may remove another learner's or tool's container that this lesson never created.

**How to verify:** docker ps --filter label=com.docker.compose.project=ds60-docker-study lists only owned containers; anything else on 18080 belongs to someone else.

## Exercise 5: Explain why down preserves user data by default.

**Expected answer:** Named volume removal is a separate explicit operation.

**Why:** Containers and networks are generally disposable application infrastructure. Persistent state deserves a deliberate retention policy, so destruction is not an incidental consequence of stopping a lab.

**Approach:** Compare what down removes by default (containers and the project network) with what it removes only when asked (volumes, with -v).

**Why this is correct:** The study-data volume holds counter.json, which is learner progress. Keeping it by default means routine stops do not erase work.

**A plausible wrong approach:** Adding -v to every down for a tidy machine deletes the counter each time and makes the persistence lessons impossible to observe.

**How to verify:** After down, docker volume ls still lists the project's study-data volume, and the next up returns the previous counter value.

## Exercise 6: Design a two-copy experiment without interference.

**Expected evidence:** Distinct project names and distinct published host ports.

**Why:** Both copies can use the same internal service names because each project has its own network. Host-published ports share a host namespace and must avoid conflicts.

**Approach:** Give each copy its own -p project name and its own host port on the ports line, while leaving service names and container ports unchanged.

**Why this is correct:** Each project gets its own network and volume, so app resolves within each copy. Host ports share one namespace and must differ.

**A plausible wrong approach:** Changing only the project name leaves both copies trying to bind 127.0.0.1:18080, so the second up fails to publish.

**How to verify:** Both projects appear in docker compose ls, and each loopback port returns its own copy's response.

## Check your transfer

Both copies used the same project name, so Compose treated them as one project. The second `up` reconciled the first learner's containers, and both copies shared the same named volume, which is why the counter changed. The second copy needs a distinct project name such as `ds60-docker-study-b` and a distinct loopback port such as 18081, used consistently in every command. After that, `docker compose ls` shows two projects and each label filter finds its own volume. One volume appearing under both project names would show the rename was incomplete.
