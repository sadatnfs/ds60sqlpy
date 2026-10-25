# Deep Kubernetes networking authoring

`python courses/kubernetes/authoring/networking/build.py` regenerates k8s-043 through k8s-066 from chapters.py, merges them into the original plan and authored manifest, and applies durable supplements to selected original guides. It preserves every original ID and verifier admission. The existing complete/build_all.py invokes this extension last so regeneration retains the new material.

The new lessons are reading/practice with explicit optional owned host labs. They do not add admitted cluster operations. Each has two worked examples, six progressive tasks, an answer-free worksheet, explanatory solutions and a synthetic case ledger. The networking fixture is maintained directly; check_fixtures.py performs only static/offline checks. An actual cluster acceptance receipt must come from a separately reviewed ownership-aware runtime workflow.

Use Bash inside WSL 2 on Windows. No native Windows credential or ACL workflow belongs here. Preserve no-ambient-context, named-capability and UID-aware cleanup boundaries. No em dashes or private infrastructure identifiers.

## Shared maintenance gates

Use [CONTRIBUTING](../../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
