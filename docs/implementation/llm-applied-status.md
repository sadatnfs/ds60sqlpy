# Applied LLM content and execution checkpoint

Updated2026-10-22. All24 reviewed lesson IDs, `llm-applied-001` through `llm-applied-024`, have complete authored bundles registered in `courses/llm-applied/lessons.json`. The course covers subject-assistant design, data-science extraction, prompt/context engineering, corpus provenance, chunking, lexical and embedding retrieval, hybrid ranking, ACLs, multi-hop retrieval, grounded answers, evaluation, SFT, LoRA, quantized frozen bases, DPO-style updates, retrieval-model training, optional pretrained adaptation, typed analysis tools and a bounded capstone.

## Teaching artifacts

Every guide has three worked examples, mechanism and design explanations, vocabulary, syntax/reasoning anatomy, six inspectable exercises, failure diagnosis, hints, retrieval questions and a lesson-specific Codex prompt. Code lessons have separate answer-free learner worksheets, executable references and explanatory solutions. Lesson021 is a reading worksheet with a separate optional pretrained recipe. Guide word counts range from1639 to2316 after removing repeated helper code from later worked blocks.

The original portable authoring sources are in `courses/llm-applied/authoring/`. Regenerate with:

```text
python courses/llm-applied/authoring/build.py
```

The authored corpus and vector fixtures are literal local data. The fixed embedding table, lexical ranker and extractive answerer are explicitly labelled baselines. The tiny decoder and adapter lessons perform actual gradient updates but do not claim pretrained natural-language capability. Lesson017 implements uniform signed4-bit packing and adapter gradients, explicitly distinguishing these from NF4, double quantization, paged optimizers and GPU memory evidence.

## Focused checks

Using the existing prepared course Python environment from the repository root:

```text
python -m pytest tests/test_llm_applied.py -q --disable-warnings
```

Latest result: **31 passed,6 skipped**. The six skips are the explicit host-side PyTorch execution tests. All24 lessons pass the shared depth and practice gates inside this suite. Every authored Python source and optional recipe script parses. The17 core reference functions were also executed directly and passed.

Independent tests exercise source offsets and overlap, an arithmetic BM25 oracle, embedding shape/norm failures, duplicate-resistant RRF, access-partitioned cache identity, bounded cyclic traversal, SFT target-mask truncation, restricted-answer non-disclosure, optional asset tamper detection, dataset family isolation and local-only pretrained loading. The optional acquisition entry point is separately identified and requires explicit network acknowledgement.

## Actual prepared-container execution

Root integration executed all23 runnable references successfully in prepared Linux arm64 Docker images with network disabled, unprivileged UID65534 and bounded resources:

- `llm-applied-001` through `llm-applied-014`, plus `llm-applied-022` through `llm-applied-024`:17 core references passed.
- `llm-applied-015` through `llm-applied-020`:6 actual PyTorch training/adaptation references passed.

The local implementation receipts are `work/applied-llm-core-acceptance.jsonl` and `work/applied-llm-torch-acceptance.jsonl`. Their per-lesson status rows were read back and all report `succeeded`. This is bounded reference execution on the prepared Linux arm64 images. It does not establish native Windows/macOS execution, GPU performance, pretrained adaptation quality, production readiness or learner mastery.

## Optional pretrained recipe remains unexecuted

Lesson021 links `courses/llm-applied/fixtures/pretrained/README.md`. The recipe includes direct package pins, an immutable SmolLM2-135M-Instruct revision, model-card license metadata, explicit connected acquisition, local file hashes, offline-only model loading, chat-template prefix checks, completion-mask checks, full/LoRA modes, a10-step CPU budget and a local inference probe. A separate optional Dockerfile requires a reviewed digest-pinned base image; its manual offline run bind-mounts learner-owned model and output directories instead of using an ephemeral browser pad.

Only model/package metadata was read during authoring. No pretrained weights or datasets were downloaded, no packages were installed, no optional image was built and no pretrained training or inference was executed. The model tree reports269,060,552 weight-file bytes. Memory figures in the recipe are arithmetic planning estimates, not measurements. Direct dependency pins are not presented as a complete transitive lock or a qualified environment. No pretrained success receipt exists in the repository.

## Remaining integration and workstream boundary

Root owns shared catalog/runtime registration, generated dashboard/readers and browser acceptance. The source bundles and focused checks are complete. The default capstone is an evaluated extractive subject-assistant baseline, while the optional pretrained proposal stage requires its own preparation and validation receipts. A causal or inferential statistical conclusion still requires valid design and deterministic analysis evidence.

Java authoring resumes separately at `java-013`; Java001..012 are already authored and passed root's prepared-image execution. This applied LLM completion does not claim the remaining Java or other queued language lessons are finished.
