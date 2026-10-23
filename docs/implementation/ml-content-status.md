# ML content completion and verification checkpoint

Updated 2026-10-22. This checkpoint records authored source and actual checks separately from runtime qualification and learner mastery.

## Authored inventory

- TensorFlow: **36 of36 reviewed IDs**, `tf-001` through `tf-036`.
- LLM mechanisms: **42 of42 reviewed IDs**, `llm-001` through `llm-042`.
- This pass completed the previously missing `tf-009` through `tf-036` and `llm-010` through `llm-042`,61 lesson bundles.
- Each guide includes a mechanism explanation, definitions, syntax or reasoning anatomy, two worked examples, six concrete exercises with Expected/Verify contracts, diagnosis, hints, retrieval and a copy-ready Codex prompt. Every code lesson has an answer-free learner worksheet, an executable reference with assertions, and a separate explanatory solution. Reading lessons have separate worksheets and explanations.
- Guide word counts across the complete inventory range from1360 to2757. Counts are structural evidence; the per-topic calculations, counterexamples and independent assertions carry the teaching evidence.
- The reviewed IDs, prerequisites and runtime profiles are preserved. Authored registration alone does not publish the active catalog or qualify a runtime.

## Actual checks in this pass

Command from the repository root, using the existing prepared Python environment:

```text
python -m pytest tests/test_ml_module_lessons.py -q --disable-warnings
```

Result: **58 passed,42 skipped**. Skips are explicit optional heavy-runtime tests:1 existing TensorFlow foundation test,25 newly completed TensorFlow reference tests,15 PyTorch reference tests and1 additional decoder/cache negative-control test. The latest focused run completed without warnings. Three additional regressions compile embedded child programs without importing heavy frameworks.

The complete78-entry inventory passed the shared lesson depth and practice checks inside the focused test suite. All authored Python files parsed. Existing behavior tests were preserved; new tests cover full planned-ID coverage, core reference execution, tool proposal failures, retrieval tie behavior, tokenwise normalization and optional decoder/cache boundaries.

All30 `python-core` executable reference `verify()` functions were also executed directly and passed:

`tf-002`, `tf-003`, `tf-004`, `tf-005`, `tf-006`, `tf-010`, `tf-034`, `tf-035`, `llm-002`, `llm-003`, `llm-004`, `llm-005`, `llm-006`, `llm-007`, `llm-008`, `llm-009`, `llm-010`, `llm-011`, `llm-012`, `llm-013`, `llm-014`, `llm-021`, `llm-025`, `llm-027`, `llm-033`, `llm-034`, `llm-036`, `llm-037`, `llm-038`, `llm-040`

## Explicitly unexecuted surfaces in this pass

The27 TensorFlow and15 PyTorch lesson references require the corresponding prepared CPU runtime. They were authored and structurally checked, but were not executed in the host environment during this authoring pass. No host package installation, model download, data download, database action or Docker mutation occurred here. Root integration owns the prepared-image execution receipts.

Heavy-runtime IDs awaiting that execution receipt:

`tf-007`, `tf-008`, `tf-009`, `tf-011`, `tf-012`, `tf-013`, `tf-014`, `tf-015`, `tf-016`, `tf-017`, `tf-018`, `tf-019`, `tf-020`, `tf-021`, `tf-022`, `tf-023`, `tf-024`, `tf-025`, `tf-026`, `tf-027`, `tf-028`, `tf-029`, `tf-030`, `tf-031`, `tf-032`, `tf-033`, `tf-036`, `llm-015`, `llm-016`, `llm-017`, `llm-018`, `llm-019`, `llm-020`, `llm-022`, `llm-023`, `llm-024`, `llm-026`, `llm-028`, `llm-031`, `llm-032`, `llm-035`, `llm-042`

Reading-only IDs require written reasoning rather than a fabricated execution receipt:

`tf-001`, `llm-001`, `llm-029`, `llm-030`, `llm-039`, `llm-041`

`tf-028`, `tf-032` and `llm-022` include same-interpreter fresh-process persistence checks with60-second subprocess bounds and owned TemporaryDirectory cleanup. Their source intentionally distinguishes prediction parity from next-update parity. `llm-024`, `llm-035` and `llm-042` compare full-prefix and incremental KV-cache outputs. The capstones permit a no-go decision and distinguish fixed saved answer records from actual model-generated outputs.

## Continue without losing authoring state

The portable original specifications and renderer are checked in under `courses/deep-learning-tensorflow/authoring/`. Run:

```text
python courses/deep-learning-tensorflow/authoring/build.py
```

The renderer preserves the earlier first8 TensorFlow and first9 LLM bundles and regenerates the61 completed bundles from topic-specific source. Edit the specifications when changing generated lesson text, then rerun the renderer and checks. It does not touch shared catalog generators, runtime adapters, learner state or the practice expansion registry.

Prepared runtime test switches:

```text
DS60_TEST_TENSORFLOW=1 python -m pytest tests/test_ml_module_lessons.py -q
DS60_TEST_TORCH=1 python -m pytest tests/test_ml_module_lessons.py -q
```

Those are POSIX environment-prefix forms. In PowerShell set `$env:DS60_TEST_TENSORFLOW = "1"` or `$env:DS60_TEST_TORCH = "1"` before invoking the selected interpreter, then remove the temporary environment setting afterward. Use only a runtime whose dependencies were already deliberately prepared.

## Remaining integration work

Run the full heavy reference suites in prepared containers, record failures and repairs, regenerate the shared dashboard/readers after root catalog integration, and inspect the actual browser lesson/solution flow. Current content completion must not be described as a live-runtime or production-quality acceptance result. Additional Python/SQL deepening remains a separate queued workstream owned by root; no such lesson was claimed complete by this ML pass.

## Fresh-process repair checkpoint

Root prepared-container execution reported25 of27 TensorFlow references passing and indentation failures in the embedded child programs of `tf-028` and `tf-032`. The authoring specifications and generated artifacts now use `textwrap.dedent` with a leading newline, compile the child source before launching it, and include child stderr in a failure. The same defect was proactively repaired in `llm-022`. Static child-source compilation regressions pass. Root will rerun the actual prepared-runtime cases; this paragraph does not claim the repaired subprocesses have executed.

## Prepared-runtime acceptance readback

Root integration subsequently executed all27 TensorFlow reference programs and all15 PyTorch reference programs successfully in the prepared Linux arm64 Docker images. Initial failures in TensorFlow028/032 and PyTorch022 were repaired and individually rerun. TensorFlow032 additionally retains the loaded SavedModel owner so its captured variables remain alive during serve. Receipts are the local implementation files `work/tensorflow-all-lessons-acceptance.jsonl`, `work/tensorflow-repaired-lessons-acceptance.jsonl`, `work/tensorflow-export-lifetime-acceptance.jsonl`, `work/torch-all-lessons-acceptance.jsonl` and `work/torch-repaired-lessons-acceptance.jsonl`. These establish bounded CPU reference execution on that image/architecture, not Windows-native, x86, GPU, production-quality or learner-mastery acceptance. Earlier unexecuted statements above describe the authoring pass before this integration run.
