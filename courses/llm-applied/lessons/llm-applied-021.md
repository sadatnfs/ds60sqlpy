# llm-applied-021: Optional pretrained-model adaptation with pinned offline artifacts

Read the guide, record a prediction, then answer the six cases without opening solutions.

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
   **Expected:** pretrained execution unverified; no generated success receipt.
   **Verify:** Save the reasoning table for exercise 6, including pretrained execution unverified; no generated success receipt.
