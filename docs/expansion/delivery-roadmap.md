# Deliver the expansion in reviewable slices

Status: proposed sequencing. No fixed calendar or unsupported completion claim.

## Phase 0: design and teaching prototype

Deliver all five prerequisite-aware curricula, a complete pilot per subject, capstone briefs, shared lesson/runtime contracts, a validated planning graph, and the browser journey preview. Review conceptual coverage, prerequisite burden, safe practice boundaries, and exercise quality. This phase does not qualify heavy runtimes or publish planned lessons.

## Phase 1: one executable slice per subject

Implement the job controller and worker profile handshake first. Build the C++ compile/test slice, one TensorFlow gradient lesson, one NumPy/PyTorch LLM slice, paired Scala/PySpark fixture execution, and one owned-kind reconciliation lesson. These can proceed in parallel behind a common job contract. Kubernetes host provisioning and advanced credentials need their own review.

Each slice must include browser instructions, the real language/runtime, a failing learner attempt, useful feedback, cancellation, offline assets, save/resume, and cleanup. Measure resource envelopes before choosing defaults. Publish only those individual lessons whose receipts pass. Keep remaining plans visible as planned.

## Phase 2: beginner foundations

Author small batches by prerequisite order. Review each batch for the lesson contract, run all reference exercises, and observe a newcomer. Teach environment basics inside the relevant track. Retain short routes for people who already know the prerequisites. Introduce a progress-v2 adapter with reversible migration before changing the live progress format.

## Phase 3: intermediate projects

Add multi-file C++, TensorFlow data/evaluation workflows, tiny transformers, typed Scala and Spark shuffles, and Kubernetes rollout/configuration/operations. Integrate artifact viewing, structured diagnostics, bounded long jobs, and retrieval scheduling. Stage capstones test transfer and diagnosis rather than reproducing a notebook verbatim.

## Phase 4: advanced boundaries

Add concurrency/performance, training and model deployment tradeoffs, attention/decoding/evaluation experiments, Spark streaming/recovery, and dedicated-cluster Kubernetes administration. GPU, external clusters, cloud APIs, large models, and multi-node data systems are opt-in extensions with separate budgets and acceptance evidence. A default offline CPU route must remain coherent.

## Content promotion states

| State | Entry evidence | Learner visibility |
| --- | --- | --- |
| Planned | Valid design metadata and prerequisites | Clearly labelled roadmap and preview |
| Authored | Full guide, examples, exercises, solutions | Review workspace only |
| Reference verified | All examples and checks executed; known bad attempts rejected | Internal testing |
| Runtime verified | Actual profile, offline run, resource and platform receipts | Limited pilot, explicit compatibility |
| Teaching reviewed | Newcomer walkthrough and accessibility issues resolved | Eligible for publication |
| Published | Catalog entry, regenerated readers, release notes, migration proof | Normal course journey |

A track may contain published and planned lessons, but current catalogs must register only supported runnable or explicitly reading-only content. Never copy the design JSON directly into the strict extension loader.

## Parallel work boundaries

Subject authors own track plans, fixtures, guides, and reference solutions. Runtime owners own registered profiles and semantic verifiers. The platform owner owns jobs, persistence, security boundaries, and host launchers. The experience owner owns teaching components and accessibility. Changes to shared schemas require one owner and a compatibility review; do not let separate agents invent competing manifest formats.

Keep expensive integration jobs under a resource budget, while lightweight tests run in parallel. Use immutable fixture hashes and isolated namespaces/workspaces to prevent cross-test state. Report skipped platform rows as unverified. Content quantity is not an acceptance criterion by itself.

## Release gate for each batch

1. Validate the planning graph and published manifest without changing existing IDs.
2. Run reference solutions, intended failures, retrieval tasks, and offline fixture checks.
3. Test browser documents, actual execution, useful error feedback, save/resume, cancel, and container replacement.
4. Record the actual platform matrix, dependency/image hashes, resource peaks, and known gaps.
5. Regenerate catalog/readers and verify no drift; run the appropriate parallel test suite.
6. Review the complete learner path and publish a small batch with a clear outcome and compatibility statement.
