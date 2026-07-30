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

## Learner exercises and progressive hints

1. Try a zero-shot-classification pipeline with your own candidate labels.
2. Compare tokenization from spaCy with a Hugging Face tokenizer.

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
4. **Model-provenance contract:** Design metadata that proves which Hugging Face model/tokenizer and spaCy pipeline produced an output, including revisions and offline cache state.
   **Progressive hint:** Record repository ID, immutable revision/commit when available, library versions, tokenizer settings, and local-files-only mode.
5. **Evaluation leakage:** Find and repair leakage when near-duplicate documents or excerpts from one source appear in both train and validation.
   **Progressive hint:** Group by source/document/entity and use normalized hashes or similarity checks before splitting.
6. **Sensitive-text boundary:** Design a local text-classification workflow that minimizes PII in logs, cached datasets, examples, and error analysis.
   **Progressive hint:** Use synthetic fixtures, stable opaque IDs, redacted excerpts, bounded retention, and counts rather than raw matched values.

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
