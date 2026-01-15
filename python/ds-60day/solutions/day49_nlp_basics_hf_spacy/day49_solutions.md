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

# 2) Data: use IMDB for demo
ds = load_dataset('imdb')

# 3) Tokenizer and encoding
tok = AutoTokenizer.from_pretrained('distilbert-base-uncased')

def encode(batch):
    return tok(batch['text'], truncation=True, padding='max_length', max_length=256)

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
args = TrainingArguments(output_dir='out', evaluation_strategy='epoch',
                         per_device_train_batch_size=16, per_device_eval_batch_size=32,
                         num_train_epochs=1, logging_steps=50)
trainer = Trainer(model=model, args=args, train_dataset=ds_enc['train'].shuffle(seed=0).select(range(8000)),
                  eval_dataset=ds_enc['test'].select(range(2000)), compute_metrics=compute_metrics)

trainer.train(); trainer.evaluate()
```
Line‑by‑line
- load_dataset: quick access to IMDB; replace with your dataset if needed
- encode: consistent padding/truncation to fixed length 256
- set_format: returns torch tensors compatible with Trainer
- compute_metrics: argmax over logits → accuracy
- TrainingArguments: small epochs for demo; adjust for real training

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

# Define custom loss with weights in Trainer
from transformers import TrainingArguments

def custom_loss(model, inputs, return_outputs=False):
    labels = inputs.get('labels')
    outputs = model(**{k:v for k,v in inputs.items() if k!='labels'})
    logits = outputs.logits
    loss_fn = torch.nn.CrossEntropyLoss(weight=w.to(logits.device))
    loss = loss_fn(logits, labels)
    return (loss, outputs) if return_outputs else loss

trainer_weighted = Trainer(model=model, args=args, train_dataset=ds_enc['train'].select(range(8000)),
                           eval_dataset=ds_enc['test'].select(range(2000)), compute_metrics=compute_metrics)
trainer_weighted.compute_loss = custom_loss
trainer_weighted.train(); trainer_weighted.evaluate()
```
Explanation
- Compute class weights inversely proportional to class counts
- Plug a custom compute_loss into Trainer to apply weighted CrossEntropy
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
- For custom domains, train spaCy NER or use patterns + lists
- For long docs, prefer nlp.pipe for speed
