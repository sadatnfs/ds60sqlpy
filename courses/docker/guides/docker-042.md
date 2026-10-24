# docker-042: Advanced capstone: a release, recovery and teaching handoff

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-041`

## Learning objectives

Assemble a source-bound release packet. Teach the full system and defend its limits. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

The final project is a compact release system rather than a larger application. Starting from the maintained fixture, produce a source-controlled build, an identified image, runtime acceptance, persistence and restore evidence, and a readable operator handoff. The aim is independent reasoning across the complete lifecycle.

An expert explanation separates facts from assumptions. It names the tested engine and platform, the image identity, the source inputs and the behavior actually observed. It can explain why a failure occurs at one layer and which next observation would disprove that explanation. It also knows when a simple local project does not meet public-service or multi-host requirements.

No capstone can certify expertise by itself. Use it to identify gaps: if you cannot explain a mount, signal, cache, network hop or recovery boundary, return to the relevant chapter. Repetition with a changed input is more valuable than copying a completed recipe.

## Anatomy and a trace you can follow

Create a fresh learner copy, keep public synthetic configuration, build visibly, qualify host and peer requests, test one controlled failure, recreate the app, export and independently restore data, and stop owned resources. Preserve an optional image archive for offline transfer without pushing it anywhere.

Your handoff should contain a diagram, command sequence, expected outputs, failure decision tree and explicit retention policy. Include a coverage table with source checks, image build, actual runtime, browser observation, persistence and restore as separate rows. Mark untested engines or architectures honestly.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Organize the release evidence

This is a checklist of independent observations.

```text
source and context reviewed
image identity and platform recorded
health + host request + peer request observed
controlled failure diagnosed
container replacement preserved data
independent restore accepted
owned cleanup verified
```

**Expected observation:** Every row has actual evidence or an explicit not-run statement.

### Worked example 2: Explain one complete request

Use values from your owned run.

```text
browser -> host loopback:18080 -> published mapping -> app:8080
-> handler -> volume-backed counter -> JSON response
peer client -> service DNS app -> app:8080
```

**Expected observation:** The diagram distinguishes network scope, process behavior and durable state.

## Six progressive exercises

### Exercise 1: Predict all outcomes before running the final project.

**Expected evidence:** A written normal, failure, replacement and recovery expectation.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Change one noncritical configuration and rebuild or recreate appropriately.

**Expected evidence:** The chosen lifecycle action matches the kind of change.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Assemble a source-bound release packet.

**Expected evidence:** Exact source, image, platform, commands and observations.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a deliberate single-layer failure.

**Expected evidence:** Minimal evidence locates the fault and a targeted repair restores the invariant.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Prove independent data recovery.

**Expected evidence:** A new owned target serves the preserved expected state.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Teach the full system and defend its limits.

**Expected evidence:** A beginner can follow the handoff and identify what it does not guarantee.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a deliberate single-layer failure. Use its expected observation, Minimal evidence locates the fault and a targeted repair restores the invariant., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/building/best-practices/)
- [Official reference 2](https://docs.docker.com/compose/production/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-042: Advanced capstone: a release, recovery and teaching handoff.
Read courses/docker/guides/docker-042.md and courses/docker/lessons/docker-042.md. Direct prerequisites: `docker-041`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
