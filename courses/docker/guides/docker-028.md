# docker-028: Registries, tags, digests and deliberate publication

## Level and prerequisites

Intermediate; about 100 minutes, with additional time for the optional host experiment. Direct prerequisites: `docker-027`

## Learning objectives

Design a release identity record. Describe a safe publication review without performing it. Use registry, repository and tag accurately when you explain what you observed.

## Purpose, vocabulary and mental model

A registry stores image manifests and blobs for distribution. A repository groups related image names inside that registry. Authentication determines who can access the registry; authorization determines which operations that identity may perform. Public pull access is different from permission to overwrite a release tag.

A local tag does not publish anything. Publication is a deliberate operation with credentials, destination, retention and rollback implications. This course uses local builds and offline exports by default. You can study a registry workflow without pushing the course or your private code anywhere.

Mutable tags such as latest are useful conveniences but weak deployment identities. A release procedure should resolve or record an immutable digest and relate it to source, build inputs and acceptance evidence. A registry availability problem should not cause an operator to deploy a different unreviewed image merely because its tag looks similar.

### Key terms

- **Registry:** A service that stores image manifests and blobs for distribution.
- **Repository:** A group of related image names, with their tags, inside a registry.
- **Authorization:** The decision about which operations an authenticated identity may perform, such as pull but not overwrite.
- **Release tag:** A tag used for a published release, which a reviewed process should resolve to an immutable digest.
- **Publication review:** A deliberate check of credentials, destination, retention and rollback before anything is pushed.

## Anatomy and a trace you can follow

Read a reference as registry/repository:tag or registry/repository@digest. A tag may point to a platform index, which then selects a platform manifest. Keep that level of identity clear when comparing builds. Registry credentials belong in an approved credential store or short-lived CI mechanism, never in a Dockerfile.

The examples below inspect local metadata and a conceptual release record. They intentionally contain no push command. If you later publish your own project, make the destination and intended visibility explicit and verify the uploaded immutable identity after publication.

## How to use this lesson

The classroom displays this guide and saves your worksheet, `courses/docker/lessons/docker-028.md`. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example. **How to use the lessons** in the [subject README](../README.md) collects these rules in one place.

## Worked example / walkthrough

### Worked example 1: Inspect local tags without publication

This uses the locally built study image only.

```sh
docker image inspect ds60-docker-study:local --format "{{json .RepoTags}}"
```

**Expected observation:** The local tag is visible; this does not prove any registry has a copy.

### Worked example 2: Design a release identity record

Use real verified values in a private or public record as appropriate.

```json
{
  "source_revision": "recorded revision",
  "platform": "linux/amd64",
  "image_digest": "recorded immutable digest",
  "acceptance": "separate test receipt"
}
```

**Expected observation:** Each field has a distinct source of evidence; placeholder text is not a qualified release.

## Six progressive exercises

For each exercise, name the object involved and the phase of its lifetime before changing anything, then vary only the condition the task names. Exercises that ask you to predict, explain, compare or diagnose keep their answers in the solutions file; the others show the evidence to look for.

### Exercise 1: Parse the components of an image reference.

**Expected evidence:** Registry, repository, optional tag and optional digest.

**Hint:** Split a reference at the first slash, the colon and the @ sign.

### Exercise 2: Predict whether adding a local tag uploads bytes.

**Hint:** Check whether docker tag contacts a registry.

### Exercise 3: Design a release identity record.

**Expected evidence:** Source revision, immutable image identity, platform and tested behavior.

**Hint:** List what someone needs to identify exactly what you tested.

### Exercise 4: Diagnose an overwritten mutable release tag.

**Hint:** Compare the digest you recorded with what the tag resolves to now.

### Exercise 5: Explain why credentials do not belong in the build context.

**Hint:** Ask what happens to files in the build context during a build.

### Exercise 6: Describe a safe publication review without performing it.

**Hint:** Write the destination, visibility, artifact identity and rollback before any push.

## Common mistakes and diagnosis

Publishing by reusing a mutable tag such as `latest`. Leaving credentials in the build context. Assuming a local tag was uploaded.

Exercise 4 is this chapter's boundary case: Diagnose an overwritten mutable release tag. Resolve the tag to its current digest and compare it with the digest recorded beside the earlier acceptance evidence. Preserve the original failure and the exact changed field before retrying. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations first. List the fields a release identity record needs and say which one never changes after publication. Then reconstruct worked example 2 (Design a release identity record) with one different value, predict what changes, and name which of registry, repository, tag, digest and publication review the change touches.

When a host session ends, run `docker compose -p ds60-docker-study down` from your fixture copy. It removes the project's containers and network but keeps named volumes; deleting a volume is a separate, deliberate reset described in the fixture README.

## Primary references

- [What is a registry?](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-registry/)
- [docker login reference](https://docs.docker.com/reference/cli/docker/login/)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for docker-028: Registries, tags, digests and deliberate publication.
Read courses/docker/guides/docker-028.md and courses/docker/lessons/docker-028.md. Direct prerequisites: `docker-027`
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
