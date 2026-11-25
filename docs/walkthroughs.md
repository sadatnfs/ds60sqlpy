# Authored Walkthroughs

An authored walkthrough explains a module lesson's reference program a few lines at a
time. The classroom shows it in the same step panel as the live trace, with the label
**Authored steps, not a live trace**.

## What it is and what it is not

- **Live traces** exist only for core Python and SQL lessons. Bridge lessons reuse the
  Python tracer. These traces come from actually running the learner's code.
- **Authored walkthroughs** cover every other module track (Go, Rust, Java, JavaScript,
  and so on). A person wrote the steps. Nothing is traced or executed when the learner
  opens one, and the panel never says otherwise.
- DAX keeps its hand-derived references. There is no universal automatic tracer.

An authored walkthrough is trustworthy for two reasons:

1. It is **hash-bound**. Each entry stores the SHA-256 of the reference file it explains,
   and every step stores the exact source excerpt it covers. If the reference changes,
   CI fails until the walkthrough is rebound or rewritten.
2. Its **expected output is checked**. The CI reference corpus runs the reference
   program and fails if any `expected_output` line does not appear in the real output.

## Where it lives

Each track has at most one file: `courses/<track>/walkthroughs.json`. Authors working on a
track edit only that track's file. No catalog, manifest or generated file needs to change.

## File format

```json
{
  "schema_version": 1,
  "track_id": "go",
  "evidence": "authored",
  "walkthroughs": [
    {
      "lesson_id": "go-001",
      "title": "How the reference program builds and checks its result",
      "anchor": "reference",
      "source_path": "courses/go/solutions/go-001_solution.go",
      "source_sha256": "<64 lowercase hex characters>",
      "expected_output": ["All lesson checks passed."],
      "steps": [
        {
          "lines": [1, 6],
          "excerpt": "<lines 1 to 6 of the source, joined with newlines>",
          "title": "Package and imports",
          "explanation": "What these lines do, in plain language.",
          "observe": "What the learner should notice."
        }
      ]
    }
  ]
}
```

### Top level

| Field | Rule |
| --- | --- |
| `schema_version` | Must be `1`. |
| `track_id` | Must equal the directory name. |
| `evidence` | Must be exactly `"authored"`. Anything else is rejected with "Walkthroughs must not claim runtime evidence." |
| `walkthroughs` | A list of entries. No other top-level keys are allowed. |

### Entry

| Field | Rule |
| --- | --- |
| `lesson_id` | A lesson in this track. One entry per lesson. |
| `title` | Nonempty, at most 200 characters. |
| `anchor` | Must be `"reference"`. |
| `source_path` | The executable reference: the tutorial lesson's `source_path`, or for a practice lesson its single solution file that is not Markdown. It must sit under `courses/<track>/`. |
| `source_sha256` | SHA-256 of the current bytes of `source_path`, 64 lowercase hex characters. |
| `expected_output` | 1 to 5 nonempty strings, at most 200 characters each. Each must appear in the reference run's output. |
| `steps` | 3 to 20 steps. |

No other entry keys are allowed. The lesson must use an ordinary runtime profile: reading,
k8s-kind, dax-offline, browser and GPU lessons cannot carry a walkthrough because the CI
reference corpus does not run them.

### Step

| Field | Rule |
| --- | --- |
| `lines` | `[start, end]` with `1 <= start <= end <=` the line count. Starts must not decrease from one step to the next. |
| `excerpt` | Exactly the source lines `start` through `end` joined with `\n`. Lines are split on `\n`, and a single trailing newline is dropped first. |
| `title` | Nonempty, at most 200 characters. |
| `explanation` | Nonempty, at most 1200 characters. |
| `observe` | Nonempty, at most 600 characters. |

Authored text (titles, explanations, observations and expected output) must not contain
em or en dashes. The loader does not check excerpts, which are copied from source, but
`scripts/check_no_dashes.py` rejects dashes in every tracked file, so sources and
excerpts stay free of them too.

One invalid entry makes the whole track's file fail to load, so no lesson in that track
offers a walkthrough until it is fixed. CI catches this before release.

## Reveal rule

A walkthrough explains the reference solution, so the server returns it only when the
request includes `reveal: true`. The classroom button reads "Walk through the reference
solution" on practice lessons and "Walk through the reference" on tutorials. Opening it
never changes the learner's draft.

## Coverage floor

Every track with authored walkthroughs needs at least one per stage: beginner,
intermediate and advanced. Prefer lessons whose reference shows the stage's key idea.

## Commands

```bash
# Validate every track's walkthroughs (this runs in CI). Nothing is executed.
uv run python scripts/check_walkthroughs.py --check

# Report one track: steps and expected output per lesson, and stages still missing one.
uv run python scripts/check_walkthroughs.py --track go

# After an edit that changed only a reference file's bytes, not the excerpted lines,
# refresh the stored hashes. Refuses and changes nothing if any excerpt no longer matches.
uv run python scripts/check_walkthroughs.py --track go --rebind

# See which reference cases carry walkthrough expected output, without running them.
uv run python scripts/check_module_references.py --profiles go \
  --report work/refs.json --list-only
```

If `--rebind` refuses, the steps no longer describe the code. Re-author the affected steps,
then run `--rebind` again.
