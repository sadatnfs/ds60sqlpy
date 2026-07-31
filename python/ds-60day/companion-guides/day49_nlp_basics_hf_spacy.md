# Day 49 — NLP Basics with Hugging Face and spaCy

**Lesson ID:** `python-49` · **Level:** advanced · **Dependencies:** `nlp` · **Network:** optional model download

This is a bounded survey of tokenization, pretrained pipelines, and rule-based
text processing. It does not confer mastery of language-model training or make
pretrained predictions reliable for a new domain.

## Learning objectives

By the end of the lesson, you can:

- explain tokens, subword tokenization, embeddings, logits, and entity spans;
- run a cached Hugging Face pipeline and inspect its output contract;
- compare a Transformers tokenizer with spaCy tokenization;
- use a local spaCy fallback without a downloaded language model; and
- identify model-card, bias, privacy, and domain-shift questions.

## Prerequisites

- Complete `python-48` (transfer learning).
- Understand train/inference differences and optional cached model assets.
- Install the `nlp` dependency group while connected.

## Network and offline contract

The notebook's first `pipeline("sentiment-analysis")` call may download a
default model and tokenizer. `en_core_web_sm` is also a separate spaCy model
download. Cache intentional assets during connected setup; do not assume they
exist on another machine.

Offline fallbacks:

```python
import spacy

nlp = spacy.blank("en")
doc = nlp("Natural language processing is fun.")
print([token.text for token in doc])
```

This blank pipeline tokenizes locally but has no trained part-of-speech tagger
or named-entity recognizer. A whitespace or regex baseline is also useful for
understanding what the pretrained tools add.

## Vocabulary and mental models

| Term | Definition |
|---|---|
| Token | Unit produced by a tokenizer; not always a word |
| Subword | Reusable word fragment used to handle vocabulary coverage |
| Token ID | Integer lookup key in a model vocabulary |
| Embedding | Dense numeric representation learned for an item or context |
| Pipeline | Packaged preprocessing, model inference, and postprocessing |
| Named entity | Span labeled as a type such as organization or location |
| Zero-shot classification | Scoring candidate labels without task-specific supervised training |
| Model card | Documentation of intended use, data, limitations, and evaluation |

Different tokenizers solve different problems. spaCy typically exposes
linguistic document objects; Transformers tokenizers produce model-specific
subword IDs and masks.

## Worked example: make the model choice explicit

```python
from transformers import pipeline

# This identifier should already be cached for an offline run.
sentiment = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)
for text in ["I love this course!", "This is terrible..."]:
    print(text, sentiment(text))
```

Record the exact model identifier and package version. A confidence-like score
is not automatically calibrated probability, and sentiment labels may fail on
sarcasm, dialect, negation, or domain-specific language.

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## How to run this lesson

1. Open the Day 49 learner notebook from this guide's **Next
   step** section in VS Code or JupyterLab.
2. Select the `Python (ds60sqlpy)` kernel. Start at the top and use
   **Run All** only after making the written predictions; every added
   worked example is bounded and offline after bootstrap.
3. Keep experiments in new scratch cells. Do not edit the official
   solution while attempting the numbered practice.
4. Restart the kernel and run from the first cell before calling the
   lesson complete. A clean run catches hidden state and stale
   variables.

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m jupyter lab
```

macOS/Linux:

```bash
.venv/bin/python -m jupyter lab
```

If the Windows environment uses the documented conda-prefix fallback,
use `.\.venv\python.exe` in place of
`.\.venv\Scripts\python.exe`.

## Concept deep dive — tokenization contracts, cached NLP models, and sensitive-text evaluation

### The mental model

Natural-language processing begins with a tokenizer contract. A token is
a model-specific unit, not necessarily a word; subword models split rare
words into reusable pieces and map them to integer IDs. A pipeline then
combines preprocessing, model logits, and postprocessing labels.

Different tokenizers produce different boundaries and offsets. Model
output depends on truncation, maximum length, label mapping, model card,
language/domain, and version. Raw text may contain personal or secret
information, so examples, logs, caches, and evaluation artifacts need a
privacy boundary.

### Worked examples and syntax anatomy

- **`spacy.blank('en')`:** creates an offline tokenizer without a downloaded statistical pipeline.
- **`pipeline(task, model=..., local_files_only=...)`:** bundles a specific cached Transformer tokenizer/model and postprocessing; model identity must be explicit.
- **token offsets and truncation:** connect tokens back to original text and define what content the model actually saw.

Read an API call from the inside out: identify the data entering the
operation, the state learned (if any), the value returned, and the
evidence that would make the result trustworthy. A method returning
without an exception proves only that the syntax and immediate runtime
path worked.

### Focused example A — inspect an offline spaCy token boundary

Before running the example, predict the shape, type, or direction of the
result. Write the prediction down so that a surprise becomes evidence
rather than something to overlook.

```python
import spacy

nlp = spacy.blank("en")
doc = nlp("Tokenization isn't identical to splitting on spaces.")
tokens = [(token.text, token.idx) for token in doc]
print(tokens)
assert "".join(token.text_with_ws for token in doc) == doc.text
```

**Expected observation:** Punctuation and the contraction receive tokenizer-specific boundaries while offsets reconstruct the original text.

**Assumption to name:** The blank English tokenizer supplies lexical boundaries only; it has no trained part-of-speech or entity component.

### Focused example B — make vocabulary and unknown-token behavior visible

This second example changes one important condition. Compare it with
Example A instead of reading it as unrelated syntax.

```python
vocabulary = {"[UNK]": 0, "data": 1, "science": 2, "helps": 3}
text = "data science helps teams"
pieces = text.lower().split()
token_ids = [vocabulary.get(piece, vocabulary["[UNK]"]) for piece in pieces]
print({"pieces": pieces, "token_ids": token_ids})
assert token_ids[-1] == vocabulary["[UNK]"]
```

**Expected observation:** The unseen word maps to an explicit unknown ID; a real subword tokenizer may split it instead.

**Assumption to name:** This tiny whitespace vocabulary demonstrates the contract and is not a substitute for a trained tokenizer.

### From first attempt to independent use

| Stage | What to do | Evidence to keep |
|---|---|---|
| Recall | Define tokenization contracts, cached NLP models, and sensitive-text evaluation in your own words and identify its input and output. | A definition that does not rely on the library name. |
| Predict | Predict the examples before execution, including shape and direction. | A written prediction and an explanation of any mismatch. |
| Implement | Recreate one example with a changed but valid input. | Code plus an assertion for the central invariant. |
| Debug | Trigger the named mistake or edge case intentionally. | The observed symptom and the smallest diagnostic that isolates it. |
| Transfer | Apply the idea to a different local dataset or decision. | A stated assumption, metric, and reason the method is suitable. |

### Common mistake and debugging path

**Mistake:** Calling an unpinned default pipeline that downloads a model, then interpreting its label and score without reading the model contract.

**Debug it deliberately:** Record model/tokenizer IDs and revisions, cache status, token IDs/offsets, truncation length, label mapping, and evaluation slices.

**Stop condition:** Do not send sensitive learner text to a remote model or persist raw text/logits without explicit purpose, access, and retention rules.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Learner exercises and progressive hints

1. Try a zero-shot-classification pipeline with your own candidate labels.

**Verify:** Practice 1 — tokenization contracts, cached NLP models, and sensitive-text evaluation — when cached model artifacts exist, print model revision, candidate labels, input text, ordered labels, and scores whose sum is approximately 1; otherwise print an explicit offline-skip result without downloading.

2. Compare tokenization from spaCy with a Hugging Face tokenizer.

**Verify:** Practice 2 — tokenization contracts, cached NLP models, and sensitive-text evaluation — for one fixed text, print spaCy token text/start/end and Hugging Face token IDs/tokens/offsets; reconstruct covered substrings, mark special/unknown/truncated tokens, and record exact tokenizer model/revision or local fallback.

### Progressive hints

1. This is an optional connected/cached path. Keep the text and label list small,
   record the chosen model ID, and test at least one ambiguous sentence.
2. Print token text for spaCy; for Transformers, inspect `tokenize`, encoded IDs,
   and decoded output. Use contractions and punctuation to expose differences.

The reference solution extends the topic with a 20-step DistilBERT smoke
fine-tune and a spaCy matcher. That path downloads dataset/model assets unless
cached and is intentionally not the default offline exercise.

### Additional mastery practice

Treat tokenization, model identity, cache state, evaluation boundaries, and sensitive text handling as first-class NLP pipeline metadata.

Predict or plan before you run code. Use the hint only after an honest
attempt, and record the evidence that would prove your result correct.

3. **Truncation debugging:** Create a text longer than the model limit and inspect token count, special tokens, truncation, attention mask, and which part of the document is lost.
   **Progressive hint:** Request truncation and max_length explicitly. The tokenizer can report overflowing tokens or support sliding windows.

**Verify:** Truncation debugging — print original character length, token count before/after truncation, special tokens, attention mask, offsets, and lost suffix; assert all retained offsets reconstruct exact source substrings.

4. **Model-provenance contract:** Design metadata that proves which Hugging Face model/tokenizer and spaCy pipeline produced an output, including revisions and offline cache state.
   **Progressive hint:** Record repository ID, immutable revision/commit when available, library versions, tokenizer settings, and local-files-only mode.

**Verify:** Model-provenance contract — write and validate metadata containing model/tokenizer IDs and revisions, spaCy pipeline/version, local artifact hashes, offline/cache status, and preprocessing limits; reject a revision/hash mismatch.

5. **Evaluation leakage:** Find and repair leakage when near-duplicate documents or excerpts from one source appear in both train and validation.
   **Progressive hint:** Group by source/document/entity and use normalized hashes or similarity checks before splitting.

**Verify:** Evaluation leakage — group near-duplicates/source excerpts before splitting, print group-overlap count before/after repair, assert repaired overlap is zero, and compare the leaked versus grouped validation metric.

6. **Sensitive-text boundary:** Design a local text-classification workflow that minimizes PII in logs, cached datasets, examples, and error analysis.
   **Progressive hint:** Use synthetic fixtures, stable opaque IDs, redacted excerpts, bounded retention, and counts rather than raw matched values.

**Verify:** Sensitive-text boundary — run email/phone/name-like fixtures through logging, cache, example, and error paths; assert raw sentinel strings are absent from captured logs/artifacts while redacted IDs still support debugging.

Before opening the reference solution, explain the relevant assumption,
failure mode, and validation check for every answer.

## Self-check

- Why can one word become several subword tokens?
- What capabilities are absent from `spacy.blank("en")`?
- Why is a zero-shot label score not proof that the label is correct?
- What text must never be sent to an external model service without approval?

Expected behavior: cached pipelines run locally after bootstrap. If assets are
absent offline, the lesson should use the disclosed local tokenizer fallback
rather than silently attempting network access.

## Pitfalls, diagnostics, and tradeoffs

| Symptom | Likely cause | Response |
|---|---|---|
| Hugging Face connection error | Model/tokenizer is not cached | Connect intentionally to cache, or use local fallback |
| spaCy `OSError` for model | Language model package is absent | Use `spacy.blank("en")` or install/cache while connected |
| Laptop fine-tuning is too slow | Dataset/sequence/model too large | Use the documented bounded smoke subset and max steps |
| High score on harmful output | Domain shift or model bias | Build domain evaluation and human review |
| Raw sensitive text appears in logs | Unsafe observability | Minimize/redact data and define retention |

Pretrained models reduce startup cost but bring inherited data, licensing,
fairness, and version risks. Rule-based systems are narrower and brittle but
often easier to audit.

## Next step

- Work in the [Day 49 learner notebook](../notebooks/day49_nlp_basics_hf_spacy.ipynb).
- Then consult the
  [Day 49 solution](../solutions/day49_nlp_basics_hf_spacy/day49_solutions.md).
- Continue to [Day 50 — Time-Series Modeling](day50_time_series_modeling.md).

## Ask Codex about this lesson

The lesson is complete without an AI assistant. If you want optional
coaching, copy this prompt into Codex while the repository root is open:

```text
Tutor me through `python-49` — Day 49 — NLP Basics with Hugging Face and spaCy.

Follow the repository tutoring skill `guide-ds60sqlpy-learning`.
Emphasize tokenization contracts, cached NLP models, and sensitive-text evaluation. Use exactly these maintained learner materials:
- guide: `python/ds-60day/companion-guides/day49_nlp_basics_hf_spacy.md`
- learner artifact: `python/ds-60day/notebooks/day49_nlp_basics_hf_spacy.ipynb`

Treat me as a beginner except for these direct catalog prerequisites:
`python-48`. Do not assume knowledge beyond them or skip the
guide's declared setup boundary. Do not open or quote anything under
`solutions/` unless I explicitly ask after an honest attempt. First
explain one concept in plain language and show a tiny example. Then ask
me to predict what happens before I run code.
Give me one bounded task at a time and wait for my code, output, error,
or written reasoning. If I am stuck, reveal only one rung of a
progressive hint ladder at a time.

Run or inspect my learner artifact when safe, distinguish observed
evidence from inference, and help me diagnose tracebacks instead of
replacing my work. Finish with two or three retrieval questions and
one transfer task.

Done when I can explain the core mechanism without notes, complete one
fresh attempt without copied solution code, produce the guide's stated
verification evidence from a clean run, answer the retrieval questions,
and explain how the transfer task changes the assumptions. A cell that
merely ran is not evidence of mastery.
```
