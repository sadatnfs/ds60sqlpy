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

## Key terms

- **Spatial weights:** The matrix W encoding a declared adjacency or distance relation between locations.
- **Moran's I:** A global summary of spatial dependence comparing centered values with their weighted neighbors.
- **Permutation reference set:** Rearrangements of the observed values over the same locations, used to compute a p-value under exchangeability.
- **Blocked spatial validation:** Holding out contiguous regions so nearby correlated observations do not appear in both training and evaluation.

## Worked case 1: distinguish clustering from alternation

The map 0,0,0,1,1,1 groups similar values together. The alternating map 0,1,0,1,0,1 places unlike values next to each other. The first has positive Moran's statistic and the second has negative statistic under the specified graph. The code checks the signs and calculates the exact values.

A permutation reference rearranges the values across the same locations. With six locations and three ones there are only \(\binom{6}{3}=20\) distinct arrangements, so the program enumerates all of them instead of sampling. Two arrangements, the observed map and its mirror image, reach the observed statistic of 0.6, so the exact one-sided p-value is \(2/20=0.10\). For larger maps the reference set is too large to enumerate, and a Monte Carlo estimate with \(B\) random permutations uses \((1+\#\{I_b\ge I_{\text{obs}}\})/(B+1)\), which counts the observed arrangement and therefore cannot report a zero probability. The interpretation depends on exchangeability under the permutation null. Arbitrary rearrangement may be inappropriate when the design, covariates or observation process impose additional structure.

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

## Worked example: Moran's I on a 3 by 3 grid with rook neighbors

```python
from itertools import combinations
import numpy as np

coords = [(r, c) for r in range(3) for c in range(3)]
W = np.array(
    [[1.0 if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 else 0.0 for b in coords] for a in coords]
)


def moran(v):
    z = np.asarray(v, float) - np.mean(v)
    return len(z) / W.sum() * (z @ W @ z) / (z @ z)


stripe = [1, 1, 1, 0, 0, 0, 0, 0, 1]
checker = [1, 0, 1, 0, 1, 0, 1, 0, 1]
print(f"neighbor pairs {int(W.sum() / 2)}")
print(f"left block of four I = {moran([1, 1, 0, 1, 1, 0, 0, 0, 0]):.4f}")
print(f"checkerboard I = {moran(checker):.4f}, expected under randomness {-1 / 8:.4f}")
ref = []
for ones in combinations(range(9), 4):
    v = np.zeros(9)
    v[list(ones)] = 1
    ref.append(moran(v))
obs = moran([1, 1, 0, 1, 1, 0, 0, 0, 0])
print(f"{len(ref)} arrangements; exact p for block = {np.mean(np.array(ref) >= obs - 1e-12):.4f}")
```

Observed output:

```text
neighbor pairs 12
left block of four I = 0.3500
checkerboard I = -1.0000, expected under randomness -0.1250
126 arrangements; exact p for block = 0.0317
```

On a 3 by 3 grid with rook adjacency there are 12 neighbor pairs, so \(\sum W=24\). Putting four ones in the upper-left 2 by 2 block gives \(I=0.35\): neighbors tend to share values. The checkerboard reaches \(I=-1\) because every neighbor pair has opposite values, the extreme of negative autocorrelation. Neither should be compared with zero. Under random arrangement the expected value is \(-1/(n-1)=-0.125\), so a modest positive \(I\) is further from randomness than it looks. The permutation reference set enumerates all \(\binom{9}{4}=126\) ways to place four ones. Exactly four arrangements, the four 2 by 2 blocks that each contain the center cell, reach 0.35, giving an exact p-value of \(4/126=0.0317\). That p-value is conditional on the neighbor definition: switching to queen adjacency, which adds diagonal pairs, changes both \(W\) and the reference distribution. The same dependence that makes \(I\) positive also inflates random-split validation scores, because neighboring cells in training and test share information.

## Complete reproducible program

Run the complete program in the classroom's declared prepared profile. Every run starts a fresh process with tiny offline synthetic data. This is a worked tutorial, with no exam or hidden solution. Runtime: `python-core`.

```python
"""Complete bounded synthetic scientific investigation; no external data."""

from __future__ import annotations

import json
from itertools import combinations

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
    # Six locations and three ones allow only C(6, 3) = 20 arrangements: enumerate them all.
    reference = []
    for ones in combinations(range(6), 3):
        values = np.zeros(6)
        values[list(ones)] = 1
        reference.append(moran(values, w))
    p = float(np.mean(np.array(reference) >= clustered - 1e-12))
    assert len(reference) == 20 and np.isclose(p, 0.1)  # 2 of 20 arrangements
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
        reference_arrangements=len(reference),
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
