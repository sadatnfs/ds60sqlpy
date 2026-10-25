# Maintain the CUDA subject

The subject has three owned content fragments and one catalog assembler.

- [GPU foundations and C++ authoring](CPP_README.md) owns cuda-001 through cuda-064.
- [Python, frameworks and Spark authoring](python_README.md) owns cuda-065 through
  cuda-128, including the GPU Spark specialization.
- `build_catalog.py` combines complete fragments into the public track and
  admission manifests. It also attaches the separately reviewed optional C++
  GPU variants. Do not hand-edit the assembled manifests.

Regenerate the branches you changed, then assemble and validate:

```sh
python courses/cuda/authoring/cpp_content.py
python courses/cuda/authoring/python_generate.py
python courses/cuda/authoring/build_catalog.py
python scripts/check_modules.py
```

Use each branch's documented check/test mode. Run the shared formatter after
generation and ensure the durable templates/data and generated executables agree.
Then refresh the shared readers through their maintained builders. JSON catalog
checks compare structured content so formatter-only JSON layout is acceptable.

Default chapters use reading and meaningful CPU models. Optional profiles are
independently prepared, not dependencies of reading. Keep source/result histories
separate by variant. A CPU result must never be labeled a GPU benchmark. New
GPU verifiers require an actual trusted backend and device qualification before
receiving a non-null verifier ID. See `../AGENTS.md` and the root authoring skill.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
