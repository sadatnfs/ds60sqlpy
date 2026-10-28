## A score belongs to a complete system specification

Changing a prompt, decoding temperature, seed, retrieval corpus or answer parser changes the evaluated system. Comparing a carefully tuned candidate to an untuned baseline confounds model capability with the selection procedure. Define the comparison budget and preserve the complete configuration for every generated answer.

A crossed design evaluates each model with each prompt on a common set of tasks and generation seeds. This exposes interactions that an average hides. A prompt that helps one model can hurt another. If the deployment uses only one fixed prompt, an equal-prompt average describes a different target; choose the target and analysis before selecting a favorable cell.

For a descriptive two-factor decomposition of cell means, write

\[
\bar{Y}_{mp}=\mu+\alpha_m+\beta_p+\gamma_{mp},
\]

where model and prompt effects are centered and interaction terms are the remaining differences. This is an algebraic decomposition of the observed table. Statistical inference would also need a sampling model, task-level replication and an appropriate dependence structure. Three seeds do not automatically provide three independent samples of the task population.

## Worked case A: a prompt interaction reverses a comparison

The authored tensor has axes model, prompt and seed. Averaging seeds gives baseline scores 0.9 and 0.6 under the two prompts, while the candidate has 0.8 and 0.9. The candidate loses under the first prompt and wins under the second. Its equal-prompt average exceeds the baseline by 0.1, but this average should not be substituted for either fixed-prompt deployment result.

The decomposition leaves interaction terms of magnitude 0.1. The program verifies that the grand mean, main effects and interaction reconstruct every cell exactly. These values are constructed aggregates for teaching, not measurements from a pretrained model.

{{WORKED_A}}

## Worked case B: selection budgets change the procedure

Selecting the best prompt for each model on this same table produces a tie at 0.9. Comparing only the candidate's selected prompt to the baseline's untuned average would instead report a difference of 0.15. That difference mixes system selection with model identity. A fair comparison can assess the complete prompt-selection procedures, but it needs independent final data after both procedures finish.

{{WORKED_B}}

## Design useful replication

Keep task identity aligned across every model/prompt cell. Record failed generations rather than dropping them from only one cell. If generation seeds are repeated for one task, preserve the task group when estimating uncertainty. Seed variability describes stochastic decoding under that task and configuration; task sampling variability describes generalization across requests or families.

For a larger study, use a hierarchical or crossed model only after identifying which factors are fixed choices and which represent sampled populations. Random effects are not a substitute for enough independent levels. A design with one prompt family and many seeds cannot establish robustness across prompt styles.

## Diagnose and transfer

Inspect the full cell table before interpreting a main effect. Plot paired model differences by prompt and task family, with an explanation of the weighting. A stable overall average can coexist with a severe negative result on an important slice. Conversely, a noisy seed-level fluctuation should not immediately trigger a new model choice without accounting for repeated inspection.

Store prompt text, parser version, model identity, generation settings and actual outputs alongside the score. A seed alone does not guarantee identical execution across library versions or hardware. Reproducibility requires reconstructable artifacts and a stated numerical tolerance where appropriate.

The programs demonstrate a deterministic crossed table and selection arithmetic. They do not estimate sampling variance from real language-model runs. To use this design in practice, obtain representative independent tasks, prespecify the selection budget, and evaluate the selected system on data that did not choose its configuration.
