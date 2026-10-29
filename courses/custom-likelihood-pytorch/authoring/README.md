# Likelihood tutorial authoring

`units.json` defines the twenty stable teaching units; `chapters/` contains original prose and `programs/` contains complete independent CPU programs. `build.py` checks these inputs and emits the course guides, examples, metadata and README deterministically using the standard library. `--check` compares exact UTF-8 bytes. It does not run PyTorch or claim native acceptance.

Every program exposes `run_cases()` with finite JSON evidence and a main block that prints it. Each guide embeds the exact program bytes after its mathematical and worked-case explanation. Change the durable program and chapter together, regenerate, and run tests/test_custom_likelihood_pytorch.py. Numerical tests require the prepared Torch environment and are distinct from source checks. No model or dataset download is allowed during a lesson.

Root integrates the track into the shared directory, compiles TeX and regenerates shared HTML after all authors freeze. Source manifests are emitted only after all twenty complete chapters/programs exist.
