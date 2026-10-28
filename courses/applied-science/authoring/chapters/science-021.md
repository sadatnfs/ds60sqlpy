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
