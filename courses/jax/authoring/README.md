# JAX authoring ownership

`foundation.py`, `composition.py`, `scientific.py` and `advanced.py` contain original unit specifications. `model.py` defines the teaching-unit contract; `build.py` publishes the route and bundles. Use the tested JAX/JAXLIB 0.12.0.1 API contract with Python 3.12 or newer. Package/image qualification is owned by the `jax-cpu` runtime and does not happen while generating content.

Each unit declares three to five distinct `key_terms`, each a lesson-specific term with a one-sentence definition. `build.py` validates them and renders them as the guide's Key terms section after Mechanism and purpose.

`reasoning.py` holds one `Reasoning` entry per unit for the explained reference: the solution `approach`, why it is `correctness`-preserving for this lesson's literal values, six `pitfalls` (one plausible wrong approach per exercise, in order) and a `verification` paragraph. `build.py` requires at least 35 words for approach, correctness and verification, six distinct pitfalls of at least 18 words, no en or em dashes, and at least 700 words in each rendered `jax-NNN_solutions.md`. Write each entry from that lesson's code and closed-form values; never invent runtime output.

`records.py` gives each reading-only unit one fenced `text` evidence-record sketch per worked example, rendered after the written trace so the guide shows the record a learner would keep. Unobserved stages stay marked missing, untested or pending. Executable units must not declare records.

Run `python courses/jax/authoring/build.py` to refresh this subject only, or add `--check` to detect drift. Shared readers remain owned by the repository builders. This generator does not execute examples, install dependencies, access the network or modify other subjects.

Every executable reference is a complete `main.py`-compatible program with a main guard, independent assertions and declared precision. The guides show the first two explained cases, each with only the setup definitions it uses; the six practice cases in the reference remain separate from the answer-free learner scaffold. Reading-only optional systems chapters use written traces and separate explained answers.

Use `tests/test_jax_lessons.py` for static, generation and mathematics checks. Actual JAX execution is opt-in in the prepared JAX environment and must also be qualified in the packaged worker. Device/kernel correctness, profiling, distributed operation and learner-state persistence are separate evidence.

## Canonical displayed code

Both generation and `--check` pass every Markdown artifact through the shared
guarded `canonical_markdown` hook before writing or comparing it. Use the prepared
Core authoring environment with pinned Ruff 0.16.0. Both Python formatting paths
use that interpreter through `sys.executable -m ruff`; no separate PATH executable
is assumed. The existing standalone Python formatting step remains in place. The shared formatter verifies Python syntax,
literal values and ordered comments while preserving prose, TeX and fence
identities. Missing prepared tools or a genuine formatting error fail explicitly;
the generator never installs a dependency or executes JAX examples.
