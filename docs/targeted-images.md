# Targeted native Docker image checks and partial publication

The targeted workflow selects one complete qualification group from the pushed
HEAD commit message. Its source of truth is
[`docker/ci-profile-groups.json`](../docker/ci-profile-groups.json). Each ordinary
profile name is also an alias for the group that contains it. A profile alias
therefore builds and checks every profile in that group.

| HEAD marker | Allowed push | Work performed |
| --- | --- | --- |
| `[build-test-ALIAS]` | Any branch | Build and qualify native Linux AMD64 and ARM64 App, Python Core and the selected complete group. No Docker Hub credentials, image uploads, starter ZIP or canonical tags are used. |
| `[publish-ALIAS]` | `main` only | Pass the exact revision's source and portable starter checks, build and qualify both native platforms, stage qualified digests, then publish App, Core and the selected complete group. |
| `[publish-docker]` | `main` only | Run the separate complete publisher for every ordinary profile. |

Use exactly one Docker marker in the HEAD message. Unknown, malformed and
multiple markers fail the intent check. A marker on an earlier commit in the
same push does not select a release. `js` is a short alias for the
`javascript-typescript` group, which contains both `javascript-node` and
`typescript-node`. For example, `[build-test-js]` checks both workers, and
`[publish-javascript-node]` publishes both workers after qualification. The
`python-core` group selects only App and Core.

## Using a partial release

A successful targeted publish creates combined AMD64 and ARM64 version indexes
for App, Core and the selected worker profiles. The app and selected indexes
carry `io.ds60.release.scope=partial` and the canonical
`io.ds60.release.group` annotation. The promotion receipt lists the exact
selected profiles. No unselected worker version tag or latest alias is written.
Selected worker latest aliases move only after all selected immutable version
tags are verified, and App latest moves last. An older rerun does not move
latest backward.

Use a matching source checkout or starter ZIP and select only published
profiles. The accepted partial 1.0.0 App/Core/JS/TS release is explicitly
selected with:

```sh
./classroom --profile javascript-node --profile typescript-node \
  --from-hub YOUR_DOCKERHUB_USER --tag 1.0.0
```

`./classroom` includes Python Core with explicit worker selections. The same
selection can use the app's default latest pointer on a new Hub project when
that pointer resolves to the matching source version. Do not use `--all` for a
partial release. The complete publisher is the route that qualifies and
publishes all ordinary profiles.

Version tags are immutable. A targeted run refuses an occupied version tag
from another source revision, including an unselected profile's tag. To run a
later complete `[publish-docker]` release from a changed source commit, bump
the checked-in patch version first. Do not assign a new registry-only tag to
the old source.

## Qualification and retries

Both build-test and publication runs retain small qualification JSON reports as
GitHub Actions artifacts, including bounded redacted diagnostics from failed
owned service projects. These report uploads do not upload images or write
Docker Hub tags. Look for the native `seed-checks` or `worker-checks` artifact
for the failing group and architecture. Private `.workshop` directories,
credential files and raw service logs are not uploaded by this step.

Publication waits for the exact marked revision's source checks and portable
starter job, then rechecks them before canonical writes. Native App/Core and
selected worker receipts bind their source revision, workflow run and attempt,
platform, tested image IDs, qualification reports and selected seed digests.
Promotion requires both native platforms and every selected group receipt.
Candidate staging uploads are not a completed release.

After successful promotion, a separate hosted acceptance job reads that run's
published receipt, checks the selected combined indexes, then pulls and starts
a fresh classroom on native AMD64 and ARM64 runners. It verifies that the
launcher pins the release, that the selected worker is available, and that
stop/resume retains PostgreSQL and worker container IDs, saved selections,
learning/database volume names and a learner marker. If Docker reassigns the
dynamic browser port, only the App container may be recreated from the same
image to repair its public-port setting. The result and any bounded diagnostics
are retained as separate acceptance artifacts.
Canonical version and latest tags may already be published if this later
acceptance fails. Inspect its receipt and repair the concrete failure before
describing the release as ready for learners; do not treat promotion alone as
a passed fresh-install check. The partial 1.0.0 promotion succeeded,
but its original post-promotion assertion rejected an expected App-only port
repair. A separate [read-only native reverification](https://github.com/sadatnfs/ds60sqlpy/actions/runs/40787547771)
accepted the same immutable tags on both architectures with saved-volume and
browser readback checks. The old publisher run remains failed overall; no
1.0.0 tag was repushed. A full release from later source requires a new
checked-in version such as 1.0.1 and its own acceptance.

If a qualification job fails, re-run the failed job and use successful receipts
from the same workflow run and revision. A failed promotion may finish matching
version tags from those original qualified digests. A new run or a rebuilt seed
cannot silently replace an already published version. Inspect the workflow
result, promotion receipt and published manifests before announcing that a
profile is available.
