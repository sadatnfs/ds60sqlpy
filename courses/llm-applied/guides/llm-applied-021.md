# llm-applied-021: Optional pretrained-model adaptation with pinned offline artifacts

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-020`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A realistic pretrained-model adaptation recipe introduces dependencies that the tiny offline exercises deliberately avoid: model weights, tokenizer files, chat templates, library versions, artifact licenses and larger resource needs. The central investigation is concrete: Read the supplied model manifest and identify model ID, revision and license note before any download. The finish condition is exact40-character revision and Apache-2.0 card note are present. pretrained executionunverified; no generated success receipt. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A realistic pretrained-model adaptation recipe introduces dependencies that the tiny offline exercises deliberately avoid: model weights, tokenizer files, chat templates, library versions, artifact licenses and larger resource needs. These are part of the experiment, not setup trivia. A model name pointing to a moving branch is not a reproducible identity. Pin an exact repository revision and record hashes of the downloaded files. Keep the acquisition step separate from local training so an offline run cannot silently fetch missing assets.

The optional recipe targetsHuggingFaceTB/SmolLM2-135M-Instruct at revision12fd25f77366fa6b3b4b768ec3050bf629380bac, whose model card was checked asApache-2.0 during authoring. This is a small pretrained model for a bounded demonstration, not a recommended production assistant. The recipe pins direct package versions, uses a literal local prompt-completion dataset, checks chat-template prefix alignment and answer-only masks, and runs at most10CPU updates. It is authored but intentionally unexecuted unless the learner separately prepares dependencies and assets. No default lesson downloads a model or calls a paid service.

## Design decisions and when to use this method

Use the optional recipe only after the default tiny-model lessons make the data, mask and optimization mechanics understandable. Prepare a separate environment so experimentation does not silently replace the classroom runtime. The direct pins are a starting reproducibility contract; for a shared release, resolve a complete platform-specific lock with hashes and retain the downloaded wheels. Record Python, OS, architecture, Torch and accelerator information with the run.

Do not assume a chat template supports assistant-only masking merely because the tokenizer has a template. The supplied recipe uses prompt/completion boundaries and verifies them. Do not enabletrust_remote_code or load arbitrary pickled checkpoints to make an unfamiliar model work. Do not treat a model card license note as a blanket approval for every dataset or deployment. The optional inference script loads only local base and adapter artifacts and still requires the same grounded-output and access controls as the default assistant baseline.

## Vocabulary and concepts

**Pinned revision:** An immutable model-repository commit identifying exact source artifacts.

**Offline asset manifest:** Local filenames,hashes,license note and revision used by a run.

**Chat-template alignment:** Agreement between rendered prompt prefix and full conversation tokens.

**Completion-only loss:** Supervision restricted to completion targets under the trainer contract.

## How to run this lesson

Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The prepared scripts live underfixtures/pretrained. prepare_assets.py requires an explicit network acknowledgement and downloads only the pinned model snapshot into a new learner-owned directory. It records SHA256 hashes. train_local.py useslocal_files_only=True andtrust_remote_code=False, checks the manifest and refuses a nonempty output directory. TRL SFTTrainer receives conversational prompt/completion records withcompletion_only_loss=True. Before training, the script inspects tokenized examples and a collated batch to ensure prompt labels are ignored and answer labels remain active. The model itself performs the causal label shift; do not shift labels twice.

## Worked example / walkthrough

### Example A: Inspect the pinned artifact contract

A license field records the inspected artifact metadata; it does not replace reviewing the actual license and intended use. The revision prevents a future branch update from silently changing the model.

```text
Model: HuggingFaceTB/SmolLM2-135M-Instruct
Revision: 12fd25f77366fa6b3b4b768ec3050bf629380bac
Card license checked: apache-2.0
Default lesson action: no download
Optional acquisition: explicit --acknowledge-network flag
```

**Expected:** exact40-character revision and Apache-2.0 card note are present.

### Example B: Separate acquisition from execution

Separating phases makes network behavior reviewable. A successful local run should not depend on an unnoticed cache hit from a different model revision.

```text
1. Prepare a separate Python3.12 environment with pinned direct dependencies.
2. Explicitly acquire the pinned snapshot and record local file hashes.
3. Disconnect or enable offline flags.
4. Run train_local.py with --model-dir pointing to the verified snapshot.
5. Missing files cause a failure,not a download.
```

**Expected:** training requires existing local assets and never falls back to a remote model ID.

### Example C: Verify chat-template boundaries

Template markers belong to the model interface. A mismatch should stop the run rather than produce a guessed mask based on character length or a hardcoded token count.

```text
prompt_ids = tokenizer.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True)
full_ids = tokenizer.apply_chat_template(prompt+completion,tokenize=True,add_generation_prompt=False)
assert full_ids[:len(prompt_ids)] == prompt_ids
assert len(full_ids) > len(prompt_ids)
```

**Expected:** prompt IDs are an exact prefix; at least one completion token remains.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: exact40-character revision and Apache-2.0 card note are present. pretrained executionunverified; no generated success receipt. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect the pinned artifact contract.** Read the supplied model manifest and identify model ID, revision and license note before any download.
   **Expected:** exact40-character revision and Apache-2.0 card note are present.
   **Verify:** Save the reasoning table for exercise 1, including exact40-character revision and Apache-2.0 card note are present.

2. **Separate acquisition from execution.** Trace the optional workflow from dependency preparation to snapshot acquisition to offline training.
   **Expected:** training requires existing local assets and never falls back to a remote model ID.
   **Verify:** Save the reasoning table for exercise 2, including training requires existing local assets and never falls back to a remote model ID.

3. **Verify chat-template boundaries.** For each local prompt/completion record, compare full conversation token IDs with the prompt rendered usingadd_generation_prompt=True.
   **Expected:** prompt IDs are an exact prefix; at least one completion token remains.
   **Verify:** Save the reasoning table for exercise 3, including prompt IDs are an exact prefix; at least one completion token remains.

4. **Inspect trainer labels before training.** Read one collated batch and compare labels with the prompt/completion boundary.
   **Expected:** prompt labels-100; active completion labels match their input token IDs.
   **Verify:** Save the reasoning table for exercise 4, including prompt labels-100; active completion labels match their input token IDs.

5. **Compare full and adapter configuration.** Inspectmodefull versusmodelora, rank 4, alpha 8, target modulesq_proj/v_proj, with the same local data and10-step cap.
   **Expected:** mode and trainable-parameter count recorded; no automatic quality winner.
   **Verify:** Save the reasoning table for exercise 5, including mode and trainable-parameter count recorded; no automatic quality winner.

6. **Refuse a false execution claim.** Write the status when scripts are authored and syntax-checked but weights were not acquired or training was not run.
   **Expected:** pretrained executionunverified; no generated success receipt.
   **Verify:** Save the reasoning table for exercise 6, including pretrained executionunverified; no generated success receipt.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Pinned revision, Offline asset manifest, Chat-template alignment using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-020` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [TRL SFTTrainer0.24.0](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.

## Complete optional scripts and setup

Read the [pretrained recipe](../fixtures/pretrained/README.md) for pinned dependencies, model identity, explicit acquisition, local hash verification, mask checks, bounded training, local inference, resource estimates and a manual container recipe with persistent mounted artifacts. These optional scripts remain unexecuted unless their own receipt says otherwise.

## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-021, Optional pretrained-model adaptation with pinned offline artifacts.
Read courses/llm-applied/guides/llm-applied-021.md and courses/llm-applied/lessons/llm-applied-021.md. Direct prerequisites: `llm-applied-020`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
