# Core module plan sources

This directory contains the five original module plans that still supply live
classroom route metadata. It is not an alternate application or a design
preview. Learners enter every subject through `/classroom`.

| Subject | Canonical plan | Authored admission |
| --- | --- | --- |
| Kubernetes | [kubernetes.json](plans/kubernetes.json) | [lessons.json](../../courses/kubernetes/lessons.json) |
| C++ | [cpp.json](plans/cpp.json) | [lessons.json](../../courses/cpp/lessons.json) |
| TensorFlow | [deep-learning-tensorflow.json](plans/deep-learning-tensorflow.json) | [lessons.json](../../courses/deep-learning-tensorflow/lessons.json) |
| LLM theory | [llm-theory.json](plans/llm-theory.json) | [lessons.json](../../courses/llm-theory/lessons.json) |
| Scala/Spark | [scala-spark.json](plans/scala-spark.json) | [lessons.json](../../courses/scala-spark/lessons.json) |

`src/ds60sqlpy/module_plans.py` loads these inputs with `load_core_plans`.
Preserve their stable IDs, stage sequence, prerequisites and pilot lesson ID.
`ModuleCatalog` combines them with authored admission and validates the full
cross-subject dependency graph. A plan row is not an execution capability or a
complete authored lesson. Runtime readiness is reported separately.

New additive subjects normally use `courses/<subject>/track.json` and
`lessons.json`. The statistics/ML tutorial has its dedicated manifest and
coverage contract. Do not move an existing subject or invent a second plan as
an incidental content edit.

Run from the prepared contributor environment at the repository root:

```sh
python scripts/check_modules.py --json
python scripts/course.py validate
```

Use the [extension playbook](../curriculum-extension-playbook.md) to choose a
registration route, the [module contract](../implementation/ADDING_A_MODULE.md)
for exact fields, and the [current architecture](../implementation/CHECKPOINT.md)
for runtime and state boundaries. Subject `AGENTS.md` and authoring READMEs
identify durable sources. After authoring changes, use `make generate` to
refresh shared readers and run the [publication gates](../validation.md).
