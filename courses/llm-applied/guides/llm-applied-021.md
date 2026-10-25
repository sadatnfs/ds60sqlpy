# llm-applied-021: Optional pretrained-model adaptation with pinned offline artifacts

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-020`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A pretrained-model experiment connects the earlier concepts to real artifacts, tokenizers and training software. This chapter follows the qualified optional recipe from preparation through reload and generation, explaining exactly what its successes and its observed failure establish.

## Purpose and mental model

A realistic pretrained-model adaptation recipe introduces dependencies that the tiny offline exercises deliberately avoid: model weights, tokenizer files, chat templates, library versions, artifact licenses and larger resource needs. These are part of the experiment, not setup trivia. A model name pointing to a moving branch is not a reproducible identity. Pin an exact repository revision and record hashes of the downloaded files. Keep the acquisition step separate from local training so an offline run cannot silently fetch missing assets.

The optional recipe targetsHuggingFaceTB/SmolLM2-135M-Instruct at revision 12fd25f77366fa6b3b4b768ec3050bf629380bac, whose model card was checked asApache-2.0 during authoring. This is a small pretrained model for a bounded demonstration, not a recommended production assistant. The recipe pins direct package versions, uses a literal local prompt-completion dataset, checks chat-template prefix alignment and answer-only masks, and runs at most 10CPU updates. The optional recipe has separate bounded Linux arm64 execution evidence for ten full-SFT and LoRA updates, while its generation probe produced an incorrect formula despite evidence. Learners must still explicitly prepare their own dependencies and assets; mechanics success does not establish subject expertise. No default lesson downloads a model or calls a paid service.

## Move from literal tokens to a model with a prior history

The tiny decoder began with randomly initialized weights and an authored vocabulary. A pretrained model arrives with a tokenizer, architecture, learned parameters, chat formatting and a history of training that this course does not reproduce. Those artifacts are part of the experiment's starting state. A model name alone is too imprecise to identify that state when a repository branch can change.

The optional recipe pins one SmolLM2-135M-Instruct revision and verifies the acquired local files. It also uses a separately prepared dependency environment with platform-specific locks. This makes the transition to a real model explicit without changing the ordinary classroom's offline fixtures. Reading the chapter does not acquire weights or start training; the separate recipe documents those deliberate actions.

The qualified run is evidence for a bounded path through that particular environment. Its source, manifests and receipts should be read together. A successful dependency resolution on another architecture is useful preparation, but it is not an executed result on that architecture. Likewise, a matching file hash proves identity relative to the recorded artifact, not answer quality.

## Inspect what the small dataset is actually teaching

The four training examples ask for only the assignment unit. They map statements about randomized accounts, racks and hosts to singular labels, and map an unspecified assignment description to unknown. The evaluation example uses clusters. The family labels are disjoint, but all examples share a narrow extraction task and a closely related prompt form.

That structure is valuable for testing formatting, masks and actual updates. It is much weaker evidence for a broad subject assistant. A model can improve this task by learning how to emit the requested short label without learning a new statistical concept or a general policy for causal interpretation. The held-out cluster label tests one small transfer beyond the training entities, not independent coverage of business questions.

A domain dataset intended to teach evidence use would need a broader range of supported and unsupported requests, units, source conflicts and counterfactual inputs. The earlier data-design chapter explains how to construct those cases. Scaling the number of optimizer steps on these four records cannot manufacture the missing diversity.

## Verify the model's actual token interface

The recipe renders the prompt with its generation marker and renders the prompt plus completion as a full conversation. It requires the prompt token IDs to be an exact prefix of the full sequence. That check establishes the boundary for this tokenizer/template pair. It is more reliable than inferring the boundary from character length or assuming that every chat template uses the same markers.

The trainer receives completion-only supervision and no packing in the documented recipe. Before training, the script inspects processed examples and an actual collated batch. Prompt labels are ignored, active labels match the corresponding input IDs, and the causal model performs the shift internally. This differs from the earlier manual helper that explicitly created shifted inputs and labels. Applying both shifts would optimize the wrong prediction events.

The length limit is also an admission rule. Overlong records are rejected rather than silently truncated into partial answers. That policy trades dataset coverage for a clear target contract. Another application might use a reviewed truncation or segmentation policy, but it would need to inspect which answer and stop tokens survive.

## Separate execution mechanics from the model's usefulness

The documented Linux arm64 recipe completed ten full-SFT updates and ten LoRA updates. The full path had 134515008 trainable parameters; the adapter path had 230400. Both produced saved artifacts and evaluation measurements. Those observations establish that the intended training and artifact operations executed in that environment.

The held-out token losses changed substantially differently for the two paths. The full model's recorded loss fell from 6.721148 to 0.008058, while the LoRA path's fell to 6.474194. The narrow dataset and single evaluation record are essential context for those numbers. They do not establish a general ranking of adaptation methods, nor do they measure supported-answer quality on a representative domain workload.

Reload adds another evidence tier. A saved adapter must be combined with the intended base and tokenizer under the recorded configuration. The recipe performed that reload and generated a response offline. Two same-environment LoRA runs also matched artifact hashes and evaluation loss after the seed was placed before adapter construction. That is a concrete repeatability result under the tested conditions, not a promise of bitwise equivalence across every platform.

## Learn from the wrong formula that the model generated

The generation probe supplied the correct conversion definition as evidence. The saved adapter nevertheless described eligible visits divided by eligible visits, which is the wrong formula. The answer was fluent enough to appear plausible while failing the central domain claim. Its supplied evidence IDs also did not establish validated claim-level citations.

This result connects several earlier chapters. Retrieval can supply the right text without guaranteeing that generation uses it. A completed optimizer run can improve a narrow token objective without improving an unrelated analytical task. Saving and reloading an adapter proves an artifact path, while the returned answer still needs semantic and numerical evaluation.

The correct response to that failure is to preserve the generated artifact and classify the error. It may motivate a better prompt, a more appropriate dataset, a constrained calculation interface, or an evidence-use evaluation. It does not justify rewriting the expected answer after the fact or describing the model as a domain expert because training completed successfully.

## Reproduce a bounded experiment before expanding it

A learner reproducing the recipe should identify the exact environment, asset snapshot, dataset, masks, optimizer configuration and output directory, then retain the resulting receipt. Existing artifacts should not be silently overwritten by a retry. A failed preparation or training step remains a failed step until repaired and rerun; a success receipt should follow actual execution.

The [optional recipe](../fixtures/pretrained/README.md) contains the concrete Docker-first commands and current execution record. They are separate from the written cases below. The next chapter focuses on a complementary way to improve the Methods Desk: let a model propose a bounded analytical operation, while trusted code computes and records the result that the final explanation must use.

## Design decisions and when to use this method

Use the optional recipe only after the default tiny-model lessons make the data, mask and optimization mechanics understandable. Prepare a separate environment so experimentation does not silently replace the classroom runtime. The supplied recipe includes complete platform-specific dependency locks with hashes; changing those locks requires new environment preparation and qualification. Record Python, OS, architecture, Torch and accelerator information with the run.

Do not assume a chat template supports assistant-only masking merely because the tokenizer has a template. The supplied recipe uses prompt/completion boundaries and verifies them. Do not enabletrust_remote_code or load arbitrary pickled checkpoints to make an unfamiliar model work. Do not treat a model card license note as a blanket approval for every dataset or deployment. The optional inference script loads only local base and adapter artifacts and still requires the same grounded-output and access controls as the default assistant baseline.

Read the optional recipe as a staged experiment: prepare a locked environment, acquire one pinned artifact deliberately, verify local assets, inspect the real masks, train under a fixed budget, reload and evaluate actual outputs. Each stage earns a different conclusion. A fresh learner run must produce its own artifacts even when a maintainer run has already qualified the mechanism.

Keep the default chapter as a written review. The separate pretrained fixture has already run under the documented Linux arm64 environment, but reading the cases does not acquire assets or perform training. Its source and runtime remain governed by the dedicated recipe rather than the tiny-decoder classroom profile.

## Vocabulary and concepts

**Pinned revision:** An immutable model-repository commit identifying exact source artifacts.

**Offline asset manifest:** Local filenames,hashes,license note and revision used by a run.

**Chat-template alignment:** Agreement between rendered prompt prefix and full conversation tokens.

**Completion-only loss:** Supervision restricted to completion targets under the trainer contract.

## How to run this lesson

Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required.

Read the three worked cases in order and write the assumptions, intermediate reasoning and conclusion for each one. These are text cases, not programs to execute. Compare your written interpretation with the stated expected observations, then answer the six exercises in your saved worksheet. A correct argument must state its evidence boundary; source presence does not establish a model run. The optional pretrained recipe is a separate, deliberately prepared execution path with its own artifacts and receipts. Reading this chapter does not run or qualify that recipe.

## Syntax anatomy and reasoning sequence

The prepared scripts live underfixtures/pretrained. prepare_assets.py requires an explicit network acknowledgement and downloads only the pinned model snapshot into a new learner-owned directory. It records SHA256 hashes. train_local.py useslocal_files_only=True andtrust_remote_code=False, checks the manifest and refuses a nonempty output directory. TRL SFTTrainer receives conversational prompt/completion records withcompletion_only_loss=True. Before training, the script inspects tokenized examples and a collated batch to ensure prompt labels are ignored and answer labels remain active. The model itself performs the causal label shift; do not shift labels twice.

## Read the qualified recipe as several independent evidence tiers

The pinned revision identifies a particular repository state; the local manifest identifies the acquired files and their hashes. The lock identifies resolved dependency artifacts for a platform. The image identifies the executable environment. None of these identities alone establishes that training happened. A run receipt and saved artifact provide that next tier, followed by separate reload and task-quality observations.

The existing recipe record reports 13 acquired files and actual 10-update CPU runs for both full SFT and LoRA. Full SFT has 134515008 trainable parameters; the rank-four q_proj/v_proj adapter path has 230400. The recorded held-out losses changed from 6.721148 to 0.008058 for full SFT and from 6.721148 to 6.474194 for LoRA. These are observations from the qualified recipe, not reruns performed by this prose review. [Optional recipe evidence and workflow](../fixtures/pretrained/README.md).

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

**Expected:** exact 40-character revision and Apache-2.0 card note are present.

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

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: exact 40-character revision and Apache-2.0 card note are present. this hypothetical learner run remains unverified; no generated success receipt. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Inspect the pinned artifact contract.** Read the supplied model manifest and identify model ID, revision and license note before any download.
   **Expected:** exact 40-character revision and Apache-2.0 card note are present.
   **Verify:** Save the reasoning table for exercise 1, including exact 40-character revision and Apache-2.0 card note are present.

2. **Separate acquisition from execution.** Trace the optional workflow from dependency preparation to snapshot acquisition to offline training.
   **Expected:** training requires existing local assets and never falls back to a remote model ID.
   **Verify:** Save the reasoning table for exercise 2, including training requires existing local assets and never falls back to a remote model ID.

3. **Verify chat-template boundaries.** For each local prompt/completion record, compare full conversation token IDs with the prompt rendered usingadd_generation_prompt=True.
   **Expected:** prompt IDs are an exact prefix; at least one completion token remains.
   **Verify:** Save the reasoning table for exercise 3, including prompt IDs are an exact prefix; at least one completion token remains.

4. **Inspect trainer labels before training.** Read one collated batch and compare labels with the prompt/completion boundary.
   **Expected:** prompt labels-100; active completion labels match their input token IDs.
   **Verify:** Save the reasoning table for exercise 4, including prompt labels-100; active completion labels match their input token IDs.

5. **Compare full and adapter configuration.** Inspectmodefull versusmodelora, rank 4, alpha 8, target modulesq_proj/v_proj, with the same local data and 10-step cap.
   **Expected:** mode and trainable-parameter count recorded; no automatic quality winner.
   **Verify:** Save the reasoning table for exercise 5, including mode and trainable-parameter count recorded; no automatic quality winner.

6. **Distinguish an unexecuted learner scenario.** For a hypothetical new learner who has only reviewed scripts, write the status without overwriting the separately qualified maintainer recipe.
   **Expected:** this hypothetical learner run remains unverified; no generated success receipt.
   **Verify:** Save the reasoning table for exercise 6, including this hypothetical learner run remains unverified; no generated success receipt.

## Common pitfalls and diagnosis

If training cannot find an asset, inspect the local manifest and exact directory rather than permitting an implicit download. If losses are unexpectedly low, inspect target leakage, family/task overlap and mask boundaries. If saved-adapter predictions differ across repeated runs, check seed placement before construction, artifact identity and decoding settings.

If the generated answer is wrong despite supplied evidence, score that failure explicitly. Do not relabel successful optimization as grounded-answer acceptance. If an unexecuted learner scenario is reported, keep it conditional on that learner's state rather than overwriting the maintainer recipe's observed execution record.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Pinned revision, Offline asset manifest, Chat-template alignment using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-020` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [TRL SFTTrainer 0.24.0](https://huggingface.co/docs/trl/v0.24.0/en/sft_trainer), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Complete optional scripts and setup

Read the [pretrained recipe](../fixtures/pretrained/README.md) for pinned dependencies, model identity, explicit acquisition, local hash verification, mask checks, bounded training, local inference, resource estimates and a manual container recipe with persistent mounted artifacts. See the recipe execution record for the bounded training/reload results and the observed generation-quality failure. A new learner run needs its own receipt.

## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-021, Optional pretrained-model adaptation with pinned offline artifacts.
Read courses/llm-applied/guides/llm-applied-021.md and courses/llm-applied/lessons/llm-applied-021.md. Direct prerequisites: `llm-applied-020`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
