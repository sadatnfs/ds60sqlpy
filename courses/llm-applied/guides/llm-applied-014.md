# llm-applied-014: Supervised fine-tuning data and answer-target masks

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-013`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Supervised fine-tuning data specifies the behavior a model is asked to imitate. The central investigation is concrete: Use promptIDs[1, 2] andanswerIDs[5, 6, 3]. The finish condition is inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets. record excluded despite valid token arrays. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

Supervised fine-tuning data specifies the behavior a model is asked to imitate. Each record needs a prompt, desired answer, source or annotation provenance and a family identity for splitting. In a causal language model, input tokens are shifted against next-token targets. An answer-only loss mask includes targets belonging to the answer while leaving prompt text as context. The first answer token is predicted from the final prompt position, which makes mask alignment easy to get wrong.

Formatting is part of the model interface. A pretrained chat tokenizer may insert role markers and end-of-turn tokens, and an assistant-only mask must match that exact template. Do not infer mask boundaries from character counts after tokenization. This default lesson uses literal integer tokens with an explicitly declared boundary so every active target can be enumerated. The optional pretrained recipe later checks the actual tokenizer and trainer behavior before any real adaptation. Fine-tuning on incorrect or unsupported answers can make the model more consistent at the wrong behavior.

## Design decisions and when to use this method

Use SFT when the desired behavior is stable and examples can demonstrate it more reliably than a prompt alone. Common targets include domain response structure, terminology use or task-specific transformations. Start with a prompt baseline and a data-quality audit. Track annotation disagreements, unsupported answers and template leakage before increasing training volume.

Do not use SFT as the sole store for rapidly changing facts or as a replacement for citations and access control. A model can memorize sensitive examples, and adapter weights still require governance. Keep a holdout that was not used to write templates or select hyperparameters. Measure task accuracy, unsupported output rate, formatting validity and retention of unrelated useful behavior. A decreasing training loss is necessary for diagnosing optimization but insufficient for accepting an adapted assistant.

## Vocabulary and concepts

**SFT record:** A governed prompt-answer example used for supervised weight updates.

**Answer target mask:** The aligned next-token positions contributing to the loss.

**Chat template:** The tokenizer-specific representation of roles and turn boundaries.

**Training denominator:** The number of active answer targets in an objective.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-014/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-014.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-014.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Concatenate prompt IDs and answer IDs, then createinputs=sequence[:-1] andtargets=sequence[1:]. A target is an answer target when its original sequence position is at least the prompt length. Replace excluded targets with-100 for PyTorch-style cross entropy, and count active labels explicitly. Truncation must preserve at least one answer target or reject the record. Split by task/document family before selecting demonstrations or tuning format.

## Worked example / walkthrough

### Example A: Align an answer-only record

The first answer token5 is predicted at the second input position. Masking based on input positions alone would easily exclude this target by mistake.

```python

def prepare(prompt,answer,max_length):
    if not prompt or not answer or max_length<2: raise ValueError('prompt and answer targets required')
    if any(type(x) is not int or x<0 for x in prompt+answer): raise ValueError('nonnegative integer token IDs required')
    sequence=(list(prompt)+list(answer))[:max_length]
    inputs=sequence[:-1]; targets=sequence[1:]
    labels=[token if position>=len(prompt) else -100 for position,token in enumerate(targets,1)]
    if not any(x!=-100 for x in labels): raise ValueError('truncation removed answer targets')
    return inputs,labels
inputs,labels=prepare([1,2],[5,6,3],10)
assert inputs==[1,2,5,6] and labels==[-100,5,6,3] and sum(x!=-100 for x in labels)==3
```

**Expected:** inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

### Example B: Preserve prompt context without prompt loss

The model sees the prompt through its forward computation even though prompt-prediction events are excluded from the supervised objective.

```python
other_inputs,other_labels=prepare([8,9],[5,6,3],10)
assert other_inputs[:2]==[8,9] and other_labels==labels
```

**Expected:** prompt inputs change; answer labels remain5, 6, 3.

### Example C: Reject an empty answer

A mean loss over no supervised events is undefined. Silently retaining such rows can make a data pipeline appear larger without providing learning signal.

```python
try: prepare([1,2],[],10)
except ValueError: pass
else: raise AssertionError('empty supervised answer accepted')
```

**Expected:** ValueError for no answer targets.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets. record excluded despite valid token arrays. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Align an answer-only record.** Use promptIDs[1, 2] andanswerIDs[5, 6, 3].
   **Expected:** inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.
   **Verify:** Save the assertion results for exercise 1, including inputs[1, 2, 5, 6]; labels[-100, 5, 6, 3]; 3 active targets.

2. **Preserve prompt context without prompt loss.** Change promptIDs to[8, 9] while retaining the answer; inspect labels.
   **Expected:** prompt inputs change; answer labels remain5, 6, 3.
   **Verify:** Save the assertion results for exercise 2, including prompt inputs change; answer labels remain5, 6, 3.

3. **Reject an empty answer.** Prepare a record with prompt[1, 2] and no answer tokens.
   **Expected:** ValueError for no answer targets.
   **Verify:** Save the assertion results for exercise 3, including ValueError for no answer targets.

4. **Detect destructive truncation.** Use a context limit2 for a prompt oflength2 and answerlength3.
   **Expected:** ValueError because truncation removes every answer target.
   **Verify:** Save the assertion results for exercise 4, including ValueError because truncation removes every answer target.

5. **Keep family splits disjoint.** Assign two formatting variants tofamilyF and test that they cannot cross train/test.
   **Expected:** family intersectionF is a leak.
   **Verify:** Save the assertion results for exercise 5, including family intersectionF is a leak.

6. **Reject unsupported targets before training.** Mark a target answer as unsupported by its cited source and apply an admission gate.
   **Expected:** record excluded despite valid token arrays.
   **Verify:** Save the assertion results for exercise 6, including record excluded despite valid token arrays.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain SFT record, Answer target mask, Chat template using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-013` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [TRL SFTTrainer0.24.0](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-014, Supervised fine-tuning data and answer-target masks.
Read courses/llm-applied/guides/llm-applied-014.md and courses/llm-applied/lessons/llm-applied-014.py. Direct prerequisites: `llm-applied-013`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
