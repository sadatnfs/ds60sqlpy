# Applied LLMs: subject assistants, retrieval and adaptation

> **Study in the unified classroom:** run `./classroom` from the repository
> root, then choose **Applied LLMs: subject assistants, retrieval and adaptation** on `/classroom`. Python, SQL and all other
> subjects share this home and workspace. Each subject has its own theme;
> prerequisites guide your choices and you set the pace. The
> [one-command setup](../../docs/one-command-classroom.md) prepares the Docker runtimes and preserves saved
> work. Native terminal/editor commands below are optional alternatives.


Build a subject assistant by specifying its task, sources, computation and evaluation before choosing a model update. This 24-lesson route complements the [language-model mechanisms course](../llm-theory/README.md), the [NLP foundations route](../nlp/README.md) and the [statistics book](../statistics-ml/README.md). It covers data-science extraction and analysis, grounded retrieval, actual tiny-model fine-tuning, low-rank adapters and a bounded assistant capstone.

The [authored manifest](lessons.json) is the source of truth for available lesson artifacts. The [route plan](track.json) preserves stable IDs and prerequisites. There are currently24 authored lesson bundles. Authored content and runtime acceptance are separate: consult the [execution checkpoint](../../docs/implementation/llm-applied-status.md) for the exact references that have run.

## Choose the right mechanism

Use prompts to specify behavior and examples, retrieval to supply current and attributable knowledge, deterministic tools for exact computation, and fine-tuning for a stable measured behavior gap supported by governed examples. These mechanisms can be combined. Fine-tuning does not replace citations, per-user access control or a statistical study design. A fluent explanation cannot validate a causal conclusion or invent a missing measurement.

The default code uses literal local fixtures and prepared NumPy or PyTorch CPU environments. It does not call a paid API, fetch a dataset, download a model or start a deployment. Lexical and extractive baselines are labelled as such. The tiny decoder and adapter chapters perform actual gradient updates but do not claim pretrained natural-language competence. The quantized-base chapter implements explicit uniform4-bit packing and adapter gradients; it does not claim NF4, paged optimizers or GPU-memory measurements.

## Study and execution

Each guide contains detailed intuition and design tradeoffs, definitions, syntax or reasoning anatomy, three worked examples, six concrete exercises, failure diagnosis, hints and a lesson-specific Codex prompt. Keep learner attempts separate from the executable and explanatory solutions. A successful reference run checks its assertions, not your independent understanding.

Use the Docker classroom Journeys page and the lesson's declared runtime. `python-core` uses the prepared NumPy/data environment. `llm-torch-cpu` uses the separately prepared PyTorch CPU worker. The optional pretrained recipe is reading mode until you deliberately prepare its separate assets and dependencies. Save work in a learner pad or your own ignored `.learning/` directory; source updates must not overwrite attempts.

For a prepared native environment, run your copied Python file with the selected interpreter. On PowerShell use `& $CoursePython path\to\practice.py`; on POSIX use `"$DS60_COURSE_PYTHON" path/to/practice.py`. These variables denote paths supplied by setup, not automatic installers. Read the profile notice before interpreting an import error as a lesson failure.

## Route

| Lesson | Topic | Profile | Content |
| --- | --- | --- | --- |
| [llm-applied-001](guides/llm-applied-001.md) | The subject assistant decision: prompts, retrieval or fine-tuning | python-core | Authored |
| [llm-applied-002](guides/llm-applied-002.md) | Data-science task contracts and structured extraction | python-core | Authored |
| [llm-applied-003](guides/llm-applied-003.md) | Prompt and context engineering with measurable boundaries | python-core | Authored |
| [llm-applied-004](guides/llm-applied-004.md) | Corpus provenance, versions and evaluation isolation | python-core | Authored |
| [llm-applied-005](guides/llm-applied-005.md) | Chunking, overlap, offsets and context budgets | python-core | Authored |
| [llm-applied-006](guides/llm-applied-006.md) | Lexical retrieval and BM25 from first principles | python-core | Authored |
| [llm-applied-007](guides/llm-applied-007.md) | Embedding retrieval, similarity and representation limits | python-core | Authored |
| [llm-applied-008](guides/llm-applied-008.md) | Hybrid retrieval, reciprocal-rank fusion and reranking | python-core | Authored |
| [llm-applied-009](guides/llm-applied-009.md) | Metadata filtering and access-controlled retrieval | python-core | Authored |
| [llm-applied-010](guides/llm-applied-010.md) | Query rewriting and bounded multi-hop retrieval | python-core | Authored |
| [llm-applied-011](guides/llm-applied-011.md) | Grounded claims, citations and evidence-based abstention | python-core | Authored |
| [llm-applied-012](guides/llm-applied-012.md) | Evaluating retrieval and answers with oracle controls | python-core | Authored |
| [llm-applied-013](guides/llm-applied-013.md) | Paired reliability studies and family-aware uncertainty | python-core | Authored |
| [llm-applied-014](guides/llm-applied-014.md) | Supervised fine-tuning data and answer-target masks | python-core | Authored |
| [llm-applied-015](guides/llm-applied-015.md) | Full supervised fine-tuning of a tiny causal decoder | llm-torch-cpu | Authored |
| [llm-applied-016](guides/llm-applied-016.md) | Low-rank adaptation: dimensions, gradients and a real update | llm-torch-cpu | Authored |
| [llm-applied-017](guides/llm-applied-017.md) | Quantized frozen bases, adapter gradients and QLoRA limits | llm-torch-cpu | Authored |
| [llm-applied-018](guides/llm-applied-018.md) | Compare full and adapter fine-tuning on frozen tasks | llm-torch-cpu | Authored |
| [llm-applied-019](guides/llm-applied-019.md) | Preference optimization, DPO and the RLHF distinction | llm-torch-cpu | Authored |
| [llm-applied-020](guides/llm-applied-020.md) | Fine-tuning embeddings and a small reranker | llm-torch-cpu | Authored |
| [llm-applied-021](guides/llm-applied-021.md) | Optional pretrained-model adaptation with pinned offline artifacts | reading | Authored |
| [llm-applied-022](guides/llm-applied-022.md) | Structured tools for extraction, aggregation and data-science work | python-core | Authored |
| [llm-applied-023](guides/llm-applied-023.md) | Domain assistant boundaries: freshness, injection, budgets and traces | python-core | Authored |
| [llm-applied-024](guides/llm-applied-024.md) | Capstone: a grounded and evaluated data-science subject assistant | python-core | Authored |

## Optional realistic pretrained experiment

Lesson021 links a complete [separate pretrained recipe](fixtures/pretrained/README.md), including direct dependency pins, a model revision and license note, an explicit connected acquisition script, local hash verification, template/mask checks, bounded full or LoRA SFT and local inference. No weights were downloaded and no pretrained training was executed during authoring. The recipe must not be counted as runtime-accepted until its own actual receipts exist.

## Evidence to retain

Keep corpus and chunk versions, access policy, prompt/template identity, tokenizer/model/adapter revisions, training and evaluation family manifests, exact tool inputs/outputs, citations, failures and execution receipts. Evaluate retrieval and answer quality separately, include oracle-context controls, preserve paired question identities and report independent family counts. A no-go with a precise missing-evidence list is a valid capstone result.
