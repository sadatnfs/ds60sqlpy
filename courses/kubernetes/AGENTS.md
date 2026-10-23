# Kubernetes authoring rules

Read [root guidance](../../AGENTS.md), the [content contract](../../docs/content-authoring.md)
and [module integration](../../docs/implementation/ADDING_A_MODULE.md).
Preserve stable IDs and prerequisites. Keep guides, learner source, executable
references and explanations aligned. Each practice guide defines vocabulary,
explains syntax, gives at least two bounded worked examples, and includes six
inspectable exercises, progressive hints, retrieval and a lesson-specific
`Ask an AI tutor about this lesson` prompt. A reference run is not proof of
learner understanding.

Register complete bundles through `lessons.json`. Keep `verification_id` null
unless its trusted typed verifier is registered and tested. Content metadata
cannot install tools or execute arbitrary commands. Preserve learner state,
reviewed fixtures and private runtime credentials. Update durable authoring
sources where present, then regenerate and run focused content/runtime checks.
Do not use em dashes.

Explain the API object, desired state, reconciliation and observed status before
commands. Teach inspectable YAML and failure diagnosis, including readiness,
configuration, ownership and cleanup. Never use a learner's ambient kubeconfig
or current context to select a target.

The reviewed adapter operates only on an explicitly prepared, owned disposable
cluster/namespace and its allowed manifests. Ordinary reading does not create
resources. Host-dependent controller, storage and network behavior must be
labeled and separately qualified. Preserve exact identity/ownership receipts,
UID-aware deletion, bounded readiness and cleanup after failure. Do not put
cluster credentials or engine access in source or portable learner exports.
