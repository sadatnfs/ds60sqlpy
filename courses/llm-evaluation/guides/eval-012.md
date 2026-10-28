# eval-012: Prompt, model and seed effects

## Starting point and outcome

Intermediate; approximately 120 minutes. Direct prerequisites: `eval-006`, `eval-011`.

Analyze a crossed prompt/model/seed experiment and distinguish decoding variability from independent task evidence.

## Classroom execution

Choose **LLM evaluation and alignment** in `/classroom`, open `eval-012`, and use its `python-core` profile. A Run starts a fresh Python process. Both worked programs below include their own setup and can be copied in full. Save your draft first. The examples use small authored fixtures and explicit numerical checks. Process success establishes those checks, not population validity, safety certification or natural-language competence. Code and notes persist; temporary program files do not. No network call or model download is needed.

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

```python
import numpy as np


def decomposition(scores):
    values = np.asarray(scores, float)
    if values.ndim != 3 or min(values.shape) < 1 or not np.isfinite(values).all():
        raise ValueError("Finite model/prompt/seed tensor required")
    cells = values.mean(axis=2)
    grand = float(cells.mean())
    model = cells.mean(axis=1) - grand
    prompt = cells.mean(axis=0) - grand
    interaction = cells - grand - model[:, None] - prompt[None, :]
    return cells, grand, model, prompt, interaction


def fixture():
    return np.array([[[0.8, 0.9, 1.0], [0.5, 0.6, 0.7]], [[0.7, 0.8, 0.9], [0.8, 0.9, 1.0]]])


def worked_a():
    cells, grand, model, prompt, interaction = decomposition(fixture())
    np.testing.assert_allclose(cells, [[0.9, 0.6], [0.8, 0.9]])
    np.testing.assert_allclose(cells, grand + model[:, None] + prompt[None, :] + interaction)
    np.testing.assert_allclose(interaction, [[0.1, -0.1], [-0.1, 0.1]], atol=1e-12)
    np.testing.assert_allclose(cells[1] - cells[0], [-0.1, 0.3])
    print("Model by prompt:", cells.tolist(), "interaction:", interaction.tolist())


worked_a()
```

## Worked case B: selection budgets change the procedure

Selecting the best prompt for each model on this same table produces a tie at 0.9. Comparing only the candidate's selected prompt to the baseline's untuned average would instead report a difference of 0.15. That difference mixes system selection with model identity. A fair comparison can assess the complete prompt-selection procedures, but it needs independent final data after both procedures finish.

```python
import numpy as np


def decomposition(scores):
    values = np.asarray(scores, float)
    if values.ndim != 3 or min(values.shape) < 1 or not np.isfinite(values).all():
        raise ValueError("Finite model/prompt/seed tensor required")
    cells = values.mean(axis=2)
    grand = float(cells.mean())
    model = cells.mean(axis=1) - grand
    prompt = cells.mean(axis=0) - grand
    interaction = cells - grand - model[:, None] - prompt[None, :]
    return cells, grand, model, prompt, interaction


def fixture():
    return np.array([[[0.8, 0.9, 1.0], [0.5, 0.6, 0.7]], [[0.7, 0.8, 0.9], [0.8, 0.9, 1.0]]])


def worked_b():
    cells, *_ = decomposition(fixture())
    fair_development = cells.max(axis=1)
    unfair_difference = cells[1].max() - cells[0].mean()
    np.testing.assert_allclose(fair_development, [0.9, 0.9])
    assert np.isclose(unfair_difference, 0.15)
    print(
        "Both selected on development:",
        fair_development.tolist(),
        "mixed-budget difference:",
        unfair_difference,
    )


worked_b()
```

## Design useful replication

Keep task identity aligned across every model/prompt cell. Record failed generations rather than dropping them from only one cell. If generation seeds are repeated for one task, preserve the task group when estimating uncertainty. Seed variability describes stochastic decoding under that task and configuration; task sampling variability describes generalization across requests or families.

For a larger study, use a hierarchical or crossed model only after identifying which factors are fixed choices and which represent sampled populations. Random effects are not a substitute for enough independent levels. A design with one prompt family and many seeds cannot establish robustness across prompt styles.

## Diagnose and transfer

Inspect the full cell table before interpreting a main effect. Plot paired model differences by prompt and task family, with an explanation of the weighting. A stable overall average can coexist with a severe negative result on an important slice. Conversely, a noisy seed-level fluctuation should not immediately trigger a new model choice without accounting for repeated inspection.

Store prompt text, parser version, model identity, generation settings and actual outputs alongside the score. A seed alone does not guarantee identical execution across library versions or hardware. Reproducibility requires reconstructable artifacts and a stated numerical tolerance where appropriate.

The programs demonstrate a deterministic crossed table and selection arithmetic. They do not estimate sampling variance from real language-model runs. To use this design in practice, obtain representative independent tasks, prespecify the selection budget, and evaluate the selected system on data that did not choose its configuration.


## Six investigations

### 1. Inspect each prompt

Calculate candidate minus baseline under each prompt.

**Expected:** The differences are -0.1 and +0.3.

**Hint:** Average seeds before comparing aligned cells.

### 2. Check reconstruction

Recombine grand mean, model, prompt and interaction terms.

**Expected:** Every observed cell is recovered within floating tolerance.

**Hint:** Broadcast model effects down rows and prompt effects across columns.

### 3. Change the prompt target

Put all deployment weight on the first prompt.

**Expected:** The candidate difference becomes-0.1.

**Hint:** The target distribution is part of the estimand.

### 4. Equalize selection budgets

Select the best prompt separately for both models on development data.

**Expected:** Both selected development scores are 0.9.

**Hint:** Apply the same procedure to both candidates.

### 5. Count seed replication

Compute variance for baseline/prompt 1 across its three authored seeds.

**Expected:** The sample variance is 0.01.

**Hint:** Use `ddof=1` for this descriptive sample calculation.

### 6. Validate axes

Provide only a two-dimensional matrix to the helper.

**Expected:** The tensor contract rejects it.

**Hint:** Every dimension must retain its scientific meaning.

## Primary references

- [Experimental design foundations](../../../courses/statistics-ml/chapters/13-classical-experimental-design.md)
- [HELM system configuration and evaluation](https://arxiv.org/abs/2211.09110)

## Study companion

Use the repository learning-companion skill with this lesson ID and your own source/output. Ask for clarification of the estimand, probability distribution, data split or gradient before a hint. Keep claims about the authored fixture separate from claims requiring real population or model evidence.
