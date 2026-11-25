# docker-026: explanatory solutions

These answers explain teaching fixtures, not engine results; the mechanism is in [the guide](../guides/docker-026.md).

## Exercise 1: Distinguish profiles and overrides.

**Expected answer:** Service selection versus model composition.

**Why:** A profile determines which optional services participate; an override modifies service and resource definitions. They can be used together but answer different questions.

**Approach:** Ask two separate questions: which services run (profiles), and what each service's settings are (the ordered -f files).

**Why this is correct:** The tools profile only adds client to the selection; compose.study.yaml changes fields of services that already exist.

**A plausible wrong approach:** Putting a changed APP_MESSAGE in a profile expecting it to alter app misreads profiles as a way to set fields.

**How to verify:** docker compose config with and without --profile tools shows client appearing, while only the override changes app's fields.

## Exercise 2: Predict ordinary startup with the tools profile disabled.

**Expected answer:** The app starts and the optional client is not a persistent service.

**Why:** The profile communicates intent. An explicit run of the client remains possible, so its commands still need review.

**Approach:** Read profiles: [tools] on client and note that ordinary up does not start profiled services.

**Why this is correct:** Plain up starts app only, so nothing needs to be stopped to remove the client afterward.

**A plausible wrong approach:** Expecting client to start with up and finding it missing does not indicate a broken model.

**How to verify:** After up --wait, docker compose ps lists app only; the explicit run in worked example 1 still runs client once.

## Exercise 3: Create an override for a public message.

**Expected evidence:** Only the intended environment value changes in the effective model.

**Why:** Keep the experiment narrow enough to inspect. Avoid mixing a message edit with mounts, privilege changes and network modifications.

**Approach:** Write an override containing only services, app, environment and APP_MESSAGE, and compare the merged config with the base.

**Why this is correct:** With a single changed field, any other difference in the merged output would show a mistake in the override.

**A plausible wrong approach:** Changing the message while also adding a mount and dropping read_only makes it unclear which edit caused a later failure.

**How to verify:** The merged config differs from the base in APP_MESSAGE only, and GET / returns the new message.

## Exercise 4: Diagnose an unexpected extra port after merging.

**Expected answer:** Inspect merge behavior and the complete effective ports list.

**Why:** Do not assume a sequence was replaced. Model composition must be understood for the actual Compose version and fields used.

**Approach:** Print the full merged ports list from config and compare it with each file's ports, in the order the -f flags were given.

**Why this is correct:** Compose combines some lists, such as ports, rather than replacing them, so a later file can add a mapping.

**A plausible wrong approach:** Assuming the override's ports replaced the base's leads you to remove the wrong line.

**How to verify:** The config output shows which file contributed the extra mapping, and removing it restores 127.0.0.1:18080 only.

## Exercise 5: Explain why a profile is not access control.

**Expected answer:** Someone with engine and project access can enable it.

**Why:** Security should come from permissions and the absence of unnecessary authority, not from an optional default selection.

**Approach:** Ask who can run docker compose for this project: anyone who can reach the engine can pass --profile tools.

**Why this is correct:** A profile changes default selection for convenience; it checks no identity and grants or denies nothing.

**A plausible wrong approach:** Hiding an admin service behind a profile as protection leaves it one flag away for any engine user.

**How to verify:** A different user with engine access runs --profile tools and starts the service with no extra check.

## Exercise 6: Write a reviewable configuration launch record.

**Expected evidence:** Ordered files, profiles, project name and safe resolved settings.

**Why:** This makes the effective deployment reproducible. Retain private values separately rather than embedding them in shared evidence.

**Approach:** Write down the project name, the -f files in order, the profiles enabled, and the resolved settings with private values removed.

**Why this is correct:** Order matters because later files override earlier ones; without it, someone else gets a different effective model.

**A plausible wrong approach:** Pasting the full config output, including resolved secrets, into the launch record exposes them.

**How to verify:** Another person reruns config with the recorded flags and gets the same output apart from the redacted values.

## Check your transfer

An empty list merges into the inherited one and adds nothing, so `config` still shows `127.0.0.1:18080` and the port stays published. Compose provides the `!reset` YAML tag for this case: `ports: !reset []` in the override clears the inherited list, and the rendered `app` service then has no `ports` key at all. Accept the change only when `config` shows that and, after `up`, `docker compose port app 8080` reports no mapping. If `config` still lists 18080, the override was not included or your Compose release predates `!reset`.
