# Day 49 — Solutions: NLP Basics with Hugging Face and spaCy

We build a sentiment classifier with Transformers, handle class imbalance with weights, and create a spaCy rule‑based matcher. Detailed explanations follow each block.

Contents
- Exercise 1: Build a HF pipeline for sentiment on your dataset
- Exercise 2: Add class weights for class imbalance
- Exercise 3: Use spaCy matcher to extract domain patterns

---

Exercise 1 — Fine‑tune DistilBERT for sentiment
```python
# 1) Imports
from datasets import load_dataset
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer)
import numpy as np
import evaluate
from pathlib import Path

# 2) Data: use IMDB for demo
ds = load_dataset('imdb')

# 3) Tokenizer and encoding
tok = AutoTokenizer.from_pretrained('distilbert-base-uncased')

def encode(batch):
    return tok(batch['text'], truncation=True, padding='max_length', max_length=128)

ds_enc = ds.map(encode, batched=True)

ds_enc = ds_enc.rename_column('label', 'labels')
ds_enc.set_format(type='torch', columns=['input_ids','attention_mask','labels'])

# 4) Model
model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)

# 5) Metrics
accuracy = evaluate.load('accuracy')

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {'accuracy': accuracy.compute(predictions=preds, references=labels)['accuracy']}

# 6) Training args and trainer
args = TrainingArguments(
    output_dir=str(Path('artifacts/day49/out')),
    eval_strategy='steps',
    eval_steps=10,
    max_steps=20,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    logging_steps=5,
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=ds_enc['train'].shuffle(seed=0).select(range(256)),
    eval_dataset=ds_enc['test'].select(range(128)),
    compute_metrics=compute_metrics,
)

trainer.train(); trainer.evaluate()
```
Line‑by‑line
- load_dataset: quick access to IMDB; replace with your dataset if needed
- encode: consistent padding/truncation to fixed length 128
- set_format: returns torch tensors compatible with Trainer
- compute_metrics: argmax over logits → accuracy
- TrainingArguments: 20-step laptop smoke run; remove `max_steps` only for an intentional full experiment

---

Exercise 2 — Class weights for imbalance
```python
# Suppose your dataset has imbalance; compute class weights
from collections import Counter

labels = ds_enc['train']['labels']
counts = Counter(labels)
major = max(counts.values()); total = sum(counts.values())
# inverse frequency weights normalized
weights = [total/(2*counts[i]) for i in range(2)]

import torch
w = torch.tensor(weights)

# Define a current Trainer subclass with a weighted loss.
class WeightedTrainer(Trainer):
    def __init__(self, *args, class_weights, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
        # The custom loss does not use the batch-size loss kwarg.
        self.model_accepts_loss_kwargs = False

    def compute_loss(
        self,
        model,
        inputs,
        return_outputs=False,
        num_items_in_batch=None,
    ):
        labels = inputs['labels']
        model_inputs = {key: value for key, value in inputs.items() if key != 'labels'}
        outputs = model(**model_inputs)
        loss_fn = torch.nn.CrossEntropyLoss(
            weight=self.class_weights.to(outputs.logits.device)
        )
        loss = loss_fn(outputs.logits, labels)
        return (loss, outputs) if return_outputs else loss


weighted_model = AutoModelForSequenceClassification.from_pretrained(
    'distilbert-base-uncased',
    num_labels=2,
)
trainer_weighted = WeightedTrainer(
    model=weighted_model,
    args=args,
    train_dataset=ds_enc['train'].select(range(256)),
    eval_dataset=ds_enc['test'].select(range(128)),
    compute_metrics=compute_metrics,
    class_weights=w,
)
trainer_weighted.train(); trainer_weighted.evaluate()
```
Explanation
- Compute class weights inversely proportional to class counts
- Override `Trainer.compute_loss` with its current signature, including
  `num_items_in_batch`, to apply weighted cross entropy
- This biases the learner to pay more attention to the minority class

---

Exercise 3 — spaCy matcher
```python
import spacy
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

# Pattern: (ORG) + (is|plans to) + (acquire|buy) + (ORG)
pattern = [
    {'ENT_TYPE': 'ORG'},
    {'LOWER': {'IN': ['is','plans','plan']}},
    {'LOWER': {'IN': ['to']}},
    {'LOWER': {'IN': ['acquire','buy','purchase']}},
    {'ENT_TYPE': 'ORG'}
]
matcher.add('M&A', [pattern])

text = 'Apple plans to acquire AcmeCorp next quarter for $1B.'
doc = nlp(text)
for mid, start, end in matcher(doc):
    span = doc[start:end]
    print('MATCH:', span.text)
```
Line‑by‑line
- Matcher composes token attribute rules; ENT_TYPE uses NER labels
- LOWER ensures case‑insensitive matching
- Iterate matches to extract spans; extend patterns for your domain

Notes
- Hugging Face and spaCy assets require a first network download; cache them before offline study
- For custom domains, train spaCy NER or use patterns + lists
- For long docs, prefer nlp.pipe for speed

---

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Exercise 1 — Original lesson practice

**Prompt:** Try a zero-shot-classification pipeline with your own candidate labels.

**How to reason about it:** Zero-shot classification is an optional cached/connected extension. Record model ID, revision, candidate-label wording, hypothesis template, and an ambiguous case because each can alter scores.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 2 — Original lesson practice

**Prompt:** Compare tokenization from spaCy with a Hugging Face tokenizer.

**How to reason about it:** spaCy and Transformer tokenizers optimize different representations. Inspect text, tokens, IDs, decoded output, punctuation, Unicode, and truncation rather than declaring one tokenization universally correct.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

### Exercise 3 — Truncation debugging

**Prompt:** Create a text longer than the model limit and inspect token count, special tokens, truncation, attention mask, and which part of the document is lost.

**Reasoning before implementation:** Request truncation and max_length explicitly. The tokenizer can report overflowing tokens or support sliding windows.

Silent right-side truncation can remove the decisive sentence. Record original
character/token length, retained span, strategy, stride, and model maximum.
For document tasks, compare head-only, tail-aware, and sliding-window
aggregation on labeled validation examples.

Do not set an arbitrarily huge max length: the model has a positional limit
and attention memory cost grows rapidly.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 4 — Model-provenance contract

**Prompt:** Design metadata that proves which Hugging Face model/tokenizer and spaCy pipeline produced an output, including revisions and offline cache state.

**Reasoning before implementation:** Record repository ID, immutable revision/commit when available, library versions, tokenizer settings, and local-files-only mode.

Store model and tokenizer identifiers together; mixing compatible-looking
versions can change vocabulary and special-token behavior. For spaCy, record
pipeline package name/version and enabled components.

Do not store developer-specific absolute cache paths. Record a portable cache
status and the connected preload command, then verify an offline load with
network disabled.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 5 — Evaluation leakage

**Prompt:** Find and repair leakage when near-duplicate documents or excerpts from one source appear in both train and validation.

**Reasoning before implementation:** Group by source/document/entity and use normalized hashes or similarity checks before splitting.

Random row splits over fragments can make validation measure memorization of
source wording. Define the deployment unit—new document, author, customer, or
future period—and keep that group disjoint.

Run exact normalized-hash checks first, then bounded near-duplicate detection.
Keep deduplication rules inside the data-version manifest so results can be
reconstructed.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

### Exercise 6 — Sensitive-text boundary

**Prompt:** Design a local text-classification workflow that minimizes PII in logs, cached datasets, examples, and error analysis.

**Reasoning before implementation:** Use synthetic fixtures, stable opaque IDs, redacted excerpts, bounded retention, and counts rather than raw matched values.

Raw free text can contain identifiers even when the dataset has no “email”
column. Restrict access, minimize retained fields, and never send lesson data
to an optional external service without explicit authorization.

PII detection is imperfect; document false-positive and false-negative risks.
For error analysis, retain only the minimum redacted context needed and route
incidents through the project's security process.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.
