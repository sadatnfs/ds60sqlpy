# docker-040: Runtime secrets, configuration files and controlled disclosure

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-039`

## Learning objectives

Design a no-disclosure validation message. Write a secret data-flow review. Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

A runtime secret is sensitive input required while an application runs. It has a different lifecycle from a build secret. Compose can expose declared secrets as files to selected services, while ordinary configuration can be passed through environment variables or files. The exact storage and protection depend on the deployment platform.

Local Compose file-based secrets are not a universal encrypted secret vault. The source file exists on the host and must be protected there. File mounts can avoid some environment-variable exposure paths, but the application can still read and accidentally log the value. Secret handling is a complete data-flow concern.

This lesson uses only an invented value. Never copy a real credential into the repository, a screenshot or a public report. The course fixture needs no password, so the optional example belongs in a separate scratch project and demonstrates a file-reading contract rather than adding a secret requirement to the app.

## Anatomy and a trace you can follow

A top-level `secrets` entry declares a source, and a service grants itself access by name. Inside the service the file commonly appears under `/run/secrets/NAME`. The app must explicitly read that file or support a documented file-based configuration option.

Rotate a credential by updating the controlled source and applying the appropriate service lifecycle, then verify the new identity and revoke the old credential according to the external service policy. A container restart alone does not prove that an old credential has been invalidated.

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough

### Worked example 1: Review a synthetic secret file mount

This is a Compose fragment for a scratch project only.

```yaml
services:
  app:
    secrets: [demo]
secrets:
  demo:
    file: ./demo-secret.txt
```

**Expected observation:** Only the service granted demo can read its mounted file; host file protection remains relevant.

### Worked example 2: Validate presence without disclosure

The application should report a safe readiness fact.

```python
from pathlib import Path

value = Path("/run/secrets/demo").read_text().strip()
if not value:
    raise ValueError("demo secret is empty")
print("demo input is present")
```

**Expected observation:** The secret bytes are not printed; validation distinguishes empty input from a usable configured value.

## Six progressive exercises

### Exercise 1: Compare build and runtime secrets.

**Expected evidence:** Temporary build input versus application-time input.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 2: Predict whether a local secret file is automatically encrypted everywhere.

**Expected evidence:** No; host storage and platform behavior require separate protection.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 3: Design a no-disclosure validation message.

**Expected evidence:** Report presence or a bounded error without the sensitive value.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 4: Diagnose a secret declared but not granted to a service.

**Expected evidence:** The service lacks the intended mounted input.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 5: Explain credential rotation beyond restarting a container.

**Expected evidence:** New input must be applied and old authority revoked deliberately.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

### Exercise 6: Write a secret data-flow review.

**Expected evidence:** Source, host protection, service grant, read path, logs, rotation and deletion.

**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.

## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: Diagnose a secret declared but not granted to a service. Use its expected observation, The service lacks the intended mounted input., to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

- [Official reference 1](https://docs.docker.com/compose/how-tos/use-secrets/)
- [Official reference 2](https://docs.docker.com/reference/compose-file/secrets/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-040: Runtime secrets, configuration files and controlled disclosure.
Read courses/docker/guides/docker-040.md and courses/docker/lessons/docker-040.md. Direct prerequisites: `docker-039`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
