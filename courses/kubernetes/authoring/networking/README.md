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

## Prepared canonical Markdown generation

Use the [prepared contributor formatting environment](../../../../docker/formatting/README.md),
including its locked Python parsers and the adapters for the actual YAML, JSON,
Python and shell fences in these chapters. PyYAML remains an explicit authoring
dependency. The shared guard uses Prettier 3.6.2, Ruff 0.16.0 and shfmt 3.12.0
where those languages are present. It formats text without executing a lesson,
contacting Kubernetes, selecting credentials or installing dependencies.

The owner passes completed Markdown through `canonical_markdown` before its
normal write. The shared adapter enforces generated-path ownership, syntax,
literal preservation and idempotence. Protected transcripts, placeholders and
unsupported languages, including PowerShell, keep explicit diagnostics. Missing
prepared tools are errors; there is no silent raw-output fallback. Standalone
manifest/check programs, synthetic ledgers, admission and runtime authority
retain their existing owners.

Normal commands and batch order are unchanged, and these builders have no
separate `--check` mode. Hash their outputs, rerun the same builder in the same
prepared environment and compare hashes, then run the existing content and
publication tests. Keep actual cluster/lifecycle evidence separate. Shared
readers remain a later root-owned step.

The networking builder's common Markdown writer covers both new lesson bundles
and its final depth-supplement updates to original guides. The original 42
identities and verifier admission remain unchanged. Do not manually format a
derived guide or change a test assertion to bypass an owner regeneration error.
