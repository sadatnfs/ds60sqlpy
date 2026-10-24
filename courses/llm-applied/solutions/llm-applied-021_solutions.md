# llm-applied-021: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A realistic pretrained-model adaptation recipe introduces dependencies that the tiny offline exercises deliberately avoid: model weights, tokenizer files, chat templates, library versions, artifact licenses and larger resource needs. These are part of the experiment, not setup trivia. A model name pointing to a moving branch is not a reproducible identity. Pin an exact repository revision and record hashes of the downloaded files. Keep the acquisition step separate from local training so an offline run cannot silently fetch missing assets.

The optional recipe targetsHuggingFaceTB/SmolLM2-135M-Instruct at revision12fd25f77366fa6b3b4b768ec3050bf629380bac, whose model card was checked asApache-2.0 during authoring. This is a small pretrained model for a bounded demonstration, not a recommended production assistant. The recipe pins direct package versions, uses a literal local prompt-completion dataset, checks chat-template prefix alignment and answer-only masks, and runs at most10CPU updates. The optional recipe has separate bounded Linux arm64 execution evidence for ten full-SFT and LoRA updates, while its generation probe produced an incorrect formula despite evidence. Learners must still explicitly prepare their own dependencies and assets; mechanics success does not establish subject expertise. No default lesson downloads a model or calls a paid service.

**Pinned revision:** An immutable model-repository commit identifying exact source artifacts.

**Offline asset manifest:** Local filenames,hashes,license note and revision used by a run.

**Chat-template alignment:** Agreement between rendered prompt prefix and full conversation tokens.

**Completion-only loss:** Supervision restricted to completion targets under the trainer contract.

## Reading the implementation

The prepared scripts live underfixtures/pretrained. prepare_assets.py requires an explicit network acknowledgement and downloads only the pinned model snapshot into a new learner-owned directory. It records SHA256 hashes. train_local.py useslocal_files_only=True andtrust_remote_code=False, checks the manifest and refuses a nonempty output directory. TRL SFTTrainer receives conversational prompt/completion records withcompletion_only_loss=True. Before training, the script inspects tokenized examples and a collated batch to ensure prompt labels are ignored and answer labels remain active. The model itself performs the causal label shift; do not shift labels twice.

## Read the qualified recipe as several independent evidence tiers

The pinned revision identifies a particular repository state; the local manifest identifies the acquired files and their hashes. The lock identifies resolved dependency artifacts for a platform. The image identifies the executable environment. None of these identities alone establishes that training happened. A run receipt and saved artifact provide that next tier, followed by separate reload and task-quality observations.

The existing recipe record reports13 acquired files and actual 10-update CPU runs for both full SFT and LoRA. Full SFT has134515008 trainable parameters; the rank-four q_proj/v_proj adapter path has230400. The recorded held-out losses changed from6.721148 to0.008058 for full SFT and from6.721148 to6.474194 for LoRA. These are observations from the qualified recipe, not reruns performed by this prose review. [Optional recipe evidence and workflow](../fixtures/pretrained/README.md).

The evaluation dataset contains one held-out entity label, while the four training records share an assignment-unit extraction task and prompt template. Distinct family labels do not automatically produce independent business domains. The dramatic full-SFT loss drop therefore needs that narrow context. It does not establish that full SFT generally beats LoRA or that either model understands unrelated statistical questions.

The generation probe is particularly informative because it tests a different boundary. It supplies the correct conversion definition as evidence, yet the saved adapter produced a fluent incorrect formula: eligible visits divided by eligible visits. That is a task-quality failure despite successful asset loading, masking, optimization, save and reload. The output also did not establish claim-level citation support. Preserve the failure rather than replacing it with a hypothetical correct answer.

Mask alignment differs from the earlier manual tiny-token helper. In the TRL path, active labels equal the corresponding input token IDs and ignored prompt positions contain-100. The causal model shifts labels internally when calculating next-token loss. Manually shifting those labels again would train the wrong target. The processed completion mask and actual collated batch are inspected before training, and records longer than the declared 128-token limit are rejected rather than silently losing answers.

Chat-template prefix equality is another concrete gate. The prompt rendered with a generation marker must be an exact token prefix of the full prompt-plus-completion rendering. This checks the specific template's boundary, not a universal property of all templates. A different model or tokenizer may require a different valid construction. Preserve the actual tokenized example and prefix lengths in the receipt.

Two LoRA runs in the same qualified image produced matching adapter hashes and evaluation loss after seeding before adapter construction. Setting a trainer seed later cannot retroactively recreate already sampled adapter matrices. That repeatability result is valuable but is limited to the tested environment and ordering. An amd64 dependency lock is preparation evidence; it is not an executed amd64 or Windows result.

A successful local loader must not silently fall back to a remote model ID when a file is missing. The recipe's explicit connected acquisition phase and later local-only, networking-disabled runs make those behaviors separable. Hash verification detects modified artifacts; it does not make a model's generated claims true or establish approval for every downstream dataset and use.

### Interview reasoning with explanatory answers

**What does the pinned revision prove?** It identifies the selected upstream artifact state. Actual local verification, execution and task quality need their own evidence.

**Why can low held-out token loss coexist with a wrong generated formula?** The evaluation record and teacher-forced objective can be narrow, while generation faces another task and its own rollout. The observed output must be scored under the intended domain contract.

**Why inspect labels instead of trusting a completion-only flag?** Configuration expresses intent. Processed examples and a real collated batch show whether the chosen trainer/template combination produced the intended active targets before optimization.

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

**Expected:** exact 40-character revision and Apache-2.0 card note are present.

**Verify:** Compare the computed values or written argument with exact 40-character revision and Apache-2.0 card note are present.

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

The question is: Inspectmodefull versusmodelora, rank 4, alpha 8, target modulesq_proj/v_proj, with the same local data and 10-step cap.

The recipe supports a controlled mechanism comparison, not an assertion that a ten-step run produces a useful assistant. Actual memory and time must be measured on the prepared environment.

```text
Full: all model parameters trainable.
LoRA: frozen base plus rank4 adapters on q_proj and v_proj.
Both: max_steps10,max_length128,batch1,seed7,CPU,report_to=[];
Evaluate the same held-out families and retain both receipts.
```

**Expected:** mode and trainable-parameter count recorded; no automatic quality winner.

**Verify:** Compare the computed values or written argument with mode and trainable-parameter count recorded; no automatic quality winner.

## Exercise 6: Distinguish an unexecuted learner scenario

The question is: For a hypothetical new learner who has only reviewed scripts, write the status without overwriting the separately qualified maintainer recipe.

An optional recipe remains valuable without pretending it has executed. The status must distinguish code review, asset preparation, training and task-quality acceptance.

```text
Scenario: a new learner has only reviewed the recipe.
Assets acquired for this learner run: no.
Training executed for this learner run: no.
Separate maintainer recipe: qualified mechanics with an observed generation-quality failure.
Required next evidence: local asset verification,mask inspection,actual run receipt,held-out evaluation.
```

**Expected:** pretrained execution unverified; no generated success receipt.

**Verify:** Compare the computed values or written argument with pretrained execution unverified; no generated success receipt.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
