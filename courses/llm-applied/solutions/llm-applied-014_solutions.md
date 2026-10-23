# llm-applied-014: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Supervised fine-tuning data specifies the behavior a model is asked to imitate. Each record needs a prompt, desired answer, source or annotation provenance and a family identity for splitting. In a causal language model, input tokens are shifted against next-token targets. An answer-only loss mask includes targets belonging to the answer while leaving prompt text as context. The first answer token is predicted from the final prompt position, which makes mask alignment easy to get wrong.

Formatting is part of the model interface. A pretrained chat tokenizer may insert role markers and end-of-turn tokens, and an assistant-only mask must match that exact template. Do not infer mask boundaries from character counts after tokenization. This default lesson uses literal integer tokens with an explicitly declared boundary so every active target can be enumerated. The optional pretrained recipe later checks the actual tokenizer and trainer behavior before any real adaptation. Fine-tuning on incorrect or unsupported answers can make the model more consistent at the wrong behavior.

**SFT record:** A governed prompt-answer example used for supervised weight updates.

**Answer target mask:** The aligned next-token positions contributing to the loss.

**Chat template:** The tokenizer-specific representation of roles and turn boundaries.

**Training denominator:** The number of active answer targets in an objective.

## Reading the implementation

Concatenate prompt IDs and answer IDs, then createinputs=sequence[:-1] andtargets=sequence[1:]. A target is an answer target when its original sequence position is at least the prompt length. Replace excluded targets with-100 for PyTorch-style cross entropy, and count active labels explicitly. Truncation must preserve at least one answer target or reject the record. Split by task/document family before selecting demonstrations or tuning format.

## Exercise 1: Align an answer-only record

The question is: Use promptIDs[1, 2] andanswerIDs[5, 6, 3].

The first answer token5 is predicted at the second input position. Masking based on input positions alone would easily exclude this target by mistake.

```python
inputs,labels=prepare([1,2],[5,6,3],10)
assert inputs==[1,2,5,6] and labels==[-100,5,6,3] and sum(x!=-100 for x in labels)==3
```

**Expected:** inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

**Verify:** Compare the computed values or written argument with inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

## Exercise 2: Preserve prompt context without prompt loss

The question is: Change promptIDs to[8, 9] while retaining the answer; inspect labels.

The model sees the prompt through its forward computation even though prompt-prediction events are excluded from the supervised objective.

```python
other_inputs,other_labels=prepare([8,9],[5,6,3],10)
assert other_inputs[:2]==[8,9] and other_labels==labels
```

**Expected:** prompt inputs change; answer labels remain5, 6, 3.

**Verify:** Compare the computed values or written argument with prompt inputs change; answer labels remain5, 6, 3.

## Exercise 3: Reject an empty answer

The question is: Prepare a record with prompt[1, 2] and no answer tokens.

A mean loss over no supervised events is undefined. Silently retaining such rows can make a data pipeline appear larger without providing learning signal.

```python
try: prepare([1,2],[],10)
except ValueError: pass
else: raise AssertionError('empty supervised answer accepted')
```

**Expected:** ValueError for no answer targets.

**Verify:** Compare the computed values or written argument with ValueError for no answer targets.

## Exercise 4: Detect destructive truncation

The question is: Use a context limit2 for a prompt oflength2 and answerlength3.

Truncation policy must be checked after constructing the aligned labels. A record can remain syntactically nonempty while losing all supervised content.

```python
try: prepare([1,2],[5,6,3],2)
except ValueError: pass
else: raise AssertionError('answer removed by truncation')
```

**Expected:** ValueError because truncation removes every answer target.

**Verify:** Compare the computed values or written argument with ValueError because truncation removes every answer target.

## Exercise 5: Keep family splits disjoint

The question is: Assign two formatting variants tofamilyF and test that they cannot cross train/test.

A model can memorize a template or answer pattern. Grouped evaluation measures transfer beyond the exact family used to construct training examples.

```python
train_families={'F'}; test_families={'F','G'}
assert train_families&test_families=={'F'}
```

**Expected:** family intersectionF is a leak.

**Verify:** Compare the computed values or written argument with family intersectionF is a leak.

## Exercise 6: Reject unsupported targets before training

The question is: Mark a target answer as unsupported by its cited source and apply an admission gate.

A correct tensor mask cannot make a fabricated target trustworthy. Data governance and numerical correctness are independent prerequisites for adaptation.

```python
record={'inputs':inputs,'labels':labels,'source_supported':False,'annotation_reviewed':True}
accepted=record['source_supported'] and record['annotation_reviewed']
assert not accepted
```

**Expected:** record excluded despite valid token arrays.

**Verify:** Compare the computed values or written argument with record excluded despite valid token arrays.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
