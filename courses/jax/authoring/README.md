# JAX authoring ownership

`foundation.py`, `composition.py`, `scientific.py` and `advanced.py` contain original unit specifications. `model.py` defines the teaching-unit contract; `build.py` publishes the route and bundles. Use the tested JAX/JAXLIB 0.12.0.1 API contract with Python 3.12 or newer. Package/image qualification is owned by the `jax-cpu` runtime and does not happen while generating content.

Run `python courses/jax/authoring/build.py` to refresh this subject only, or add `--check` to detect drift. Shared readers remain owned by the repository builders. This generator does not execute examples, install dependencies, access the network or modify other subjects.

Every executable reference is a complete `main.py`-compatible program with a main guard, independent assertions and declared precision. The guides show the first two explained cases with their common setup; the six practice cases in the reference remain separate from the answer-free learner scaffold. Reading-only optional systems chapters use written traces and separate explained answers.

Use `tests/test_jax_lessons.py` for static, generation and mathematics checks. Actual JAX execution is opt-in in the prepared JAX environment and must also be qualified in the packaged worker. Device/kernel correctness, profiling, distributed operation and learner-state persistence are separate evidence.
