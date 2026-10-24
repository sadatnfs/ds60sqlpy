# Five new learning journeys

> **Developer design archive:** this directory records the expansion design
> and planning contracts. The public learner entrypoint is now `/classroom`,
> combining Python, SQL, bridge and all module/book subjects. The old
> `/journey-preview` browser path is a compatibility alias to that classroom.
> Preview JSON, templates and the preview generator remain developer planning
> artifacts; they are not a second learner application or runtime proof.
> Read [the classroom guide](../classroom-experience.md) for the current experience.


Original design review:22October2026. This folder retains the five original
curriculum blueprints and their interactive design preview. Active authored
lessons now live under `courses/` and run through `/classroom`; additional
subjects use additive track manifests. The [implementation checkpoint](../implementation/CHECKPOINT.md)
records current content, runtime evidence and remaining work. The
[Docker classroom](../docker-classroom.md) is the learner entry point.

The design preview remains useful for reviewing the original sequencing. It
does not execute code or report current runtime readiness. Consult the actual
journey for authored lessons and the declared runtime profile for each pad.

## Start the review

1. Read [the teaching experience](learning-experience.md) and [the lesson contract](lesson-contract.md).
2. For historical design comparison, inspect the standalone generated `journey_preview.html` artifact. It records the original five-path pilot and browser reasoning checks. The public app's old `/journey-preview` path now opens the unified `/classroom` shell; use that shell for all current subjects and actual runtime readiness.
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

## Current additive paths and deeper specializations

The original five-plan design archive is only one part of the live library.
Current additive subjects use `courses/<subject>/track.json` and `lessons.json`.
The new [C](../../courses/c/README.md), [Go](../../courses/go/README.md),
[C#](../../courses/csharp/README.md), [Rust](../../courses/rust/README.md),
[Swift](../../courses/swift/README.md) and [Docker](../../courses/docker/README.md)
paths join the same classroom. The JavaScript path includes a dedicated
[24-lesson D3 sequence](../../courses/javascript-typescript/guides/js-043.md).
Kubernetes retains its original plan and adds a [24-lesson networking and
operations extension](../../courses/kubernetes/guides/k8s-043.md).

Inspect each subject's authoring README before editing generated bundles.
Browser D3, ordinary Linux compiler workers and manual Docker/advanced cluster
labs have different evidence contracts. Follow [validation](../validation.md)
and the [module integration guide](../implementation/ADDING_A_MODULE.md) rather
than inferring execution from a manifest's presence.
