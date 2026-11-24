---
phase: 07-docker-runtime-persistence-qualification
plan: 02
subsystem: classroom-runtime
status: complete
requirements: [RUN-02]
tags: [docker, lifecycle, persistence, harness]
key-files:
  created:
    - scripts/check_classroom_lifecycle.py
    - tests/test_classroom_lifecycle.py
    - tests/test_check_lab_http_sentinel.py
  modified:
    - scripts/check_lab_http.py
commits: none by executor (orchestrator commits; exec rules forbid git add or commit)
completed: 2026-11-24
---

# Phase 7 Plan 02: Disposable Classroom Lifecycle Harness Summary

This plan adds a ds60-p7 lifecycle harness. It runs a real classroom stack through fresh, stop, resume, rerun, restart, recreate, update and final-rerun. After each step it checks that volumes, the module token, learner files and a SQL sentinel all survived, then removes only resources it can prove it owns and diffs the protected environment.

## What was built

- **scripts/check_lab_http.py** (+61 lines): new `--sql-sentinel NAME:TOKEN` option.
  - NAME must match `^p7_[a-z0-9_]{1,40}$` and TOKEN must match `^[A-Za-z0-9]{8,64}$`. Invalid values cause `parser.error` before any HTTP call.
  - Seed mode creates `public.NAME` on lesson sql-start-01 and inserts TOKEN.
  - With `--check-persistence`, it requires exactly `[[TOKEN]]` and prints `SQL sentinel survived.`
  - Behavior is unchanged when the option is absent.
- **scripts/check_classroom_lifecycle.py** (927 lines, mypy strict, ruff clean).
  - It refuses to run unless the project name starts with `ds60-p7-`, and also refuses on any preexisting project resources, worktree or p7 tag.
  - It snapshots the protected environment, creates a worktree at `work/p7-worktrees/<P>`, and writes an ownership marker (`p7-owner.json`) before any Docker write.
  - It runs the steps through the real `./classroom` launcher and verifies each one.
  - In a `finally` block it checks the marker, then runs `down -v --remove-orphans`, removes the owned p7 tags and removes the worktree. It then runs a residue check and the protected diff.
  - It contains no prune command.
  - The report holds the sentinel only as sha256, and argv in logs and the report is redacted.
  - Exit codes: 0 passed, 1 failed, 2 refused.
- **Tests:** 39 lifecycle tests using a fake engine runner, plus 15 sentinel tests. Both files were written first and seen to fail (ImportError and 5 failing tests).

## Commands and real results

| Command | Result |
| --- | --- |
| `pytest -n 0 --basetemp=work/test-tmp-07-02 -q tests/test_classroom_lifecycle.py tests/test_check_lab_http_sentinel.py tests/test_classroom_launchers.py` | 243 passed in 291s |
| `ruff check src scripts tests` | All checks passed |
| `mypy --strict scripts/check_classroom_lifecycle.py scripts/check_lab_http.py` | no issues in 2 files |
| `mypy src` | no issues in 62 files |
| `set -a; . ./.env; set +a; ./scripts/lint-repo` | exit 0, "Lint checks passed." |
| `grep -c prune scripts/check_classroom_lifecycle.py` | 0 |
| en/em dash count in the 4 files | 0 each |

**Tracer:**
- Command: `ds60-p7-tracer-e837c8`, `--base HEAD --target HEAD --steps fresh,stop,resume --seed-images 1.4.3 --report work/p7-lifecycle-tracer.json`
- Result: exit 0, with up 25.0s, the seed probe 9.0s, stop 2.1s, resume 23.5s and the persistence probe 8.2s.
- Residue: none (no containers, volumes, networks, p7 tags or worktree).

**Full local run (Task 3):**
- Command: `ds60-p7-local-6d3d1279`, `--base HEAD~1 --target HEAD --seed-images 1.4.3 --report work/p7-lifecycle-local.json`
- Base: 0a3492ab54d74860ea6bfdd66a9801d77208713e. Target: 5ad22de5443ca3567e221032de0580ee224f4621. Architecture: arm64.
- Result: exit 0.

| Step | Commands and timings |
| --- | --- |
| fresh | up 29.5s, seed probe 8.0s |
| stop | 1.6s |
| resume | 17.6s, probe 6.7s |
| rerun | 4.6s, probe 2.7s |
| restart | stop 1.8s, start 25.0s, probe 7.8s |
| recreate | down without -v 0.7s, start 18.1s, probe 6.9s |
| update | skipped (see deviation 1) |
| final-rerun | 4.8s, probe 2.3s |

- Sentinel `p7_f6f6bd1e15f1` survived every step. Its token sha256 is 04cbc000...8c73.
- The plan's assertion passed: step list exact, `passed` true, `protected.errors` empty, `protected.warnings` empty.
- No project volumes remain.

**Protected environment:**
- `work/p7-protected-before.txt` and `work/p7-protected-after.txt` differ in one line: an ephemeral container `hardcore_hamilton` replaced by `nice_clarke`.
- Both come from the `ds60-formatting-julia` image and were created by an unrelated process during the run, not by this harness.
- All volumes, the shared image IDs and the ds60-classroom and ds60-phase1-browser compose states are identical.
- The scratch debug project `ds60-p7-dbg-686ba8` (from a `--keep` debugging run) was cleaned up manually after its marker was verified: down -v, its two p7 tags removed and its worktree removed. Zero residue.

## Deviations from Plan

1. **[Orchestrator instruction] Seeded images, update step skipped.**
   - `--seed-images 1.4.3` tags the existing local `ds60sqlpy-lab:1.4.3` and `ds60sqlpy-worker-python-core:1.4.3` to the owned p7 base tag, so no build runs.
   - In this mode the update step is recorded as skipped with a reason, and the step list still contains `update`.
   - The `git checkout --detach <target>` plus `--rebuild` path, the image ID comparison and the revision label check are covered by unit tests only.
2. **[Rule 3] Compose commands use explicit `--project-directory <wt> --env-file ... -f <wt>/compose.classroom.yaml -p P --profile '*'`.** A bare `docker compose -p P` would pick up the repo's default compose.yaml and miss profiled services.
3. **[Rule 1] Learner-state digests use coaching.json plus progress.json, not progress.json alone.** The plan assumed the `save` action writes progress.json, but it writes coaching.json; progress.json only appears when a lesson is completed. coaching.json must be 64-hex; progress.json may be "absent" or hex. Both must be unchanged across each transition.
4. **[Rule 1] Digest exec runs as `-u 1000:1000`.** The lab's default root user has `cap_drop: ALL` and cannot read learner-owned files.
5. **Protected container disappearance or state change is a warning, not an error.** awesome-copilot MCP and similar ephemeral containers come and go. Volume removal and shared image ID changes are errors.
6. **The Task 3 precondition ("Tasks 1 and 2 committed") could not hold**, because the exec rules forbid commits. The worktree at the base or target SHA provides only the launcher and compose files; the harness runs from the shared checkout, so this does not affect the result.

## Notes for 07-03

- Run the full step list in CI without `--seed-images`, so the update step does a real `--rebuild` from base to target, on both amd64 and arm64.
- CI project names must keep the `ds60-p7-` prefix (the harness refuses anything else) or the regex must be widened deliberately.
- The harness uses `sys.executable` for probes, so it works under setup-python.
- The launcher hardcodes release_version 1.4.3. With port 0, every start after a stop picks a new port and the launcher recreates the lab container. The harness allows a lab ID change only when the port changed.
- `--keep` leaves the stack up for debugging. Cleanup then has to be done manually after checking the marker.
- Evidence is in `work/p7-lifecycle-local.json`, `work/p7-lifecycle-tracer.json` and `work/p7-logs/<project>/`, all token-redacted.

## Self-Check: PASSED

- All 4 code files exist, and both reports exist with `passed` true.
- No commits were expected from this executor.
