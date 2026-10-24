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

Concatenate prompt IDs and answer IDs, then create inputs=sequence[:-1] and targets=sequence[1:]. A target is an answer target when its original sequence position is at least the prompt length. Replace excluded targets with-100 for PyTorch-style cross entropy, and count active labels explicitly. Truncation must preserve at least one answer target or reject the record. Split by task/document family before selecting demonstrations or tuning format.

## Enumerate the target positions before training

Let the prompt length be P and the concatenated sequence length be L. A causal next-token example at input index i predicts original sequence position i+1. It belongs to the answer when \(i+1\ge P\), or equivalently \(i\ge P-1\). The first answer token is therefore supervised from the final prompt position, not from the first answer input position.

For prompt[1, 2] and answer[5, 6, 3], the complete sequence is[1, 2, 5, 6, 3]:

| Input index | Input token | Next-token target | Participates in answer loss |
| --- | --- | --- | --- |
| 0 | 1 | 2 | No, prompt continuation |
| 1 | 2 | 5 | Yes, first answer token |
| 2 | 5 | 6 | Yes |
| 3 | 6 | 3 | Yes, final answer token |

Inputs are[1, 2, 5, 6] and labels[-100, 5, 6, 3], with three active targets. The mean cross-entropy denominator is three for this record. Dividing the summed active loss by four would dilute the objective with the excluded prompt event. The sentinel-100 is a loss API convention, not a token the model should generate or embed.

Masking a prompt target removes that position's direct loss term. It does not remove the prompt from the forward computation. Later answer positions can attend to prompt representations, so the answer loss can backpropagate through prompt embeddings and attention paths. Confusing those two boundaries can lead to detaching useful context or incorrectly claiming prompt tokens receive no training signal.

Truncation must be inspected after alignment. A maximum concatenated length of two retains[1, 2] and no answer target, so the helper rejects it. A limit of four retains[1, 2, 5, 6], giving labels[-100, 5, 6]. That passes the helper's at-least-one-answer-target rule but loses the final token3. If3 is an end marker, the truncated example no longer teaches the complete stopping behavior. Acceptance of some supervised content is weaker than preservation of the full answer.

The helper treats max_length as a sequence-length bound for this literal-token fixture. The actual model context, chat-template overhead, role tokens and generation markers must be counted under the intended tokenizer. A character boundary in raw text is not necessarily a token boundary. TRL's versioned SFT documentation distinguishes training formats and loss-mask behavior; the optional pretrained recipe checks the concrete template used there. [TRL0.24.0 SFTTrainer](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer).

Packing introduces another independence boundary. Two examples in separate batch rows have separate attention contexts. Concatenating them into one longer row can let tokens from the second example attend to the first unless the packing/attention policy prevents it. An answer-only loss mask by itself does not define that attention boundary. State whether cross-example context is allowed and test the resulting positions rather than assuming that a label sentinel blocks attention.

### Interview reasoning with explanatory answers

**Why is the first answer target easy to lose?** Its prediction is emitted at the last prompt input position. Masking by whether the input token is inside the answer creates an off-by-one error.

**Does valid training loss imply trustworthy targets?** No. Cross entropy will reward matching any accepted target, including an invented or policy-violating answer. Source support and annotation review must happen before optimization.

**Why report active-token counts?** They define the denominator and reveal empty or destructively truncated examples. They also make comparisons between variable-length batches interpretable.

## Exercise 1: Align an answer-only record

The question is: Use prompt IDs[1, 2] and answer IDs[5, 6, 3].

The first answer token5 is predicted at the second input position. Masking based on input positions alone would easily exclude this target by mistake.

```python
inputs,labels=prepare([1,2],[5,6,3],10)
assert inputs==[1,2,5,6] and labels==[-100,5,6,3] and sum(x!=-100 for x in labels)==3
```

**Expected:** inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

**Verify:** Compare the computed values or written argument with inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

## Exercise 2: Preserve prompt context without prompt loss

The question is: Change prompt IDs to[8, 9] while retaining the answer; inspect labels.

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
