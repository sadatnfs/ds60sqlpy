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

# Task 1: Calculate candidate minus baseline under each prompt.
# Task 2: Recombine grand mean, model, prompt and interaction terms.
# Task 3: Put all deployment weight on the first prompt.
# Task 4: Select the best prompt separately for both models on development data.
# Task 5: Compute variance for baseline/prompt 1 across its three authored seeds.
# Task 6: Provide only a two-dimensional matrix to the helper.

# Implement your six changes below.
