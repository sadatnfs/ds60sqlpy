# docker-011: explanatory solutions

Compare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.

## Mechanism review

Compose describes a related set of services, networks and volumes in one application model. A service describes how to create containers with a common role. A project groups their owned resources so commands can target the application rather than every container on the engine.

The YAML model is declarative input, but running Compose is still an operation against a particular engine. Two copies of the same file can create different projects. Conversely, reusing the same project name can act on existing resources from an earlier invocation. Explicit project identity makes a teaching lab safer and its cleanup understandable.

A service name is also a useful DNS name on its Compose network. The default network enables peers to find each other without fixed IPs. Named volumes remain separate storage resources. An application can therefore be recreated while preserving its data, provided the same intended volume remains mounted.

Use `docker compose -p ds60-docker-study ...` from the copied fixture directory. The explicit `-p` sets the project name consistently for build, up, logs and down. The fixture has `app` and an optional tools-profile `client`; the client uses the same local image but runs a short request command instead of the server.

`config --quiet` validates and renders the model without printing its values or starting services. `up -d --wait` creates or updates services and waits according to readiness behavior. `down` removes the project’s containers and ordinary networks while retaining named volumes unless explicit volume deletion is requested.

## Exercise 1: Identify the project and service names.

The project groups engine resources; the service describes an application role. A container ID is a third identity that can change after recreation.

**Expected:** Project ds60-docker-study and service app.

## Exercise 2: Predict what config --quiet changes.

Static model validation is valuable early evidence, but it cannot prove port availability, image execution, volume permissions or endpoint correctness.

**Expected:** It validates the model without creating runtime resources.

## Exercise 3: Write the project lifecycle command sequence.

Each step adds evidence and has a defined effect. Keeping the project option on every command prevents a directory-name change from accidentally selecting a different project.

**Expected:** Validate, build, up with readiness, inspect, then down.

## Exercise 4: Diagnose an unexpected resource collision.

A reused project name or host port can collide with another copy. Renaming or deleting blindly may affect work you did not create; establish ownership first.

**Expected:** Inspect project identity and existing owned resources before changes.

## Exercise 5: Explain why down preserves user data by default.

Containers and networks are generally disposable application infrastructure. Persistent state deserves a deliberate retention policy, so destruction is not an incidental consequence of stopping a lab.

**Expected:** Named volume removal is a separate explicit operation.

## Exercise 6: Design a two-copy experiment without interference.

Both copies can use the same internal service names because each project has its own network. Host-published ports share a host namespace and must avoid conflicts.

**Expected:** Distinct project names and distinct published host ports.

## Check your transfer

A useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.
