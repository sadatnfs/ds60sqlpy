# Python fixture authoring

This directory maintains the original synthetic tables in `python/fixtures/`.
It is not a generator for the historical notebooks or named professional units;
those are edited at their documented source paths.

From a prepared contributor environment at the repository root:

```bash
uv run --no-sync python python/authoring/build_teaching_fixtures.py --check
```

The check compares exact UTF-8 bytes with deterministic generator output. It
does not normalize CRLF before checking. Git attributes retain canonical LF for
CSV/JSON, and the loader checks the raw-byte digests in the manifest. A changed
line ending can therefore be a real data-identity mismatch even when a text
editor displays the same rows.

When intentionally revising these authored fixtures, run the generator without
`--check`, inspect all output/manifest changes and run
`tests/test_teaching_fixture_authoring.py` plus `tests/test_teaching_data.py`.
Keep fixture names, documented schemas, synthetic provenance and dependent
teaching examples aligned. Do not change data to conceal a failing assertion.
An additional dataset needs a deliberate manifest entry, fixed allowlisted
loader name, size/schema/digest checks and actual packaged-runtime evidence.

The ordinary classroom ships these bytes inside its image and needs no source
generation or external dataset download. Browser saved code/results and model
artifacts are separate learner state and never belong in this generator's output.
