# docker-026: Compose overrides, profiles and configuration review

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-025`

## Learning objectives

Create an override for a public message. Write a reviewable configuration launch record. Use override file, merge rules and profiles accurately when you explain what you observed.

## Purpose, vocabulary and mental model

An override file changes a base Compose application model. Profiles select optional services. Both mechanisms can make one project support development, teaching and operations tasks, but they also create more possible effective configurations to review.

The effective model matters more than any one input file. Merge rules differ for scalar values, mappings and sequences. An override can unexpectedly add ports or mounts rather than replace the intended list in the way a beginner assumes. Always inspect or validate the combined model before applying it.

Profiles are not a security boundary. A service omitted from the default startup is still available when explicitly selected or enabled. Use profiles for intentional optional tools and workloads, not for hiding privileged services in a file and assuming they cannot run.

### Key terms

- **Override file:** A Compose file layered on a base file that changes or adds to the application model.
- **Merge rules:** The rules for combining Compose files, which differ for scalar values, mappings and sequences such as ports.
- **Profile:** A label that makes a service optional, so it starts only when that profile is enabled or the service is named.
- **Effective model:** The combined configuration after every file, override and interpolation has been applied.
- **`docker compose config`:** The command that renders and validates the effective model without starting anything.

## Anatomy and a trace you can follow

The fixture’s client has the tools profile. Ordinary `up` starts the app; an explicit tools invocation runs the peer check. For an override experiment, copy the fixture and change only a public message or unused loopback host port. Use `-f` in a fixed order and validate that same order.

Do not print a fully rendered production model containing secrets into a public log. This lesson uses synthetic public values. The goal is to explain which input supplied each final field and how a reviewer can reproduce the exact model.

## How to use this lesson

The classroom saves `courses/docker/lessons/docker-026.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Work in a scratch copy of the fixture so the committed files stay unchanged. Create `compose.study.yaml` holding only `services:`, `app:`, `environment:` and `APP_MESSAGE: override from study file`, then render `docker compose -p ds60-docker-study -f compose.yaml -f compose.study.yaml config` and find the new message under `app`. Add a `ports:` entry of `"127.0.0.1:18081:8080"` to the same override and render again: the effective list now holds both 18080 and 18081, one after the other. Next compare `docker compose -p ds60-docker-study config --services`, which prints only `app`, with the same command after `--profile tools`, which prints `app` and `client`; `config --profiles` prints `tools`. None of these commands creates a container, network or volume, so deleting the scratch copy is the whole cleanup, and the rendered output is the record you keep.

## Worked example / walkthrough

### Worked example 1: Enable the optional client intentionally

The fixture keeps this service out of ordinary startup.

```sh
docker compose -p ds60-docker-study --profile tools run --rm client
```

**Expected observation:** A short peer request is executed; the client container is removed after completion.

### Worked example 2: Review a combined model

Use two files in your own scratch copy.

```sh
docker compose -p ds60-docker-study -f compose.yaml -f compose.study.yaml config --quiet
```

**Expected observation:** The exact ordered combination validates without creating resources.

## Six progressive exercises

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

### Exercise 1: Distinguish profiles and overrides.

**Hint:** Ask which one chooses services and which one changes service definitions.

### Exercise 2: Predict ordinary startup with the tools profile disabled.

**Hint:** Check which services have a profiles key.

### Exercise 3: Create an override for a public message.

**Expected evidence:** Only the intended environment value changes in the effective model.

**Hint:** Put only the changed environment value in the override file.

### Exercise 4: Diagnose an unexpected extra port after merging.

**Hint:** Run docker compose config with the same files and read the merged ports.

### Exercise 5: Explain why a profile is not access control.

**Hint:** Ask who can run docker compose --profile tools.

### Exercise 6: Write a reviewable configuration launch record.

**Expected evidence:** Ordered files, profiles, project name and safe resolved settings.

**Hint:** Record the files in order, the profiles and the project name you used.

## Common mistakes and diagnosis

Forgetting that Compose merges list fields such as `ports` instead of replacing them. Using profiles as a security boundary. Launching with a different file order than the one you reviewed.

Exercise 4 is this chapter's boundary case: Diagnose an unexpected extra port after merging. Render the merged model with `docker compose config` and read the complete `ports` list for the service before assuming an override replaced it.

Naming your override `compose.override.yaml` feels tidy, but Compose loads a file with exactly that name automatically whenever a command runs without `-f`. Every plain `docker compose up` in that directory then carries your study message and extra port, and the project you reviewed with explicit files is no longer the one people launch by habit. The symptom is a setting nobody passed on the command line. List `compose*.yaml` in the directory and render `docker compose config` with no flags to see what a bare command really uses. Keep study overrides under a name Compose does not pick up, such as `compose.study.yaml`, and pass them with `-f` so the choice is visible in every command you record.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** Predict the merged `ports` list when both Compose files declare a port for the same service.

**Transfer case.** A teammate adds `ports: []` to an override, expecting the app to run with no published port for a private test. What does the rendered model show, and how would you actually remove the mapping?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

## Primary references

- [Merge Compose files](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)
- [Compose profiles](https://docs.docker.com/compose/how-tos/profiles/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-026: Compose overrides, profiles and configuration review.
Read courses/docker/guides/docker-026.md and courses/docker/lessons/docker-026.md. Direct prerequisites: `docker-025`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
