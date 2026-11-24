---
phase: "01"
slug: "qualify-1-4-4-guide-python-sql-walkthroughs"
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-11-23"
---

# Phase 01: Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 in the prepared `.venv`, plus the Node classroom UI harness |
| **Config file** | `pyproject.toml`, `tests/conftest.py` |
| **Quick run command** | `node scripts/check_classroom_ui.mjs` |
| **Focused backend command** | `env -u DS60_TEST_DATABASE_URL -u DS60_SQL_EXPANSION_TEST_URL -u DS60_DATABASE_URL .venv/bin/python -m pytest -n 0 tests/test_learning_lab.py tests/test_execution.py -q` |
| **Full suite command** | `uv run --no-sync python -m pytest -n 4 --dist loadgroup` |
| **Estimated runtime** | Not measured; the focused UI harness passed 94 checks during research |

The focused backend command removes database URL overrides so it cannot
accidentally target a personal database. PostgreSQL integration tests may run
only with the documented disposable CI database service and its test
environment. Use `--dist loadgroup` for parallel shared-database tests or
`-n 0` for serial tests.

The UI harness is a fast regression gate, not evidence for guide, tour, or
walkthrough flows until their assertions are added. Browser acceptance must use
a disposable classroom because the checker writes pads and progress. Do not
install or update browser-lock packages for this phase without resolving the
researcher's supply-chain warning first.

---

## Sampling Rate

- **After every task commit:** Run `node scripts/check_classroom_ui.mjs` and the focused backend command when backend behavior changes.
- **After every plan wave:** Run the disposable PostgreSQL integration command for SQL behavior changes and the disposable desktop-browser command for guide, tour, or walkthrough changes.
- **Before `/gsd-verify-work`:** Run the full suite, disposable PostgreSQL integration, and desktop-browser acceptance; record unavailable gates rather than treating them as passed.
- **Max feedback latency:** Not measured; keep UI and focused backend checks as the per-task loop, with database and browser checks at the wave gate.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01 | 01 | 0 | GUIDE-01 | n/a | Manual links and help content do not trigger runtime actions | browser + UI regression | `node scripts/check_classroom_ui.mjs`; disposable-browser command below | ✅ harness; extend guide and entry-point assertions in Wave 0 | ⬜ pending |
| 01-02 | 01 | 0 | GUIDE-02 | n/a | Tour lifecycle preserves selection and draft and never executes code | browser | Disposable-browser command below | ✅ checker; extend tour lifecycle and route-neutrality assertions in Wave 0 | ⬜ pending |
| 01-03 | 01 | 0 | WALK-01 | n/a | Trace is bounded and source-linked; error/limit outcomes are explicit | unit + browser | `.venv/bin/python -m pytest -n 0 tests/test_execution.py -q`; disposable-browser command below | ✅ backend tests; add trace-contract assertions in Wave 0 | ⬜ pending |
| 01-04 | 01 | 0 | WALK-02 | n/a | Unsupported SQL is rejected before database preparation or execution; tested supported queries do not mutate learner data | unit + PostgreSQL integration | `uv run --no-sync python -m pytest -n 4 --dist loadgroup tests/test_execution.py tests/test_sql_expansion_live.py -q` | ✅ test files; add parser/offset and before/after state assertions in Wave 0 | ⬜ pending |
| 01-05 | 01 | 0 | WALK-04 | n/a | Solution inspection is distinct from Run and preserves the learner's source | backend + browser | `env -u DS60_TEST_DATABASE_URL -u DS60_SQL_EXPANSION_TEST_URL -u DS60_DATABASE_URL .venv/bin/python -m pytest -n 0 tests/test_learning_lab.py tests/test_execution.py -q`; disposable-browser command below | ✅ run-preservation tests; add walkthrough-specific draft/history assertions in Wave 0 | ⬜ pending |

Disposable-browser command:

```sh
work/browser-env/bin/python scripts/check_classroom_browser.py --url "$CLASSROOM_URL" --confirm-disposable --report work/phase1-browser-receipts.json
```

The PostgreSQL integration command above is for the existing CI job with its
disposable PostgreSQL service only. No local PostgreSQL service or database URL
may be substituted.

---

## Wave 0 Requirements

- [ ] Extend `tests/test_execution.py` to assert Python trace source/event mapping, bounded state/output, and explicit limit/error behavior.
- [ ] Add SQL planner and offset assertions to the existing focused tests; verify supported SQL against PostgreSQL 17 and compare database state before and after unsupported input.
- [ ] Extend `scripts/check_classroom_browser.py` to cover both guide entry points, tour start/dismiss/restart without route or draft changes, visible Python/SQL walkthrough distinction, and solution inspection without replacing a draft.
- [ ] Run browser acceptance only against a disposable classroom; do not install browser packages until the browser-lock SUS warning is resolved.
- [ ] Keep PostgreSQL tests on the existing disposable CI service; do not use local or personal databases.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Confirm the guide and walkthrough controls are understandable at the supported desktop viewport | GUIDE-01, GUIDE-02, WALK-04 | Automated interaction checks cannot establish whether the instructions are clear to a first-time learner | Open the disposable classroom in a desktop browser; follow initialization and lesson-switching instructions, then start, dismiss, and restart the tour and inspect both solution walkthroughs while checking that the draft and selected lesson remain unchanged. |

Scheduled in Plan 05, Task 3. Record the first-time learner outcome, observed confusion, selected lesson before/after, and draft-preservation result in `.planning/phases/01-qualify-1-4-4-guide-python-sql-walkthroughs/01-VERIFICATION.md`. Use a disposable classroom and do not record its URL, secrets, or learner source text. If the desktop environment is unavailable, record the check as unavailable rather than passed.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 300s for quick checks
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
