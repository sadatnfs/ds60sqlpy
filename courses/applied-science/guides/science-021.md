# science-021: Spatial dependence, permutation reference sets and blocked validation

Tutorial mode. Stage: advanced. Direct prerequisites: `statistics-030`.

## Location creates dependence and validation boundaries

Nearby observations can share weather, infrastructure, measurement systems, populations or latent processes. Randomly splitting rows can place almost identical neighboring information in training and evaluation, producing an optimistic estimate for a deployment that must predict a new region.

A spatial analysis starts by defining the unit, coordinate system, distance or adjacency relation and outcome scale. Spatial weights \(W_{ij}\) encode a particular relationship, not an intrinsic property of the data. Contiguity, distance thresholds and nearest-neighbor graphs can imply different scientific questions.

For centered values \(z_i\), a common global dependence summary is Moran's statistic:

\[
I=\frac{n}{\sum_{ij}W_{ij}}
\frac{\sum_{ij}W_{ij}z_iz_j}{\sum_i z_i^2}.
\]

This tutorial uses a simple chain graph with symmetric adjacency and no diagonal self-links. The function rejects a constant map because its standardized denominator is zero. Quietly returning zero would confuse an undefined statistic with evidence of no dependence.

## Worked case 1: distinguish clustering from alternation

The map 0,0,0,1,1,1 groups similar values together. The alternating map 0,1,0,1,0,1 places unlike values next to each other. The first has positive Moran's statistic and the second has negative statistic under the specified graph. The code checks the signs and calculates the exact values.

A permutation reference repeatedly rearranges the values across the same locations. The Monte Carlo upper-tail value includes the observed arrangement through a plus-one correction, so it cannot report a zero probability from a finite number of permutations. The interpretation depends on exchangeability under the permutation null. Arbitrary rearrangement may be inappropriate when the design, covariates or observation process impose additional structure.

A global statistic can conceal local patterns, and a positive spatial association does not identify a causal mechanism. It may reflect an omitted spatial covariate, a sampling artifact or a shared measurement process. Local analyses introduce additional multiplicity and interpretation issues. The goal is to diagnose structure and choose suitable models and validation, not to convert every spatial pattern into a causal story.

## Worked case 2: compare row splits with spatial blocks

The chain has six locations. A random-style training set containing alternating locations places a train/test boundary on every neighboring edge. A contiguous training block creates only one such boundary. The program counts those crossing edges directly.

This does not prove that contiguous blocks are always the correct validation design. The split must match the intended deployment. Predicting missing values within a densely observed region differs from predicting an entirely new region. Spatial buffers, grouped folds and time-space splits address different forms of dependence and extrapolation.

Block size also matters. Tiny blocks can retain strong dependence across fold boundaries. Very large blocks can leave few independent evaluation units or create an intentionally difficult extrapolation problem. Report the split geometry and perform sensitivity analysis to scientifically meaningful distances rather than choosing the split that yields the preferred score.

## Review the measurement and aggregation process

Area-level observations may aggregate heterogeneous individuals. A relationship among area averages need not hold at the individual level. Changes in boundaries or aggregation scale can alter observed associations, which is one reason to retain the geographic definitions and population denominators used by each record.

Distance calculations require compatible coordinate units. Euclidean distance on arbitrary longitude/latitude numbers can be inappropriate over large regions, and a graph built from coordinates in meters behaves differently from one built in degrees. Geometry should be validated before it becomes a predictor or a weight matrix.

Spatial modeling can use correlated random effects, Gaussian processes, structured smoothing or other mechanisms, but fitting a more elaborate model does not repair an invalid evaluation split automatically. Assess calibration, error and uncertainty for the target locations and horizons. A held-out region supplies different evidence from another randomly omitted row inside a known cluster.

## Answered scientific discussion

**Does a significant permutation result justify adding a spatial term?** It supports evidence against the specified exchangeability null. A model term still needs a scientific interpretation and evaluation of whether it improves the intended prediction or inference.

**Why does the program retain the graph explicitly?** It makes the dependence assumption inspectable. Reproducing only the scalar statistic would hide which observations were considered neighbors and could make a later result impossible to interpret.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json

import numpy as np


def moran(values, weights):
    z = np.asarray(values, float)
    z = z - z.mean()
    w = np.asarray(weights, float)
    if np.isclose(z @ z, 0):
        raise ValueError("A constant map has no standardized spatial statistic")
    return float(len(z) / w.sum() * (z @ w @ z) / (z @ z))


def run_cases():
    w = np.zeros((6, 6))
    for i in range(5):
        w[i, i + 1] = w[i + 1, i] = 1
    clustered = moran([0, 0, 0, 1, 1, 1], w)
    alternating = moran([0, 1, 0, 1, 0, 1], w)
    assert clustered > 0 and alternating < 0
    rng = np.random.default_rng(21)
    permuted = [moran(rng.permutation([0, 0, 0, 1, 1, 1]), w) for _ in range(199)]
    p = (1 + sum(v >= clustered for v in permuted)) / 200
    assert 0 < p <= 1
    # Random row folds put neighboring locations in both sets; block folds do not.
    random_train = {0, 2, 4}
    block_train = {0, 1, 2}
    crossings = lambda train: sum(
        (i in train) != (j in train) for i in range(6) for j in range(i + 1, 6) if w[i, j]
    )
    assert crossings(random_train) > crossings(block_train)
    return dict(
        clustered_I=clustered,
        alternating_I=alternating,
        permutation_p=p,
        random_boundary_edges=crossings(random_train),
        blocked_boundary_edges=crossings(block_train),
    )


def render_figure(evidence):
    import plotly.graph_objects as go

    positions = list(range(6))
    values = [0, 0, 0, 1, 1, 1]
    fig = go.Figure(go.Scatter(x=positions, y=values, mode="lines+markers"))
    fig.update_layout(
        title="Values on an adjacency chain",
        xaxis_title="Graph position, not geographic distance",
        yaxis_title="Synthetic value",
        meta=dict(
            description="Three zeros followed by three ones on a six-node chain. Moran I is positive under nearest-neighbor adjacency.",
            table=dict(
                columns=["Graph position", "Value"],
                rows=[[a, b] for a, b in zip(positions, values, strict=True)],
            ),
        ),
    )
    fig.show()


if __name__ == "__main__":
    evidence = run_cases()
    print("science-021 complete")
    print(json.dumps(evidence, sort_keys=True, allow_nan=False))
    render_figure(evidence)
```

## Primary references

- [PySAL ESDA Moran documentation](https://pysal.org/esda/stable/generated/esda.Moran.html)
