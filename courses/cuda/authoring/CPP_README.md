# CUDA foundation and C++ authoring

This branch owns **cuda-001 through cuda-064**. Each canonical lesson is reading
practice with a saved Markdown worksheet, two worked examples, six tasks and
separate explanatory answers. A complete standard-library Python reference
makes the stated CPU arithmetic or reasoning model reproducible on any ordinary
classroom machine. It is always labelled CPU evidence.

Durable sources:

- `cpp_units.json`: original prose, concrete questions/answers, CPU model and a
  representative CPU observation. Assertions, rather than floating-point string
  spelling, define acceptance.
- `cpp_gpu_programs.json`: eight complete standalone CUDA references and separate
  learner harnesses. These are optional GPU labs, not a CPU emulator.
- `cpp_content.py` and `cpp_gpu_sources.py`: deterministic generation.

From the repository root:

```sh
python courses/cuda/authoring/cpp_content.py
python courses/cuda/authoring/cpp_content.py --check --test-models
```

The generator writes only `courses/cuda/cpp/` generated teaching artifacts and
`cpp_manifest.json` plus `cpp_optional_gpu_variants.json` in this authoring
folder. It never modifies the full subject manifests, shared HTML, Docker
configuration or learner state. The integration owner merges its `track_lessons`
and `admissions` arrays with the Python/Spark fragment. GPU variants are a
separate keyed fragment and may be registered only with the reviewed profile.

When changing a CPU model, format its canonical code with the pinned Ruff
configuration, execute its assertions, refresh its illustrative output and
regenerate. When changing CUDA source, use the pinned clang-format configuration
at `docker/formatting/clang-format.yaml`, store the resulting full source back in
`cpp_gpu_programs.json`, then regenerate. Do not format only the generated file
and leave regeneration drift. The repository formatting entrypoint checks the
standalone `.cu` files using the CUDA adapter.

The optional references cover first launch, grid-stride mapping, rectangular
padded images, a two-stage reduction, atomic histogram, two-buffer stencil,
cross-stream events and graph replay. They use small deterministic input suites,
checked APIs and host comparisons. Source inspection and CPU tests do not prove
CUDA compilation or execution. Retain actual GPU qualification separately and
never fabricate an execution receipt on a CPU-only machine.
