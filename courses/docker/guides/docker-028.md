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

The classroom saves `courses/docker/lessons/docker-028.md` and holds no engine socket ([host-lab setup](../STUDY-GUIDE.md#host-lab-setup)).

**Host lab.** Give the existing image a second name without contacting any registry: `docker image tag ds60-docker-study:local localhost:5000/ds60-study:rehearsal`. Run `docker image ls --format '{{.Repository}}:{{.Tag}} {{.ID}}'` and find both names beside one ID, because tagging only adds a reference. Read the new reference from left to right: `localhost:5000` is the registry, since a first component holding a port, a dot or the word `localhost` names a host; `ds60-study` is the repository; `rehearsal` is the tag. Compare `python:3.12-slim`, which expands to `docker.io/library/python:3.12-slim`, and the README's mirror reference, whose registry is `mirror.gcr.io`. Do not push. Remove the extra name with `docker image rm localhost:5000/ds60-study:rehearsal`; the engine prints `Untagged:` and keeps the image, which `docker image ls ds60-docker-study` confirms. Nothing else was created.

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

Answer-type prompts keep their answers in the solutions file ([exercise rules](../STUDY-GUIDE.md#exercise-rules)).

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

Exercise 4 is this chapter's boundary case: Diagnose an overwritten mutable release tag. Resolve the tag to its current digest and compare it with the digest recorded beside the earlier acceptance evidence.

A reference can carry a tag and a digest at once, such as `ds60-study:1.0@sha256:` followed by the hash, and it reads as if the engine checks both. It does not: when a digest is present, the pull resolves by digest alone and the tag plays no part in resolution, so a stale tag beside a correct digest still pulls the right bytes, and a familiar tag beside a wrong digest pulls whatever that digest names or fails. Reviewers who glance at the tag can approve an artifact they never meant to ship. In release records and deployment files, treat the digest as the identity and the tag as a label for people, and check the digest character by character against the release record, since nothing else in the reference is enforced.

Never trade a safety control for a passing example ([safety rules](../STUDY-GUIDE.md#safety-rules)).

## Retrieval, transfer and next steps

**Retrieval.** List the fields a release identity record needs and say which one never changes after publication.

**Transfer case.** `ds60-docker-study:local` and `registry.example.com/team/ds60-study:1.0` show the same image ID. If you remove the first name, does the second still run, and what would pushing the second create?

Then run the [retrieval loop](../STUDY-GUIDE.md#retrieval-and-cleanup) and end any host session with its cleanup.

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
