# docker-030: Vulnerability findings, patching and dependency updates

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-029`

## Learning objectives

Design a minimal base-image update. Write a patch decision record. Use vulnerability finding, affected version and base image update accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A vulnerability finding connects an affected component version to a published issue under a scanner’s knowledge and matching rules. It is evidence for investigation, not a complete exploitability assessment. False matches, missing packages, runtime exposure and available fixes all influence the response.

Patching an image generally means rebuilding from updated inputs and replacing containers with the new image. Installing packages interactively inside a running container makes an untracked difference that disappears on recreation. The maintained build recipe and lock inputs must describe the repair.

A rebuild can introduce regressions as well as fixes. Use a small update scope, preserve the old immutable artifact, run the relevant tests and verify the actual final image. Do not claim that a passing scan proves absence of all vulnerabilities or that an unfixed low-severity finding is automatically harmless.

## Anatomy and a trace you can follow

Classify findings by component, installed version, fixed version if available, application reachability and required action. Keep the scanner database timestamp and artifact digest. A tag-based report becomes stale when the tag changes.

For this lesson, use a synthetic finding table and prepare an update plan without downloading a scanner or changing the engine. Actual scanning is an optional explicitly prepared tool workflow. The course does not invent a zero-findings badge for an unscanned image.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-030.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Read a synthetic finding

The package and versions are illustrative.

```json
{
  "component": "example-library",
  "installed": "1.0",
  "fixed": "1.1",
  "artifact": "specific image digest",
  "status": "requires review"
}
```

**Expected observation:** The record is input to a patch decision, not proof of exploitation or a completed fix.

### Worked example 2: Trace a reproducible patch

This is the required sequence.

```text
update declared input -> build new image -> run tests -> inspect exact digest -> replace owned container -> verify behavior
```

**Expected observation:** An interactive package install inside the old container is not the maintained release artifact.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Separate vulnerability presence and exploitability.

**Expected evidence:** A matched affected component versus a demonstrated reachable exploit condition.

**Hint:** Ask whether the vulnerable code is reachable in this app.

### Exercise 2: Predict why an interactive patch disappears.

**Hint:** Ask what docker compose up does to a container's writable layer.

### Exercise 3: Design a minimal base-image update.

**Expected evidence:** Change the resolved base deliberately and rerun relevant acceptance.

**Hint:** Change the base image reference and rerun the same acceptance checks.

### Exercise 4: Diagnose a scan report attached only to a mutable tag.

**Hint:** Resolve the tag to a digest before trusting the report.

### Exercise 5: Explain why zero findings is not a universal security proof.

**Hint:** Ask what the scanner's database and matching rules cover.

### Exercise 6: Write a patch decision record.

**Expected evidence:** Finding, affected artifact, chosen action, tests and residual risk.

**Hint:** Record the finding, the artifact, the decision, the tests and the remaining risk.

## Common mistakes and diagnosis

Patching inside a running container instead of rebuilding the image. Reading zero findings as proof of safety. Applying a scan result to a tag that now points elsewhere.

Exercise 4 is this chapter's boundary case: Diagnose a scan report attached only to a mutable tag. Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status; an application request adds another layer, and a healthy container can still serve the wrong result. Preserve the original failure and the exact changed field before retrying. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here, using vulnerability finding, affected version, base image update and rebuild and retest. Reconstruct worked example 2 (Trace a reproducible patch) with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild, or why none of those operations applies to this mechanism.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Docker Scout exceptions](https://docs.docker.com/scout/explore/exceptions/)

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
