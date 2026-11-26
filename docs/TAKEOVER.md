# Progress and agent takeover

Snapshot: 2026-11-25. This file is a handoff, not a new backlog.
Read `AGENTS.md` first; historical phase instructions do not override the
current owner policy.

## What is delivered

| Area | State |
| --- | --- |
| Classroom overhaul | All 44 implementation plans completed. Phase 11 verified; the owner requested closeout. |
| Published classroom | v2.1.1 is the latest published release, from `658d0cea`, with 62 Docker Hub tags and native AMD64/ARM64 pull/resume acceptance. See [release evidence](dockerhub.md). |
| Apache download repair | `627a0396` moves retired Pinot 1.5.1 to Apache's archive, adds archive fallback for Kafka/Cassandra/Flink and extends binary preparation to 900 seconds. Flink's identity-bound artifact lock is unchanged. |
| CVE policy change | `d1f9ddde` removes automatic image scans from full and targeted workflows. Release staging no longer requires `--scan`; receipts explicitly report scans as not requested. Runtime, source/digest, secret and CodeQL checks remain. |
| CVE PR automation | GitHub automated security-fix PRs were disabled and read back as disabled. No alerts were dismissed. The historical 94 exception proposals no longer need renewal. |
| New computer | [Fresh-machine onboarding](fresh-machine.md) supplies clone, published-image, contributor and assistant routes without prior chat or local caches. |
| Local cleanup | DS60 images and containers were removed earlier. Learner volumes and unrelated services were retained. No classroom images were rebuilt for this closeout. |
| Branch preservation | Old checkpoint tips are ancestors of `main`. Four unmerged dependency proposals were preserved as remote `archive/2026-11-25/dependabot-uv-*` tags rather than merged into working code. |
| Clean branch state | The local checkout and upstream are `main`. All six other remote branches and the local checkpoint branch were deleted after preservation; only `main` remains. |

The latest source on `main` contains changes after the v2.1.1 release tag.
Those changes are **not** retroactively baked into published v2.1.1 images.
Do not overwrite immutable release tags, bump a version or publish new images
merely to complete this handoff.

## Verification already performed

For the CVE opt-in change, the focused offline suite passed **335 tests** across
`test_docker_release.py`, `test_ci_scientific_projects.py`,
`test_ci_contract.py`, `test_image_scan.py`, `test_ci_hub_acceptance.py` and
`test_ci_release_artifacts.py`. Coverage includes ordinary/scientific staging
without scans, promotion past expired historical policy, explicit not-requested
records, and rejection of invalid scan evidence when deliberately supplied.
Ruff lint/format checks passed. Repository guidance checked 194 documents and
37 module subjects with zero failures, and the tracked-file dash check passed.

These are source/unit checks, not a new Docker build or hosted CI result.
The final `main` GitHub Actions outcome was not confirmed at handoff.
Read current runs rather than treating older cancelled, queued or failed runs
as evidence for this revision.

The whole-workspace sensitive-content check flagged the pre-existing local
`.env` filename. It was confirmed ignored and absent from tracked files; its
contents were not read or committed. Do not copy that file into a fresh clone
or describe that workspace-wide scan as passed.

## What is not claimed complete

- Human walkthroughs for Phases 1 and 6 and the R11 clarity review were not
  performed. They are deferred and must not be relabeled as passed.
- Final closeout CI must be checked against the exact revision if the owner
  asks for verification. The previous Apache download timeout has a source fix;
  success of a previous release is not proof of a later branch run.
- A new machine needs Docker and initial downloads. Git contains no learner
  volumes, local credentials, Docker caches or private execution state.
- A historical machine-local GSD config/state stash was preserved on the old
  computer rather than committed. It is not needed to resume development.

## Prompt: verify the handoff

> Work in the existing ds60sqlpy checkout on main. Read AGENTS.md,
> docs/TAKEOVER.md, docs/fresh-machine.md and .planning/STATE.md. Inspect the
> working tree before changing it and preserve other agents' edits. Confirm
> origin/main and inspect GitHub Actions for that exact revision. Fix only
> functional regressions or incomplete closeout work; distinguish old failed
> runs from current failures. CVE scans, CVE-only remediation and exception
> renewal are out of scope unless I explicitly ask. Do not dismiss alerts,
> restart completed GSD phases, publish images or erase learner volumes.
> Report the exact commit, actual results and anything still unverified.

## Prompt: set up the classroom on a new computer

> Onboard this repository from scratch using AGENTS.md and
> docs/fresh-machine.md. Keep the maintainer checkout on main. Inspect
> prerequisites first, then use the documented v2.1.1 released worktree and
> published images for learning, or the main source route if I request current
> development. Use the approved package feeds on this computer and keep
> environments out of cloud-synchronized folders. Verify the printed classroom
> address and actual readiness. Preserve any existing learner data. Do not
> assume old conversations, credentials, Docker images or GSD state exist.

## Prompt: resume development

> Read AGENTS.md, docs/TAKEOVER.md and CONTRIBUTING.md on main, then work only
> on the new task I provide. Read the closest subject guidance and change
> canonical sources rather than generated readers. Preserve lesson IDs,
> learner state and local isolation. Run focused checks and report exact
> evidence. Do not revive the old zero-CVE requirement or reopen completed
> phases. Code pushes and image publication are separate authorizations.

## Useful inspection commands

```sh
git status --short --branch
git log -5 --oneline
git branch -a
git tag --list 'archive/2026-11-25/*'
gh run list --repo sadatnfs/ds60sqlpy --branch main --limit 10
gh release view v2.1.1 --repo sadatnfs/ds60sqlpy
```

GitHub reads require an appropriate signed-in account; never place tokens in
commands, committed files or handoff reports. To find architecture, curriculum,
runtime and release owners, follow the maintained source map in `AGENTS.md`.
