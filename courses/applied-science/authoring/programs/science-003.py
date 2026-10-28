"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def bias_adjusted(observed, prevalence_difference, confounder_effect):
    return observed - np.asarray(prevalence_difference) * np.asarray(confounder_effect)


def run_cases():
    observed = 3.0
    prevalence = np.array([0.0, 0.25, 0.5, 0.75])
    strength = np.array([0.0, 2.0, 4.0, 6.0])
    grid = bias_adjusted(observed, prevalence[:, None], strength[None, :])
    assert grid[0, 3] == 3 and grid[2, 3] == 0 and grid[3, 3] < 0
    # Negative control is associated despite a known zero causal effect.
    u = np.array([0.0, 0.0, 1.0, 1.0])
    a = np.array([0.0, 1.0, 1.0, 1.0])
    negative_control = 2 * u
    contrast = float(negative_control[a == 1].mean() - negative_control[a == 0].mean())
    assert contrast > 0
    # Reliability attenuation is separate from unmeasured-confounding bias.
    reliability = 0.5
    true_slope = 2.0
    attenuated = reliability * true_slope
    assert attenuated == 1
    return dict(
        adjusted_grid=grid.tolist(),
        negative_control_difference=contrast,
        attenuated_slope=attenuated,
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    prevalence = [0, 0.25, 0.5, 0.75]
    strength = [0, 2, 4, 6]
    z = evidence["adjusted_grid"]
    rows = [[p, g, z[i][j]] for i, p in enumerate(prevalence) for j, g in enumerate(strength)]
    fig = go.Figure(go.Heatmap(x=strength, y=prevalence, z=z, colorscale="RdBu", zmid=0))
    fig.update_layout(
        title="Sensitivity under an additive bias scenario",
        xaxis_title="Confounder outcome effect",
        yaxis_title="Prevalence difference",
        meta=dict(
            description="Adjusted effects from 3 down to -1.5 under a stated additive bias model; these are scenarios, not estimated hidden confounding.",
            table=dict(
                columns=["Prevalence difference", "Outcome effect", "Adjusted contrast"], rows=rows
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-003 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
