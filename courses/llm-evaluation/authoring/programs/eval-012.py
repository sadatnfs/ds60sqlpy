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


# === EXAMPLE A ===
def worked_a():
    cells, grand, model, prompt, interaction = decomposition(fixture())
    np.testing.assert_allclose(cells, [[0.9, 0.6], [0.8, 0.9]])
    np.testing.assert_allclose(cells, grand + model[:, None] + prompt[None, :] + interaction)
    np.testing.assert_allclose(interaction, [[0.1, -0.1], [-0.1, 0.1]], atol=1e-12)
    np.testing.assert_allclose(cells[1] - cells[0], [-0.1, 0.3])
    print("Model by prompt:", cells.tolist(), "interaction:", interaction.tolist())


# === EXAMPLE B ===
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


# === EXERCISES ===
def exercise_checks():
    cells, grand, model, prompt, interaction = decomposition(fixture())
    assert np.isclose((cells[1] - cells[0]).mean(), 0.1)
    assert np.isclose(model.sum(), 0) and np.isclose(prompt.sum(), 0)
    np.testing.assert_allclose(interaction.sum(0), 0, atol=1e-12)
    np.testing.assert_allclose(interaction.sum(1), 0, atol=1e-12)
    assert np.isclose(fixture()[0, 0].var(ddof=1), 0.01)
    try:
        decomposition([[1, 2]])
    except ValueError:
        pass
    else:
        raise AssertionError("Missing tensor axis accepted")


# === MAIN ===
def main():
    worked_a()
    worked_b()
    exercise_checks()
    print("eval-012: all reference checks passed")


if __name__ == "__main__":
    main()
