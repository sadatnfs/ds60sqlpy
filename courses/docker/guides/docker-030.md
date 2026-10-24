# docker-030: Vulnerability findings, patching and dependency updates

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-029`

## Learning objectives

Design a minimal base-image update. Write a patch decision record. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A vulnerability finding connects an affected component version to a published issue under a scanner’s knowledge and matching rules. It is evidence for investigation, not a complete exploitability assessment. False matches, missing packages, runtime exposure and available fixes all influence the response.

Patching an image generally means rebuilding from updated inputs and replacing containers with the new image. Installing packages interactively inside a running container makes an untracked difference that disappears on recreation. The maintained build recipe and lock inputs must describe the repair.

A rebuild can introduce regressions as well as fixes. Use a small update scope, preserve the old immutable artifact, run the relevant tests and verify the actual final image. Do not claim that a passing scan proves absence of all vulnerabilities or that an unfixed low-severity finding is automatically harmless.

## Anatomy and a trace you can follow

Classify findings by component, installed version, fixed version if available, application reachability and required action. Keep the scanner database timestamp and artifact digest. A tag-based report becomes stale when the tag changes.

For this lesson, use a synthetic finding table and prepare an update plan without downloading a scanner or changing the engine. Actual scanning is an optional explicitly prepared tool workflow. The course does not invent a zero-findings badge for an unscanned image.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Read a synthetic finding

The package and versions are illustrative.

```json
{"component":"example-library","installed":"1.0","fixed":"1.1","artifact":"specific image digest","status":"requires review"}
```

**Expected observation:** The record is input to a patch decision, not proof of exploitation or a completed fix.

### Worked example 2: Trace a reproducible patch

This is the required sequence.

```text
update declared input -> build new image -> run tests -> inspect exact digest -> replace owned container -> verify behavior
```

**Expected observation:** An interactive package install inside the old container is not the maintained release artifact.

## Six progressive exercises

### Exercise 1: Separate vulnerability presence and exploitability.

**Expected evidence:** A matched affected component versus a demonstrated reachable exploit condition.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict why an interactive patch disappears.

**Expected evidence:** Container recreation returns to the packaged image inputs.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a minimal base-image update.

**Expected evidence:** Change the resolved base deliberately and rerun relevant acceptance.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a scan report attached only to a mutable tag.

**Expected evidence:** Resolve the exact scanned artifact before using the result.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain why zero findings is not a universal security proof.

**Expected evidence:** Scanners have scope and knowledge limitations.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a patch decision record.

**Expected evidence:** Finding, affected artifact, chosen action, tests and residual risk.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a scan report attached only to a mutable tag. Use its expected observation, Resolve the exact scanned artifact before using the result., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/build/building/best-practices/)
- [Official reference 2](https://docs.docker.com/scout/explore/exceptions/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-030: Vulnerability findings, patching and dependency updates.
Read courses/docker/guides/docker-030.md and courses/docker/lessons/docker-030.md. Direct prerequisites: `docker-029`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
