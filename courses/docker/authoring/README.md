# Docker authoring

`python courses/docker/authoring/build.py` regenerates all 42 lesson bundles and metadata from `chapters.py`. It writes explicit UTF-8/LF and performs no engine operations, network requests or installation. Edit durable specifications, regenerate, then run shared normalization and module/render checks.

`fixtures/compose-lab/` is maintained directly. Its standard-library app, Compose model, Dockerfile and README form the bounded optional host lab. Reading registration does not claim in-browser engine execution. The fixture inventory records expected observations, not invented qualification results.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.

## Prepared canonical Markdown generation

Run the existing builder inside the
[prepared contributor formatting environment](../../../docker/formatting/README.md).
Its locked parsers and adapters cover the actual shell, Dockerfile, YAML, JSON
and Python fences in this route, including shfmt 3.12.0, dockerfmt 0.5.4,
Prettier 3.6.2 and Ruff 0.16.0. These tools parse and format source text; the
generator still performs no Docker engine operation, network request or
installation.

Before its normal write, the owner passes each guide, worksheet and explanatory
solution Markdown through `canonical_markdown`. The shared adapter validates
generated-path ownership, syntax, literal values and idempotence. It reports
protected transcripts, templates and unsupported fragments explicitly. It does
not execute a command from a lesson. Missing prepared tools are errors, with no
silent unformatted fallback. JSON metadata and the directly authored Compose
project retain their existing owners.

The command remains `python courses/docker/authoring/build.py`; there is no
separate `--check` mode. Hash the generated artifacts, rerun the builder in the
same prepared environment and compare hashes, then follow the shared source
and content checks. Actual engine/lifecycle qualification remains a separate
owned host-lab operation. Never edit a generated guide or weaken a publication
assertion to conceal formatting drift.
