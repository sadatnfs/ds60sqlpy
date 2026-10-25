# CUDA, web and image distribution checkpoint

> Historical record for Git checkpoint `a6e92bd`. The pending list below describes
> that snapshot. Live preview, publication workflow safeguards and later validation
> have since progressed; use the [maintained checkpoint](CHECKPOINT.md) and
> [current validation instructions](../validation.md) for continuing work.

This is an **in-progress checkpoint**, not a release qualification. Version
0.4.0 is being prepared. The owner requested this Git checkpoint while work
continues. Do not publish images based on this file.

## Implemented so far

- 128 CUDA/GPU/Python/ML/Spark chapters with portable reading and CPU models,
  selected optional NVIDIA variants, and matched framework/Spark examples.
- 60 integrated HTML/CSS/PHP lessons, an isolated native HTML browser preview,
  a PHP CLI worker and a separate small HTTP project fixture.
- Local-versus-Hub image selection, architecture-specific image tags,
  resume-preserving settings and a preview-first image publication script.
- Optional CUDA worker definitions with bounded operations, real readiness
  probes and conservative handling of interrupted/device-fault outcomes.
- New source suffixes, syntax rendering, PHP formatting support, contributor
  guidance and version updates.

## Observed checks

The first full parallel Python pass reported 2,853 passes, 326 explicit skips,
10 passing subtests and seven failures. Follow-up changes corrected stale
subject inventories, workflow runner expectations, image commands and Kubernetes
endpoint integration. Generated readers still need their final refresh and the
full suite must be rerun after the remaining implementation work.

Focused launcher tests passed. Portable CUDA models passed. All 26 PHP references
executed in the prepared Linux worker. Web checks covered 42 browser acceptance
groups and eight actual HTTP/state scenarios. Those observations do not qualify
every OS, Docker engine, GPU or future source revision.

The CUDA C++ image built. Actual compiler checks exposed and corrected two
initializer issues. Full CUDA compilation remains unqualified because the
compiler's device phase crashes under the available x86 emulation. No NVIDIA
device is available here; device probes fail closed. GPU execution, framework
GPU behavior and hardware performance are not claimed as tested.

## Continue from here

1. Finish opt-in live HTML/CSS and browser-JavaScript/D3 previews, including
   debounce, viewport controls, state-safe navigation and no automatic history
   writes. That UI is not implemented in this checkpoint.
2. Finish the manual publication workflow's two-phase build/qualification and
   artifact handoff before any push. The current draft still needs its required
   runtime-report argument and exact workflow-path CI gate corrected. It is
   manual only, defaults to no publication and has no supplied Hub credentials.
3. Format the complete maintained source, preserve canonical authoring parity,
   regenerate all shared readers and run content/link/type/lint checks.
4. Run final parallel tests and Docker/browser acceptance with disposable state,
   including resume, replacement and prebuilt-image mode.
5. Report hardware and platform gaps explicitly, review the full diff and make
   the final release commit. No test pass can prove the absence of every bug.

Use the repository's root guidance and each subject's authoring README. Keep
the main checkout, stable lesson IDs and existing learner data. Do not reset
Docker storage or remove learning volumes as an incidental repair step.
