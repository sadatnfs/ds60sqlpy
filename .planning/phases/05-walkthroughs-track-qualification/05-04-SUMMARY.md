---
phase: 05-walkthroughs-track-qualification
plan: 04
subsystem: classroom-walkthroughs
status: complete
tags: [walkthroughs, python-tracks, data-tracks, ml-tracks, science-tracks]
requirements: [WALK-03, CURR-05]
requires: [05-02 walkthroughs.json format, scripts/check_walkthroughs.py, check_module_references corpus]
provides: [authored walkthroughs for 19 Python, data, ML and science tracks, one per stage]
affects: [05-05 track qualification closure]
key-files:
  created:
    - courses/statistics-ml/walkthroughs.json
    - courses/applied-science/walkthroughs.json
    - courses/bayesian-computing/walkthroughs.json
    - courses/data-visualization/walkthroughs.json
    - courses/data-ml-engineering/walkthroughs.json
    - courses/dbt/walkthroughs.json
    - courses/ml-engineering/walkthroughs.json
    - courses/polars/walkthroughs.json
    - courses/python-web/walkthroughs.json
    - courses/nlp/walkthroughs.json
    - courses/custom-likelihood-pytorch/walkthroughs.json
    - courses/deep-learning-pytorch/walkthroughs.json
    - courses/deep-learning-tensorflow/walkthroughs.json
    - courses/jax/walkthroughs.json
    - courses/llm-applied/walkthroughs.json
    - courses/llm-evaluation/walkthroughs.json
    - courses/llm-theory/walkthroughs.json
    - courses/advanced-spark-modeling/walkthroughs.json
    - courses/apache-data-platforms/walkthroughs.json
  modified: []
decisions:
  - Every expected_output string comes from a real local execution of the reference; none rely on the literal fallback.
  - Expected output avoids platform dependent floats, timings, byte counts and MCMC values; pass markers, exact integers, booleans and exact dyadic values are used instead.
  - llm-004 replaces llm-002 as the llm-theory beginner walkthrough because llm-002 prints softmax floats.
  - bayes-017 (Stan) is the bayesian-computing advanced walkthrough, executed with a locally built, sha256 verified CmdStan 2.40.0 through ds60sqlpy.stan_runner.
metrics:
  completed: 2026-11-24
  walkthroughs: 57
  tracks: 19
actuals:
  tokens: 86900
  tasks: 3
  commits: 0
plan_head_before: n/a (orchestrator commits; executor forbidden from git writes)
plan_head_after: n/a
---

# Phase 5 Plan 04: Python, Data, ML and Science Walkthroughs Summary

57 hash-bound authored walkthroughs across 19 tracks (one beginner, one intermediate and one advanced lesson each), with every expected_output string taken from a real execution of the reference in local Docker.

`commits: 0` is intentional: the orchestrator rules forbid executor git writes and the orchestrator commits. All deliverables are uncommitted untracked files.

## Lessons per track

| Track | Beginner | Intermediate | Advanced | Where executed |
| --- | --- | --- | --- | --- |
| statistics-ml | statistics-006 | statistics-013 | statistics-023 | python-core image |
| data-visualization | viz-001 | viz-004 | viz-008 | python-core image |
| nlp | nlp-007 | nlp-011 | nlp-018 | python-core image |
| polars | polars-001 | polars-007 | polars-014 | python-core image + data-engineering env |
| ml-engineering | mle-002 | mle-006 | mle-014 | python-core image + data-engineering env |
| dbt | dbt-002 | dbt-008 | dbt-013 | python-core image + data-engineering env |
| data-ml-engineering | dme-001 | dme-014 | dme-058 | python-core image |
| llm-applied | llm-applied-001 | llm-applied-007 | llm-applied-022 | python-core image |
| llm-evaluation | eval-002 | eval-006 | eval-014 | python-core image |
| llm-theory | llm-004 | llm-021 | llm-033 | python-core image |
| deep-learning-tensorflow | tf-007 | tf-013 | tf-025 | python-core image + tensorflow env |
| deep-learning-pytorch | torch-002 | torch-014 | torch-026 | python-core image + torch env |
| jax | jax-001 | jax-008 | jax-019 | python-core image + jax env |
| advanced-spark-modeling | asm-001 | asm-003 | asm-009 | pinned spark:4.0.1 base image, spark-submit local[2] |
| applied-science | science-001 | science-007 | science-017 | python-core image |
| bayesian-computing | bayes-001 | bayes-009 | bayes-017 (Stan) | python-core; bayesian env; CmdStan 2.40.0 build |
| custom-likelihood-pytorch | clp-002 | clp-007 | clp-014 | python-core image + torch env |
| python-web | pyweb-001 | pyweb-016 | pyweb-026 | python-core image + python-web env |
| apache-data-platforms | apache-001 | apache-012 | apache-042 | python-core image + data-platforms-python env |

No stage is uncovered in any track.

## How expected_output was verified

- **Execution environment.** All runs used `ds60sqlpy-worker-python-core:1.4.3` with `--network none`, the repo mounted read only, and `ds60-p5-` container names. Every container was removed after its run.
- **Track dependencies.** Packages were supplied as pip `--target` environments under `~/.cache/ds60sqlpy/p5/<name>`, installed from the locked arm64 requirements, rather than the real per-profile worker images. The environments were: torch, jax, tensorflow, data-engineering, data-platforms-python, bayesian and python-web.
- **Captures.** Each run was captured to `work/05-04/out/<lesson>.txt` and ends with `----- rc=0`.
- **Build check.** `work/05-04/build.py` refuses to write an expected string that is not a substring of the capture.
- **Spark.** `work/05-04/run_spark.sh` ran asm lessons in `spark:4.0.1-scala2.13-java17-python3-ubuntu`. Its digest is sha256:a552a335..., the same as DS60_SPARK_IMAGE. The command was `/opt/spark/bin/spark-submit --master local[2] --conf spark.ui.enabled=false`, mirroring worker_operations.py.
- **Stan.** `work/05-04/stan_build_run.sh` downloaded `cmdstan-2.40.0-linux-arm64.tar.gz`, verified sha256 c31e9f45..., and built it with g++ in a `ds60-p5-` container. It then compiled bayes-017/018/019 as `main.stan` via `make -C /opt/cmdstan` and ran `python -m ds60sqlpy.stan_runner`, as the stan-cpu profile does. All three returned rc=0. bayes-017 is captured in `out/bayes-017.txt`.
- **Not executed locally:** none.
- **Caveat.** These runs did not use the real per-profile worker images, so CI's reference corpus (`check_module_references.py`, which now counts 96 walkthrough expected outputs) remains the authoritative gate. The worker also filters Stan argument echo, but the chosen Stan strings ("Chain 1: 100 retained draws;" and the final completion line) are printed by stan_runner itself and survive that filter.

## Verification commands (real results)

| Command | Result |
| --- | --- |
| `check_walkthroughs.py --track <t>` for all 19 tracks | each: 3 walkthroughs; stages without one [] |
| `.venv/bin/python scripts/check_walkthroughs.py --check` | `OK: 96 authored walkthroughs across 32 tracks; nothing executed.` rc=0 |
| `.venv/bin/python scripts/check_module_references.py --list-only` (as written in plan) | rc=2: `error: the following arguments are required: --profiles, --report` |
| `work/05-04/listonly.sh` (same with `--profiles <ordinary profiles> --report work/05-04/refs.json`) | `Selected 1356 executable module implementations; 96 carry walkthrough expected output; nothing executed.` rc=0 |
| `.venv/bin/python -m pytest -n 0 --basetemp=work/test-tmp-05-04 -q tests/test_walkthroughs.py tests/test_module_reference_check.py tests/test_track_qualification.py` | `137 passed, 40 xfailed` (threshold test still strict xfail for 05-05) |
| Python scan for U+2013/U+2014 in all text fields of the 19 files | files 19, hits 0 |
| `perl -CSD -ne 'print if /[\x{2013}\x{2014}]/'` over the 19 files | no output |
| `git status --short -- 'courses/*/examples/*'` | empty (no reference file changed) |
| `docker ps -a --filter name=ds60-p5-` | only `ds60-p5-javabuild`, created by another agent; not mine and left untouched |

## Deviations from Plan

1. **Precondition.** The Phase 4 precondition was unmet because `04-VERIFICATION.md` is missing. I proceeded on the orchestrator's explicit instruction.
2. **[Rule 3] Plan's list-only command.** The plan's `check_module_references.py --list-only` exits 2 because `--profiles` and `--report` are required. I used `work/05-04/listonly.sh` with the ordinary profile set.
3. **[Rule 3] Dependency environments.** The track environments were pip `--target` installs on the python-core image, not the real per-profile worker images. Spark used the pinned base image. Stan used a locally built CmdStan of the same version and sha.
4. **Lesson substitution.** llm-004 was chosen instead of llm-002 to keep expected_output deterministic.
5. **Coordination with the concurrent agent.** The five concurrently edited tracks (python-web, applied-science, bayesian-computing, custom-likelihood-pytorch, apache-data-platforms) were authored last. The final `--check` passed without needing `--rebind`.
6. **Git and planning files.** No git writes were made, and STATE, ROADMAP and REQUIREMENTS were not edited, per the orchestrator rules.

## Known Stubs

None.

## Scratch and caches

- **Scratch:** `work/05-04/` holds cands.py, run.py, run_ref.sh, run_spark.sh, stan_build_run.sh, install_env.sh, build.py, listonly.sh, specs/*.py, out/*.txt and refs.json.
- **Caches:** about 7.5 GB under `~/.cache/ds60sqlpy/p5/`, including the CmdStan build at 1.1 GB. These can be deleted.
- **Temporary test dirs:** `work/test-tmp-05-04` was deleted. The other `work/test-tmp*` directories predate this plan and belong to other agents.

## Self-Check: PASSED

All 19 walkthroughs.json files exist and validate, and `--check` returns rc=0. There are no commit hashes to verify because the orchestrator commits.
