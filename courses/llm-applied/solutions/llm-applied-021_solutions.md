# llm-applied-021: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A realistic pretrained-model adaptation recipe introduces dependencies that the tiny offline exercises deliberately avoid: model weights, tokenizer files, chat templates, library versions, artifact licenses and larger resource needs. These are part of the experiment, not setup trivia. A model name pointing to a moving branch is not a reproducible identity. Pin an exact repository revision and record hashes of the downloaded files. Keep the acquisition step separate from local training so an offline run cannot silently fetch missing assets.

The optional recipe targetsHuggingFaceTB/SmolLM2-135M-Instruct at revision12fd25f77366fa6b3b4b768ec3050bf629380bac, whose model card was checked asApache-2.0 during authoring. This is a small pretrained model for a bounded demonstration, not a recommended production assistant. The recipe pins direct package versions, uses a literal local prompt-completion dataset, checks chat-template prefix alignment and answer-only masks, and runs at most10CPU updates. It is authored but intentionally unexecuted unless the learner separately prepares dependencies and assets. No default lesson downloads a model or calls a paid service.

**Pinned revision:** An immutable model-repository commit identifying exact source artifacts.

**Offline asset manifest:** Local filenames,hashes,license note and revision used by a run.

**Chat-template alignment:** Agreement between rendered prompt prefix and full conversation tokens.

**Completion-only loss:** Supervision restricted to completion targets under the trainer contract.

## Reading the implementation

The prepared scripts live underfixtures/pretrained. prepare_assets.py requires an explicit network acknowledgement and downloads only the pinned model snapshot into a new learner-owned directory. It records SHA256 hashes. train_local.py useslocal_files_only=True andtrust_remote_code=False, checks the manifest and refuses a nonempty output directory. TRL SFTTrainer receives conversational prompt/completion records withcompletion_only_loss=True. Before training, the script inspects tokenized examples and a collated batch to ensure prompt labels are ignored and answer labels remain active. The model itself performs the causal label shift; do not shift labels twice.

## Exercise 1: Inspect the pinned artifact contract

The question is: Read the supplied model manifest and identify model ID, revision and license note before any download.

A license field records the inspected artifact metadata; it does not replace reviewing the actual license and intended use. The revision prevents a future branch update from silently changing the model.

```text
Model: HuggingFaceTB/SmolLM2-135M-Instruct
Revision: 12fd25f77366fa6b3b4b768ec3050bf629380bac
Card license checked: apache-2.0
Default lesson action: no download
Optional acquisition: explicit --acknowledge-network flag
```

**Expected:** exact40-character revision and Apache-2.0 card note are present.

**Verify:** Compare the computed values or written argument with exact40-character revision and Apache-2.0 card note are present.

## Exercise 2: Separate acquisition from execution

The question is: Trace the optional workflow from dependency preparation to snapshot acquisition to offline training.

Separating phases makes network behavior reviewable. A successful local run should not depend on an unnoticed cache hit from a different model revision.

```text
1. Prepare a separate Python3.12 environment with pinned direct dependencies.
2. Explicitly acquire the pinned snapshot and record local file hashes.
3. Disconnect or enable offline flags.
4. Run train_local.py with --model-dir pointing to the verified snapshot.
5. Missing files cause a failure,not a download.
```

**Expected:** training requires existing local assets and never falls back to a remote model ID.

**Verify:** Compare the computed values or written argument with training requires existing local assets and never falls back to a remote model ID.

## Exercise 3: Verify chat-template boundaries

The question is: For each local prompt/completion record, compare full conversation token IDs with the prompt rendered usingadd_generation_prompt=True.

Template markers belong to the model interface. A mismatch should stop the run rather than produce a guessed mask based on character length or a hardcoded token count.

```text
prompt_ids = tokenizer.apply_chat_template(prompt,tokenize=True,add_generation_prompt=True)
full_ids = tokenizer.apply_chat_template(prompt+completion,tokenize=True,add_generation_prompt=False)
assert full_ids[:len(prompt_ids)] == prompt_ids
assert len(full_ids) > len(prompt_ids)
```

**Expected:** prompt IDs are an exact prefix; at least one completion token remains.

**Verify:** Compare the computed values or written argument with prompt IDs are an exact prefix; at least one completion token remains.

## Exercise 4: Inspect trainer labels before training

The question is: Read one collated batch and compare labels with the prompt/completion boundary.

The trainer and model divide responsibilities:the collator marks ignored positions, and the causal model shifts internally. A second manual shift would train on the wrong targets.

```text
batch = next(iter(trainer.get_train_dataloader()))
active = batch['labels'] != -100
assert active.any()
assert (batch['labels'][active] == batch['input_ids'][active]).all()
# The script additionally verifies each processed completion mask and its prefix.
```

**Expected:** prompt labels-100; active completion labels match their input token IDs.

**Verify:** Compare the computed values or written argument with prompt labels-100; active completion labels match their input token IDs.

## Exercise 5: Compare full and adapter configuration

The question is: Inspectmodefull versusmodelora, rank 4, alpha 8, target modulesq_proj/v_proj, with the same local data and10-step cap.

The recipe supports a controlled mechanism comparison, not an assertion that a ten-step run produces a useful assistant. Actual memory and time must be measured on the prepared environment.

```text
Full: all model parameters trainable.
LoRA: frozen base plus rank4 adapters on q_proj and v_proj.
Both: max_steps10,max_length128,batch1,seed7,CPU,report_to=[];
Evaluate the same held-out families and retain both receipts.
```

**Expected:** mode and trainable-parameter count recorded; no automatic quality winner.

**Verify:** Compare the computed values or written argument with mode and trainable-parameter count recorded; no automatic quality winner.

## Exercise 6: Refuse a false execution claim

The question is: Write the status when scripts are authored and syntax-checked but weights were not acquired or training was not run.

An optional recipe remains valuable without pretending it has executed. The status must distinguish code review, asset preparation, training and task-quality acceptance.

```text
Status: recipe authored and statically checked.
Model/data downloads performed by this authoring pass: none.
Pretrained training executed: no.
Required next evidence: local asset verification,mask inspection,actual run receipt,held-out evaluation.
```

**Expected:** pretrained executionunverified; no generated success receipt.

**Verify:** Compare the computed values or written argument with pretrained executionunverified; no generated success receipt.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
