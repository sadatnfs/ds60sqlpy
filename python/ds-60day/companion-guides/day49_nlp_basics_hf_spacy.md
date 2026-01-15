# Day 49 — NLP Basics with Hugging Face and spaCy (Companion Guide)

## Learning objectives
- Tokenize text and understand subword tokenization
- Use transformers pipelines and fine-tune a text classifier
- Leverage spaCy for NER and rule-based NLP

## Why this matters
Modern NLP relies on pretrained language models and efficient tokenization. Knowing both HF and spaCy expands your toolbox.

## Core concepts and examples
### Tokenizers and pipelines
```python
from transformers import pipeline
sent = pipeline('sentiment-analysis')
sent('I love robust tooling but hate flaky tests.')
```

### Fine-tuning text classification (sketch)
```python
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer

ds = load_dataset('imdb')
tok = AutoTokenizer.from_pretrained('distilbert-base-uncased')

def encode(ex): return tok(ex['text'], truncation=True, padding='max_length', max_length=256)
ds_enc = ds.map(encode, batched=True)
model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
args = TrainingArguments(output_dir='out', evaluation_strategy='epoch', per_device_train_batch_size=16, num_train_epochs=2)
trainer = Trainer(model=model, args=args, train_dataset=ds_enc['train'], eval_dataset=ds_enc['test'])
trainer.train()
```

### spaCy NER
```python
import spacy
nlp = spacy.load('en_core_web_sm')
doc = nlp('Apple is acquiring a UK-based startup for $1B.')
[(ent.text, ent.label_) for ent in doc.ents]
```

## Common pitfalls
- Tokenization mismatch between pretraining and fine-tuning
- Truncation silently dropping important context; set max_length thoughtfully
- Data leakage via preprocessing using test data statistics

## Practice exercises
1) Build a HF pipeline for sentiment on your own dataset
2) Add class weights for class imbalance
3) Use spaCy matcher to extract domain-specific patterns

## Further reading
- Transformers: https://huggingface.co/docs/transformers
- spaCy: https://spacy.io
