# docker-042: Advanced capstone: a release, recovery and teaching handoff

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-041`

## Learning objectives

Assemble a source-bound release packet. Teach the full system and defend its limits. Use release record, recovery rehearsal and handoff accurately when you explain what you observed.

## Purpose, vocabulary and mental model

The final project is a compact release system rather than a larger application. Starting from the maintained fixture, produce a source-controlled build, an identified image, runtime acceptance, persistence and restore evidence, and a readable operator handoff. The aim is independent reasoning across the complete lifecycle.

An expert explanation separates facts from assumptions. It names the tested engine and platform, the image identity, the source inputs and the behavior actually observed. It can explain why a failure occurs at one layer and which next observation would disprove that explanation. It also knows when a simple local project does not meet public-service or multi-host requirements.

No capstone can certify expertise by itself. Use it to identify gaps: if you cannot explain a mount, signal, cache, network hop or recovery boundary, return to the relevant chapter. Repetition with a changed input is more valuable than copying a completed recipe.

### Key terms

- **Release record:** A document tying an image identity to its source inputs, tested engine and platform, and observed behavior.
- **Recovery rehearsal:** Practicing backup and restore against a disposable target to prove the recovery procedure works.
- **Handoff:** Passing a system to another operator with enough evidence and instructions to run it independently.
- **Acceptance evidence:** Recorded observations that show the released image meets its runtime, persistence and restore requirements.
- **Assumption:** A belief not yet verified, which a good release explanation keeps separate from observed facts.

## Anatomy and a trace you can follow

Create a fresh learner copy, keep public synthetic configuration, build visibly, qualify host and peer requests, test one controlled failure, recreate the app, export and independently restore data, and stop owned resources. Preserve an optional image archive for offline transfer without pushing it anywhere.

Your handoff should contain a diagram, command sequence, expected outputs, failure decision tree and explicit retention policy. Include a coverage table with source checks, image build, actual runtime, browser observation, persistence and restore as separate rows. Mark untested engines or architectures honestly.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-042.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

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

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Predict all outcomes before running the final project.

**Hint:** Write the expected result for the normal, failure, replacement and recovery cases first.

### Exercise 2: Change one noncritical configuration and rebuild or recreate appropriately.

**Expected evidence:** The chosen lifecycle action matches the kind of change.

**Hint:** Decide whether the change needs a rebuild or only a recreation.

### Exercise 3: Assemble a source-bound release packet.

**Expected evidence:** Exact source, image, platform, commands and observations.

**Hint:** Tie every observation to the exact source revision and image identity.

### Exercise 4: Diagnose a deliberate single-layer failure.

**Hint:** Break one layer only and collect the smallest evidence that locates it.

### Exercise 5: Prove independent data recovery.

**Expected evidence:** A new owned target serves the preserved expected state.

**Hint:** Restore into a new target and read the value through the app.

### Exercise 6: Teach the full system and defend its limits.

**Expected evidence:** A beginner can follow the handoff and identify what it does not guarantee.

**Hint:** Explain the system to a beginner and list what it does not guarantee.

## Common mistakes and diagnosis

Running the final project before writing predictions. Rebuilding when only configuration changed, or only recreating when the image changed. Presenting the handoff without its limits.

Exercise 4 is this chapter's boundary case: Diagnose a deliberate single-layer failure. Write down the single layer you changed, the first observation that failed, and the request that proves the repair, before running the full acceptance again. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. Trace one browser request through the system and one peer request, naming every port. Then reconstruct worked example 2 (Explain one complete request) with one different value, predict what changes, and name which of release record, recovery rehearsal, handoff and acceptance evidence the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [Building best practices](https://docs.docker.com/build/building/best-practices/)
- [Compose in production](https://docs.docker.com/compose/production/)

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
