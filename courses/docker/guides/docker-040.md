# docker-040: Runtime secrets, configuration files and controlled disclosure

## Level and prerequisites

Advanced; about 120 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-039`

## Learning objectives

Design a no-disclosure validation message. Write a secret data-flow review. Use runtime secret, secret file and /run/secrets accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A runtime secret is sensitive input required while an application runs. It has a different lifecycle from a build secret. Compose can expose declared secrets as files to selected services, while ordinary configuration can be passed through environment variables or files. The exact storage and protection depend on the deployment platform.

Local Compose file-based secrets are not a universal encrypted secret vault. The source file exists on the host and must be protected there. File mounts can avoid some environment-variable exposure paths, but the application can still read and accidentally log the value. Secret handling is a complete data-flow concern.

This lesson uses only an invented value. Never copy a real credential into the repository, a screenshot or a public report. The course fixture needs no password, so the optional example belongs in a separate scratch project and demonstrates a file-reading contract rather than adding a secret requirement to the app.

### Key terms

- **Runtime secret:** Sensitive input an application needs while it runs, with a different lifecycle from a build secret.
- **Secret file:** A file that Compose mounts into a selected service to deliver a declared secret's value.
- **/run/secrets:** The in-container directory where Compose places declared secrets as files.
- **Controlled disclosure:** Exposing a secret only to the processes that need it and keeping it out of logs, reports and screenshots.
- **Rotation:** Replacing a secret value with a new one and retiring the old value without exposing either.

## Anatomy and a trace you can follow

A top-level `secrets` entry declares a source, and a service grants itself access by name. Inside the service the file commonly appears under `/run/secrets/NAME`. The app must explicitly read that file or support a documented file-based configuration option.

Rotate a credential by updating the controlled source and applying the appropriate service lifecycle, then verify the new identity and revoke the old credential according to the external service policy. A container restart alone does not prove that an old credential has been invalidated.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-040.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Rehearse a file secret in a scratch copy of the fixture. Write a throwaway value with `printf 'study-only-value' > demo-secret.txt`, and put the top-level `secrets:` block and the service grant from worked example 1 in a `compose.secret.yaml` override. Render `docker compose -p ds60-docker-study -f compose.yaml -f compose.secret.yaml config` and confirm that `app` lists `demo`. Start the app with both files and `up -d --wait`, then run `docker compose -p ds60-docker-study exec app python -c "from pathlib import Path; print(len(Path('/run/secrets/demo').read_text().strip()) > 0)"`, which prints `True` without revealing the value. Search `docker inspect` output for the app container for `study-only-value`: it is absent. Finish with a plain `up -d --wait` from the original file to recreate the app without the grant, then delete the override and the secret file.

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

```python external
from pathlib import Path

value = Path("/run/secrets/demo").read_text().strip()
if not value:
    raise ValueError("demo secret is empty")
print("demo input is present")
```

**Expected observation:** The secret bytes are not printed; validation distinguishes empty input from a usable configured value.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Compare build and runtime secrets.

**Hint:** Ask when each secret is needed: during the build or while the app runs.

### Exercise 2: Predict whether a local secret file is automatically encrypted everywhere.

**Hint:** Check where the file lives on the host and who can read it.

### Exercise 3: Design a no-disclosure validation message.

**Expected evidence:** Report presence or a bounded error without the sensitive value.

**Hint:** Report whether the value exists and is well formed, never the value itself.

### Exercise 4: Diagnose a secret declared but not granted to a service.

**Hint:** Compare the top-level secrets key with the service's secrets list.

### Exercise 5: Explain credential rotation beyond restarting a container.

**Hint:** Ask whether the old credential still works after the restart.

### Exercise 6: Write a secret data-flow review.

**Expected evidence:** Source, host protection, service grant, read path, logs, rotation and deletion.

**Hint:** Trace the secret from its source to where the app reads it and where it could leak.

## Common mistakes and diagnosis

Passing secrets as environment variables that appear in `docker inspect`. Declaring a secret but not granting it to the service. Rotating by restarting without revoking the old credential.

Exercise 4 is this chapter's boundary case: Diagnose a secret declared but not granted to a service. Render the effective Compose model and read the service's `secrets` list before editing file permissions or adding a host mount.

Tightening the secret file with `chmod 600` feels like the responsible step, and on a Linux host it breaks the service. Without Swarm, Compose bind-mounts a file secret into `/run/secrets` with its host owner and mode, so a file readable only by your account is unreadable for UID 10001 in the container. The validator then fails with `PermissionError`, which looks like a missing secret. Docker Desktop's file sharing can mask the problem, so a setup that works on a laptop fails on a server. Grant read access to the container's identity instead, for example group 10001 with mode 640, and run the validator to prove the service can read it.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Recall how the validator proves the secret is present without printing it.

**Transfer case.** A teammate wants to bake a database password into the image with `ENV` so deployments need no extra files. What does that expose, and what would you propose instead?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Secrets in Compose](https://docs.docker.com/compose/how-tos/use-secrets/)
- [Compose file reference: secrets](https://docs.docker.com/reference/compose-file/secrets/)

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
