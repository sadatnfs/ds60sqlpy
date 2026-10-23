# ML course implementation checkpoint

Updated **2026-10-22**. All durable authoring took place directly in the
original repository. This checkpoint separates authored lessons, host content
checks and actual worker qualification.

## Completed teaching slice

- [TensorFlow foundations](../../courses/deep-learning-tensorflow/README.md):
  `tf-001` through `tf-008`, with every direct entry prerequisite authored.
- [LLM foundations](../../courses/llm-theory/README.md): `llm-001` through
  `llm-009`, with every direct entry prerequisite authored. The attention pilot
  uses NumPy and does not require PyTorch or TensorFlow.
- Each of the 17 lessons has a guide, a learner artifact, an executable Python
  reference and a separate explanatory solution. The orientation worksheets
  `tf-001` and `llm-001` use reading mode, with written evidence and no job.
- Each guide provides definitions, syntax/reasoning anatomy, two focused worked
  examples, six distinct Expected/Verify exercises, diagnosis, three hints,
  retrieval, an evidence rubric and its exact Codex tutoring prompt.
- Both course directories include README, local AGENTS, and valid incremental
  `lessons.json` inventories. Publication in the active catalog is managed
  separately; metadata and a source file do not install a runtime.

## Fixed pilot verifier contracts

`tf-gradient-v1` calls `gradient_step(rate=0.1, initial_weight=0.0)` and compares
four numeric fields: `loss_before`, `gradient`, `weight_after`, `loss_after`.
The typed fixture also covers overshoot and the optimum. It lives at
[courses/deep-learning-tensorflow/fixtures/tf-gradient-v1.json](../../courses/deep-learning-tensorflow/fixtures/tf-gradient-v1.json).

`llm-causal-attention-v1` calls `attention(q,k,v,allowed)` using NumPy float64
arrays and an include-True boolean mask, returning output and weight matrices.
Its [typed fixture](../../courses/llm-theory/fixtures/llm-causal-attention-v1.json)
contains the beginner equal-score case, a future-value change, malformed inputs,
and four nonuniform cases. The nonuniform goldens are derived from explicit
scalar exp formulas for known scaled score rows, independently of the candidate
helper. They expose ignored queries/keys, missing square-root scaling, wrong
normalization axis and swapped query/key calculations. Prefixes and future-only
perturbations retain the causal boundary.

Both runnable worked implementations may already pass a fixed verifier. A
successful check is evidence about that function, not completion of all six
exercises or proof of language-model quality. Predictions, owned attempts and
fresh transfer explanations remain separate evidence.

## Completed host validation

Using an existing prepared Python/NumPy environment, without installing any
package:

- `tests/test_ml_module_lessons.py`: **34 passed, 1 skipped**. The single skip
  is the explicitly opt-in qualified TensorFlow execution test.
- All 15 standard-library/NumPy references execute their exercise checks. Their
  guide examples and Python learner files also execute from fresh namespaces.
- All 17 lessons pass the shared `audit_lesson_depth` and practice-count gates
  through an isolated in-memory catalog, without publishing new active IDs.
- All source Python parses, all local authored Markdown links resolve, and
  no em dashes occur in the owned course artifacts.
- Ruff check passes for both complete course directories and the focused test
  file. All Python and Markdown code fences are formatted consistently.
- Independent `fractions.Fraction` arithmetic verifies every TensorFlow pilot
  oracle, including large-step failure, fresh repeated updates, the broadcast
  gradient and the bias/held-out transfer.

TensorFlow was **not imported or executed on the host authoring interpreter**.
The runtime team separately qualifies actual worker execution and records it in
[the runtime documentation](../modules-runtime.md). Python parsing and Fraction
math do not establish framework, platform, memory or elapsed-time acceptance.
This content work installed no TensorFlow/PyTorch package, downloaded no model
or dataset and built no image.

## Reproduce the focused checks

From the repository root, using the prepared quality environment:

```text
python -m pytest tests/test_ml_module_lessons.py
python -m ruff check --no-cache courses/deep-learning-tensorflow courses/llm-theory tests/test_ml_module_lessons.py
```

Only in an already qualified TensorFlow environment, the optional reference
execution test can be selected explicitly. Windows PowerShell:

```powershell
$env:DS60_TEST_TENSORFLOW = "1"
& $CoursePython -m pytest tests/test_ml_module_lessons.py -k qualified_runtime
```

macOS/Linux:

```bash
DS60_TEST_TENSORFLOW=1 "$DS60_COURSE_PYTHON" -m pytest tests/test_ml_module_lessons.py -k qualified_runtime
```

The selected interpreter must already contain the required packages; these
commands perform no environment setup. The optional test checks both tape
semantics in `tf-007` and all six reference exercises plus typed calls in
`tf-008`. Preserve learner state and report unavailable qualification honestly.

## Remaining content and publication gates

The reviewed design still plans `tf-009` through `tf-036` and `llm-010` through
`llm-042`: 61 later lesson bodies are not implicitly implemented. Start next
with batches/optimizer steps and positions/tokenwise normalization. Keep the
optional TensorFlow comparison out of the required LLM capstone path.

Before any wider publication, confirm actual worker readiness on each claimed
platform, save/cancel/timeout/output behavior, learner-work preservation,
prerequisite navigation, and explicit solution reveal in the UI. Register only
completed teaching artifacts and retain the immutable historical practice
baseline. Do not create placeholder lessons merely to make an entire course
appear available.
