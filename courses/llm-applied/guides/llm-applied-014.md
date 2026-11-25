# llm-applied-014: Supervised fine-tuning data and answer-target masks

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-013` (Paired reliability studies and family-aware uncertainty). They introduce the notation this lesson needs for sft record and answer target mask.

## Learning objectives

Supervised fine-tuning teaches the behavior represented by its examples and loss. This chapter develops a domain-training dataset from the assistant's task contract, then connects annotation quality, token masks, weighting and data splits to the behavior an optimizer is actually encouraged to learn.

## Purpose and mental model

Supervised fine-tuning data specifies the behavior a model is asked to imitate. Each record needs a prompt, desired answer, source or annotation provenance and a family identity for splitting. In a causal language model, input tokens are shifted against next-token targets. An answer-only loss mask includes targets belonging to the answer while leaving prompt text as context. The first answer token is predicted from the final prompt position, which makes mask alignment easy to get wrong.

Formatting is part of the model interface. A pretrained chat tokenizer may insert role markers and end-of-turn tokens, and an assistant-only mask must match that exact template. Do not infer mask boundaries from character counts after tokenization. This default lesson uses literal integer tokens with an explicitly declared boundary so every active target can be enumerated. The optional pretrained recipe later checks the actual tokenizer and trainer behavior before any real adaptation. Fine-tuning on incorrect or unsupported answers can make the model more consistent at the wrong behavior.

## Turn an observed behavior gap into training examples

Suppose the Methods Desk consistently finds the right evidence but struggles to produce a stable analysis record. It sometimes mixes assignment_unit with analysis_unit, omits an unknown status or adds a causal conclusion to a descriptive result. Those are candidate behavior gaps for supervised adaptation after prompt and validation baselines have been measured.

A training record should show the intended response to a particular admitted input. It needs the question, relevant context, desired answer, source or annotation provenance and a family identity. For the assistant's factual statements, the target should be supported by the supplied evidence. For its numerical statements, the target should agree with the validated calculation artifact. A polished but unsupported target teaches the model to reproduce the same failure more consistently.

The dataset should include the decisions the system is expected to make. Supported requests need useful answers. Missing-information cases need a specific unknown result. Conflicting applicable sources need an explicit conflict or the declared precedence behavior. Unsupported causal requests need an explanation of the missing design evidence. If every example is an easy success, the model receives little supervision for the boundaries that make the assistant reliable.

## Teach dependence on evidence rather than a memorized answer

A domain model can learn a shortcut from repeated templates. If every conversion question in training has the answer 0.3, success on a similarly worded evaluation question may not show that the model used the supplied counts. Vary the relevant inputs deliberately and check whether the target changes according to the rule. Preserve legitimate cases where the right answer remains unchanged as well, so the model is not rewarded for reacting to irrelevant differences.

For example, changing three purchases to four while holding ten eligible visits fixed changes the descriptive rate from 0.3 to 0.4. Changing an irrelevant source title should not change it. Removing the denominator should produce an incomplete-evidence outcome under the contract. These counterfactual pairs make the intended input-output dependency more explicit than repeated demonstrations of one final sentence.

The same principle applies to policy versions and units. A target should not use an old eligibility rule when the admitted context supplies a new applicable rule. A response about visits should not silently become an account-weighted estimate because a familiar phrase appears nearby. Annotation review must inspect those semantics before treating the records as a larger training corpus.

## The loss defines which parts of the record are learned directly

In causal language modeling, the model predicts the next token from the preceding sequence. The answer-only mask selects which prediction events contribute to the supervised objective. Prompt tokens still provide context, and answer loss can backpropagate through their representations. Excluding a prompt-prediction loss is different from making the prompt irrelevant to learning.

The indexed table later in this chapter shows why the first answer token is predicted at the final prompt position. That off-by-one detail matters: a mask based only on whether an input token belongs to the answer can remove the first answer target. A model may then learn later continuation patterns while receiving no direct supervised signal for how the answer should begin.

Formatting is part of that sequence. Role markers, separators and end-of-turn tokens depend on the intended tokenizer and template. A label mask should be checked against actual tokenized records and a collated batch. Character counts from the source text cannot reliably replace that inspection. The optional pretrained recipe later uses a different division of shifting responsibility from the manual helper, which is why its labels must be interpreted under its own trainer/model contract.

## Choose the weighting rule, not just the loss name

Let record i have m_i active answer tokens and mean token loss l_i. A global token mean is the sum of \(m_{i}\cdot l_{i}\) divided by the sum of m_i. An equally weighted mean of record losses is the sum of l_i divided by the number of records. These objectives differ when answer lengths differ.

For an illustrative pair, one answer has ten active tokens with mean loss 0.2 and another has 100 active tokens with mean loss 1.0. The token-weighted mean is (10*0.2+100*1.0)/110=102/110, about 0.9273. The equally weighted record mean is (0.2+1.0)/2=0.6. The first gives the longer answer more influence. Neither is automatically correct for every assistant task; the intended population and behavior should determine the weighting.

Batching and gradient accumulation must preserve that choice. Averaging microbatch means equally can change a token-weighted objective when active-token counts differ. Report those counts so the effective denominator is visible. A record with no active target cannot contribute a defined mean supervised loss, while a truncated record with some active targets may still have lost a necessary ending or qualification.

## Separate semantic admission, splitting and token processing

Data splitting should occur at the unit relevant to transfer before examples are selected or rewritten for training. Related document versions and template variants can leak the same answer structure across nominally different rows. If the goal is to generalize to new source families, a split that leaves near-duplicates on both sides does not test that goal.

Packing several records into one sequence creates another boundary. An answer-only loss mask does not by itself prevent later records from attending to earlier records. The attention and position policy must match the intended independence between examples. Likewise, truncation should be evaluated after rendering the real template, because overhead can consume the space the answer was expected to occupy.

A useful data audit follows each accepted record through these transformations: source-supported target, family assignment, rendered tokens, active-label positions, truncation result and final batch representation. The audit identifies whether a failure is semantic, structural or numerical. More optimizer steps cannot repair a target that is wrong or a mask that supervises the wrong event.

The next chapter runs the complete update loop on a small decoder. Its literal tokens make those mechanics observable, while the dataset principles here explain what would be required for the same machinery to support a meaningful domain-assistant experiment.

## Design decisions and when to use this method

Use SFT when the desired behavior is stable and examples can demonstrate it more reliably than a prompt alone. Common targets include domain response structure, terminology use or task-specific transformations. Start with a prompt baseline and a data-quality audit. Track annotation disagreements, unsupported answers and template leakage before increasing training volume.

Do not use SFT as the sole store for rapidly changing facts or as a replacement for citations and access control. A model can memorize sensitive examples, and adapter weights still require governance. Keep a holdout that was not used to write templates or select hyperparameters. Measure task accuracy, unsupported output rate, formatting validity and retention of unrelated useful behavior. A decreasing training loss is necessary for diagnosing optimization but insufficient for accepting an adapted assistant.

Review training records as both semantic targets and token-level events. A supported answer can be tokenized or masked incorrectly; a perfectly aligned mask can still train an unsupported answer. Keep annotation admission and numerical participation as independent checks.

Choose whether the objective weights tokens, examples or source families. Longer answers receive more weight under a global token mean. If that is not the desired task weighting, change the declared objective rather than silently averaging per-batch means with different active-token counts.

## Vocabulary and concepts

**SFT record:** A governed prompt-answer example used for supervised weight updates.

**Answer target mask:** The aligned next-token positions contributing to the loss.

**Chat template:** The tokenizer-specific representation of roles and turn boundaries.

**Training denominator:** The number of active answer targets in an objective.

## How to run this lesson

Run `courses/llm-applied/lessons/llm-applied-014.py` in the declared `python-core` profile. *Align an answer-only record*, *Preserve prompt context without prompt loss* and *Reject an empty answer* need only the Python standard library and literal fixtures.

Copy it to `.learning/expansion/llm-applied-014/` or the saved pad before editing; nothing is installed or downloaded.

Run Examples A to C in one scratch file: *Preserve prompt context without prompt loss* and *Reject an empty answer* reuse the helper and fixture introduced in *Align an answer-only record*. Before running Example A, write its intermediate quantities by hand and predict the result. It should give: inputs `[1, 2, 5, 6]`; labels `[-100, 5, 6, 3]`; 3 active targets. Example B should give: Prompt inputs change; answer labels remain 5, 6, 3. Example C should give: ValueError for no answer targets. Use the tolerance in each assertion; counts, identities and decisions must match exactly.

## Syntax anatomy and reasoning sequence

Concatenate prompt IDs and answer IDs, then create `inputs=sequence[:-1]` and `targets=sequence[1:]`. A target is an answer target when its original sequence position is at least the prompt length. Replace excluded targets with -100 for PyTorch-style cross entropy, and count active labels explicitly. Truncation must preserve at least one answer target or reject the record. Split by task/document family before selecting demonstrations or tuning format.

## Enumerate the target positions before training

Let the prompt length be P and the concatenated sequence length be L. A causal next-token example at input index i predicts original sequence position i+1. It belongs to the answer when \(i+1\ge P\), or equivalently \(i\ge P-1\). The first answer token is therefore supervised from the final prompt position, not from the first answer input position.

For prompt `[1, 2]` and answer `[5, 6, 3]`, the complete sequence is `[1, 2, 5, 6, 3]`:

| Input index | Input token | Next-token target | Participates in answer loss |
| --- | --- | --- | --- |
| 0 | 1 | 2 | No, prompt continuation |
| 1 | 2 | 5 | Yes, first answer token |
| 2 | 5 | 6 | Yes |
| 3 | 6 | 3 | Yes, final answer token |

Inputs are `[1, 2, 5, 6]` and labels `[-100, 5, 6, 3]`, with three active targets. The mean cross-entropy denominator is three for this record. Dividing the summed active loss by four would dilute the objective with the excluded prompt event. The sentinel-100 is a loss API convention, not a token the model should generate or embed.

Masking a prompt target removes that position's direct loss term. It does not remove the prompt from the forward computation. Later answer positions can attend to prompt representations, so the answer loss can backpropagate through prompt embeddings and attention paths. Confusing those two boundaries can lead to detaching useful context or incorrectly claiming prompt tokens receive no training signal.

Truncation must be inspected after alignment. A maximum concatenated length of two retains `[1, 2]` and no answer target, so the helper rejects it. A limit of four retains `[1, 2, 5, 6]`, giving labels `[-100, 5, 6]`. That passes the helper's at-least-one-answer-target rule but loses the final token 3. If 3 is an end marker, the truncated example no longer teaches the complete stopping behavior. Acceptance of some supervised content is weaker than preservation of the full answer.

The helper treats max_length as a sequence-length bound for this literal-token fixture. The actual model context, chat-template overhead, role tokens and generation markers must be counted under the intended tokenizer. A character boundary in raw text is not necessarily a token boundary. TRL's versioned SFT documentation distinguishes training formats and loss-mask behavior; the optional pretrained recipe checks the concrete template used there. [TRL 1.18.0 SFTTrainer](https://huggingface.co/docs/trl/v1.18.0/en/sft_trainer).

Packing introduces another independence boundary. Two examples in separate batch rows have separate attention contexts. Concatenating them into one longer row can let tokens from the second example attend to the first unless the packing/attention policy prevents it. An answer-only loss mask by itself does not define that attention boundary. State whether cross-example context is allowed and test the resulting positions rather than assuming that a label sentinel blocks attention.

### Interview reasoning with explanatory answers

**Why is the first answer target easy to lose?** Its prediction is emitted at the last prompt input position. Masking by whether the input token is inside the answer creates an off-by-one error.

**Does valid training loss imply trustworthy targets?** No. Cross entropy will reward matching any accepted target, including an invented or policy-violating answer. Source support and annotation review must happen before optimization.

**Why report active-token counts?** They define the denominator and reveal empty or destructively truncated examples. They also make comparisons between variable-length batches interpretable.

## Worked example / walkthrough

### Example A: Align an answer-only record

The first answer token 5 is predicted at the second input position. Masking based on input positions alone would easily exclude this target by mistake.

```python
def prepare(prompt, answer, max_length):
    if not prompt or not answer or max_length < 2:
        raise ValueError("prompt and answer targets required")
    if any(type(x) is not int or x < 0 for x in prompt + answer):
        raise ValueError("nonnegative integer token IDs required")
    sequence = (list(prompt) + list(answer))[:max_length]
    inputs = sequence[:-1]
    targets = sequence[1:]
    labels = [
        token if position >= len(prompt) else -100 for position, token in enumerate(targets, 1)
    ]
    if not any(x != -100 for x in labels):
        raise ValueError("truncation removed answer targets")
    return inputs, labels


inputs, labels = prepare([1, 2], [5, 6, 3], 10)
assert inputs == [1, 2, 5, 6] and labels == [-100, 5, 6, 3] and sum(x != -100 for x in labels) == 3
```

**Expected:** inputs `[1, 2, 5, 6]`; labels `[-100, 5, 6, 3]`; 3 active targets.

### Example B: Preserve prompt context without prompt loss

The model sees the prompt through its forward computation even though prompt-prediction events are excluded from the supervised objective.

```python
other_inputs, other_labels = prepare([8, 9], [5, 6, 3], 10)
assert other_inputs[:2] == [8, 9] and other_labels == labels
```

**Expected:** prompt inputs change; answer labels remain 5, 6, 3.

### Example C: Reject an empty answer

A mean loss over no supervised events is undefined. Silently retaining such rows can make a data pipeline appear larger without providing learning signal.

```python
try:
    prepare([1, 2], [], 10)
except ValueError:
    pass
else:
    raise AssertionError("empty supervised answer accepted")
```

**Expected:** ValueError for no answer targets.

## Prediction before your attempt

Before reading the code for *Preserve prompt context without prompt loss*, predict its result from the prompt alone: Change prompt IDs to `[8, 9]` while retaining the answer; inspect labels. Write the guess beside the stated outcome (prompt inputs change; answer labels remain 5, 6, 3). Then predict how the decisive case, *Reject unsupported targets before training*, should end: Mark a target answer as unsupported by its cited source and apply an admission gate. For supervised fine-tuning data and answer-target masks, the finish condition is: inputs `[1, 2, 5, 6]`; labels `[-100, 5, 6, 3]`; 3 active targets. Record excluded despite valid token arrays.

## Exercises

1. **Align an answer-only record.** Use prompt IDs `[1, 2]` and answer IDs `[5, 6, 3]`.
   **Expected:** inputs `[1, 2, 5, 6]`; labels `[-100, 5, 6, 3]`; 3 active targets.
   **Verify:** Save the assertion results for exercise 1, including inputs `[1, 2, 5, 6]`; labels `[-100, 5, 6, 3]`; 3 active targets.
   **Transfer:** This repeats Example A; reproduce it closed-book, then change one literal and predict the new result before running it.

2. **Preserve prompt context without prompt loss.** Change prompt IDs to `[8, 9]` while retaining the answer; inspect labels.
   **Expected:** prompt inputs change; answer labels remain 5, 6, 3.
   **Verify:** Save the assertion results for exercise 2, including prompt inputs change; answer labels remain 5, 6, 3.
   **Transfer:** This repeats Example B; reproduce it closed-book, then change one literal and predict the new result before running it.

3. **Reject an empty answer.** Prepare a record with prompt `[1, 2]` and no answer tokens.
   **Expected:** ValueError for no answer targets.
   **Verify:** Save the assertion results for exercise 3, including ValueError for no answer targets.
   **Transfer:** This repeats Example C; reproduce it closed-book, then change one literal and predict the new result before running it.

4. **Detect destructive truncation.** Use a context limit 2 for a prompt of length 2 and answer length 3.
   **Expected:** ValueError because truncation removes every answer target.
   **Verify:** Save the assertion results for exercise 4, including ValueError because truncation removes every answer target.

5. **Keep family splits disjoint.** Assign two formatting variants to family F and test that they cannot cross train/test.
   **Expected:** family intersection F is a leak.
   **Verify:** Save the assertion results for exercise 5, including family intersection F is a leak.

6. **Reject unsupported targets before training.** Mark a target answer as unsupported by its cited source and apply an admission gate.
   **Expected:** record excluded despite valid token arrays.
   **Verify:** Save the assertion results for exercise 6, including record excluded despite valid token arrays.

## Common pitfalls and diagnosis

If the first generated answer token is weak, inspect the shifted mask table before changing learning rate. If loss is unexpectedly small, verify that target positions were not excluded or labels leaked into the wrong input positions. If a record passes despite losing its stop marker, inspect whether the admission rule requires a complete answer or merely some active targets.

If prompt embeddings receive gradients, check whether they influence supervised answer positions before calling it a mask failure. If packed examples interfere, inspect attention boundaries separately from label masks. If formatting success grows while factual support worsens, audit target provenance rather than treating the optimizer as an evidence validator.

## Progressive hints

Hint 1: restate sft record and answer target mask for the fixture in *Align an answer-only record*. Hint 2: change one literal in *Preserve prompt context without prompt loss* and note which intermediate value moves. Hint 3: compare your fourth exercise, *Detect destructive truncation*, with its stated result (ValueError because truncation removes every answer target). If *Reject unsupported targets before training* accepts an input it should reject, look for the missing check rather than widening a tolerance.

## Self-check and retrieval

Close the examples and explain sft record, answer target mask and chat template using *Align an answer-only record*. Recompute its result (inputs `[1, 2, 5, 6]`; labels `[-100, 5, 6, 3]`; 3 active targets) from the inputs. Change one input in *Reject an empty answer* and predict whether the stated result (ValueError for no answer targets) still holds. Say which part of supervised fine-tuning data and answer-target masks the code guarantees and which part would need new observations.

## Next step

If *Align an answer-only record* cannot be reconstructed without the solution, revisit `llm-applied-013` (Paired reliability studies and family-aware uncertainty). Otherwise keep the six observations from supervised fine-tuning data and answer-target masks and continue to `llm-applied-015` (Full supervised fine-tuning of a tiny causal decoder).

## Sources and verification status

Reference for sft record: [TRL SFTTrainer 1.18.0](https://huggingface.co/docs/trl/v1.18.0/en/sft_trainer), reviewed 2026-11-18. The fixtures for *Align an answer-only record*, *Preserve prompt context without prompt loss* and *Reject an empty answer* and the six exercises are original course material.

Execution gates are described in [validation](../../../docs/validation.md); CI artifacts show which checks ran for each revision.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-014, Supervised fine-tuning data and answer-target masks.
Read courses/llm-applied/guides/llm-applied-014.md and courses/llm-applied/lessons/llm-applied-014.py. Direct prerequisites: `llm-applied-013`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
