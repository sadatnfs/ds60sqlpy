# Python and data science

Study Python in the unified Docker classroom. From the repository root:

```bash
./classroom --starter
```

Choose **Python and data science** from **All learning paths**. The worker
supplies Python and the core data packages; host Python or Jupyter installation
is unnecessary. Follow [first-time setup](../../docs/one-command-classroom.md)
on macOS, Linux or Windows WSL 2.

## Learn at your pace

The Python track contains **102 learning units**: the original 60 numbered
lessons, four foundation checkpoints, thirteen professional modules, three
additional language-mechanics units, eight NumPy units, seven pandas units and
seven data-structure/algorithm units.
Historical day numbers are stable labels, not a schedule. The classroom's
prerequisite information helps you choose where to start or review.

The numbered sequence moves from expressions, values and control flow through
functions, collections, files, testing and command-line programs, then data
analysis, statistics, machine learning and selected engineering topics.
Foundation checkpoints after Days 1, 3, 8 and 10 slow the early ramp with
tracing, debugging, trustworthy records and an auditable first investigation.

The deeper [professional Python route](../professional/README.md) covers array
shapes and numerical boundaries, pandas grain and joins, algorithms and their
costs, packaging, concurrency, Arrow/DuckDB, service reliability, testing,
experiments, model delivery and restartable pipelines. More advanced framework
work has its own [PyTorch](../../courses/deep-learning-pytorch/README.md),
[TensorFlow](../../courses/deep-learning-tensorflow/README.md),
[NLP](../../courses/nlp/README.md) and [LLM](../../courses/llm-theory/README.md)
subjects in the same classroom.

## Study one lesson

1. Read the companion guide and prerequisite notes.
2. Select the learner artifact and predict the example's result.
3. Work in your own browser pad, run a small change and read the actual output.
4. Attempt the exercises, explain a failure and use progressive hints.
5. Compare a reference when ready and record what you can now explain.

Start with the [Day 1 guide](companion-guides/day01_setup_and_repl.md).
The source [notebook](notebooks/day01_setup_and_repl.ipynb) remains available
for an optional contributor/editor workflow; it is not an extra prerequisite
for the browser classroom. The [companion guide index](companion-guides/README.md)
explains the source layout.

## Saved work and returning

Wait for the pad's saved confirmation before leaving. Browser source, notes,
progress and results live in the current project's Docker learning volume.
They are separate from tracked notebooks and references. A successful example
run is evidence for that source, not automatic proof of independent mastery.

```bash
./classroom stop
./classroom resume
```

Use the same project name and engine. See [backup and transfer](../../docs/docker-classroom.md#5-export-learning-work-and-the-database)
before deleting volumes or moving machines. A host `.learning/` directory used
by contributor tools is separate and is not automatically merged with Docker.

## Optional environments and extensions

Read the lesson capability notice before running advanced examples. A package
being installed does not mean pretrained weights or sample data are cached.
Prepare declared dependencies while connected or use the lesson's documented
local fallback; see [offline use](../../docs/setup/offline.md).

After Python Day 15 and SQL Day 15, the [engineering bridge](../../bridge/README.md)
connects application boundaries, safe SQL, transactions, tests and pipelines.
For notebook/editor work or repository checks, follow
[contributor setup](../../CONTRIBUTING.md) and [validation](../../docs/validation.md).
Those checks distinguish structural correctness, executed references and
learner understanding.

An optional tutor can use the repository's learning skill: ask it to guide
`python-01`, review prerequisites and give hints before solutions. The course
works without an AI account. See [learning with a tutor](../../docs/learning-with-an-ai-tutor.md).
