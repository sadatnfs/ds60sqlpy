# Five new learning journeys

Original design review:22October2026. This folder retains the five original
curriculum blueprints and their interactive design preview. Active authored
lessons now live under `courses/` and run through `/journeys`; additional
subjects use additive track manifests. The [implementation checkpoint](../implementation/CHECKPOINT.md)
records current content, runtime evidence and remaining work. The
[Docker classroom](../docker-classroom.md) is the learner entry point.

The design preview remains useful for reviewing the original sequencing. It
does not execute code or report current runtime readiness. Consult the actual
journey for authored lessons and the declared runtime profile for each pad.

## Start the review

1. Read [the teaching experience](learning-experience.md) and [the lesson contract](lesson-contract.md).
2. Open the app's `/journey-preview` page to explore the five paths and their pilot walkthroughs. The preview also works as a standalone HTML file. It performs browser reasoning checks, not compiler, cluster, or training execution.
3. Review the subject plans below, including their prerequisites, capstones, and pilot exercises.
4. Use [the architecture](architecture.md), [runtime and testing plan](runtime-and-testing.md), and [delivery roadmap](delivery-roadmap.md) to turn one vertical slice at a time into a supported course.

| Journey | Curriculum design | Machine-readable plan | Pilot | Solutions |
| --- | --- | --- | --- | --- |
| Kubernetes | [Track](tracks/kubernetes.md) | [Plan](plans/kubernetes.json) | [Pilot](samples/kubernetes-pilot.md) | [Solutions](samples/kubernetes-pilot-solutions.md) |
| C++ | [Track](tracks/cpp.md) | [Plan](plans/cpp.json) | [Pilot](samples/cpp-pilot.md) | [Solutions](samples/cpp-pilot-solutions.md) |
| Deep Learning with TensorFlow | [Track](tracks/deep-learning-tensorflow.md) | [Plan](plans/deep-learning-tensorflow.json) | [Pilot](samples/deep-learning-tensorflow-pilot.md) | [Solutions](samples/deep-learning-tensorflow-pilot-solutions.md) |
| LLM Theory in Python | [Track](tracks/llm-theory.md) | [Plan](plans/llm-theory.json) | [Pilot](samples/llm-theory-pilot.md) | [Solutions](samples/llm-theory-pilot-solutions.md) |
| Scala and Apache Spark | [Track](tracks/scala-spark.md) | [Plan](plans/scala-spark.json) | [Pilot](samples/scala-spark-pilot.md) | [Solutions](samples/scala-spark-pilot-solutions.md) |

## What makes a course ready

A topic list is insufficient. Every planned lesson specifies a learner outcome, concrete lab, verification method, prerequisites, and runtime. Publication additionally requires an authored guide, two worked examples, six different exercises, separate solutions, meaningful checks, learner review, and execution evidence for each supported environment. A complete plan is not a completed course.

The planning JSON is a design format, deliberately outside `curriculum/extensions/`. It cannot register runners or make planned lessons executable. IDs are stable proposals, checked against each other and the active catalog. The preview is generated from these files so its paths cannot silently diverge from the documents.

From the repository root, validate the plans and regenerate the preview:

```bash
python scripts/build_journey_preview.py
python scripts/build_journey_preview.py --check
```

Both commands use only the Python standard library and the repository source. The check also validates the dependency graph, pilot metadata, references, and runtime names. Use `make journey-preview` for the first command. See [the delivery roadmap](delivery-roadmap.md) for the publication gates.
