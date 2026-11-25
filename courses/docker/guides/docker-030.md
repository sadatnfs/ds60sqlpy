# docker-030: Vulnerability findings, patching and dependency updates

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-029`

## Learning objectives

Design a minimal base-image update. Write a patch decision record. Use vulnerability finding, affected version and base image update accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A vulnerability finding connects an affected component version to a published issue under a scanner’s knowledge and matching rules. It is evidence for investigation, not a complete exploitability assessment. False matches, missing packages, runtime exposure and available fixes all influence the response.

Patching an image generally means rebuilding from updated inputs and replacing containers with the new image. Installing packages interactively inside a running container makes an untracked difference that disappears on recreation. The maintained build recipe and lock inputs must describe the repair.

A rebuild can introduce regressions as well as fixes. Use a small update scope, preserve the old immutable artifact, run the relevant tests and verify the actual final image. Do not claim that a passing scan proves absence of all vulnerabilities or that an unfixed low-severity finding is automatically harmless.

### Key terms

- **Vulnerability finding:** A scanner's match between a component version and a published issue, which is evidence to investigate, not a verdict.
- **Affected version:** A component version that the published issue lists as vulnerable.
- **Scanner:** A tool that inventories an image's components and matches them against vulnerability data under its own rules.
- **Base image update:** Moving the `FROM` reference to a patched base so a rebuild picks up fixed operating-system packages.
- **Rebuild and retest:** Producing a new image from updated inputs and running the relevant tests on that final image before replacing containers.

## Anatomy and a trace you can follow

Classify findings by component, installed version, fixed version if available, application reachability and required action. Keep the scanner database timestamp and artifact digest. A tag-based report becomes stale when the tag changes.

For this lesson, use a synthetic finding table and prepare an update plan without downloading a scanner or changing the engine. Actual scanning is an optional explicitly prepared tool workflow. The course does not invent a zero-findings badge for an unscanned image.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-030.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** With the app running, try the patch-in-place habit and watch the fixture refuse it: `docker compose -p ds60-docker-study exec app python -c "open('/app/patched', 'w')"` fails with a read-only file system error, because the service sets `read_only`, and even a writable root would stop UID 10001 from writing into root-owned `/app`. Now take the inventory a finding would be matched against: `docker compose -p ds60-docker-study exec app python -c "import platform, ssl; print(platform.python_version(), ssl.OPENSSL_VERSION); print(open('/etc/os-release').read())"`. Write the Python version, the OpenSSL version and the Debian release next to the output of `docker image inspect --format '{{.Id}}' ds60-docker-study:local`. That pair, inventory plus identity, is what a patch decision cites. Nothing was changed, so there is no cleanup.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose a scan report attached only to a mutable tag. Resolve the tag named in the scan report to a digest, compare it with the deployed digest, and note the scanner's database date.

Running `docker compose build` again feels like patching, but with an unchanged Dockerfile and context every step is served from cache and the base comes from the local copy of the Python image, so the new image has the same ID as the old one and the same vulnerable packages. The build output gives it away with `CACHED` beside each step after `FROM`. A deliberate update refreshes the base, for example `docker compose -p ds60-docker-study build --pull app` where network access is allowed, or a new pinned base digest in the Dockerfile, and then compares image IDs: an unchanged ID means nothing was patched, whatever the command was called.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Trace the patch steps and name the identity you would record before replacing the container.

**Transfer case.** A scanner reports a finding in the base image's OpenSSL, but the fixture serves plain HTTP on loopback and never opens TLS itself. Do you patch now, defer, or accept the risk, and what goes in the record?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
