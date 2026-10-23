# C++ authoring rules

Read root AGENTS.md and docs/content-authoring.md. Own teaching content separately from profile execution. Keep stable design IDs, direct prerequisites, guide/source/solution parity and six inspectable exercises. Every guide explains new syntax, gives two bounded examples, progressive hints, retrieval and the exact lesson-specific Codex prompt. Never label a source review or process exit as verified understanding.

Use lessons.json schema1 for authored file metadata. Set verification_id to null until the trusted typed verifier is registered and independently tested. Do not add active catalog entries, install tools, download dependencies or create external resources while authoring. Preserve learner work and never reset another lesson's state.

C++ sources are staged as main.cpp; Scala sources as Main.scala with object Main; PySpark as main.py with guarded session setup. Kubernetes sources never choose a host cluster and must obey the owned-target operation's strict manifest allowlist. Fixtures are immutable reviewed inputs; do not let a learner select a harness path or replace the oracle. Keep credentials outside portable progress and exports. No em dashes.
