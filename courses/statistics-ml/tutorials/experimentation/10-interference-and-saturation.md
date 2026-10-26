# Direct effects, spillovers and full-rollout effects

Tutorial ID: `statistics-exp-010`. Prerequisites: `statistics-015`, `statistics-013`, `statistics-exp-001`. Complete example: [experiment_10.py](examples/experiment_10.py).

## Expand the potential outcome

One user's assignment can change another user's experience. Sharing, competition and common resources break the assumption that \(Y_i\) depends only on \(A_i\). An exposure mapping summarizes the relevant assignments of neighbors. It is a scientific modeling choice, not a trick that automatically removes interference.

Consider four users arranged in two disconnected pairs. Each has one neighbor. Let \(G_i\) be that neighbor's assignment and define

\[
Y_i(a,g)=b_i+2a+3g.
\]

The direct effect at fixed neighbor assignment is two. The spillover from changing only the neighbor is three. Moving from nobody treated to everyone treated changes each outcome by five. An individual mixed experiment's direct contrast and a full-rollout contrast therefore answer different questions even in this simple world.

## Enumerate the randomization space

Independent Bernoulli(.5) assignment gives 16 possible assignments for four users. Each user's joint exposure \((A_i,G_i)\) has probability .25 for each of its four possibilities. For an exposure cell \((a,g)\), the Horvitz-Thompson mean is

\[
\widehat\mu(a,g)=\frac1{4}\sum_i
\frac{\mathbf1\{A_i=a,G_i=g\}Y_i}{.25}.
\]

Some realized assignments contain no users in a particular cell, producing a zero contribution in that estimator, not evidence that the underlying potential-outcome mean is zero. Averaging over all assignments recovers the target cell mean. The code enumerates the full design and verifies that mean direct, spillover and rollout estimates equal two, three and five respectively.

This is a design-unbiasedness demonstration with known potential outcomes. It is not a variance estimator or evidence that four observed users would support a precise real result. Joint exposure probabilities, which matter for variance, become more complicated in larger networks.

## Change the assignment unit

Randomize each whole pair instead. There are only four cluster assignments, and neighbors always receive the same treatment. A policy-effect estimator based on cluster assignment now averages to five, the all-treated versus all-control effect. It cannot separately identify the direct effect at an untreated-neighbor exposure because the design never produces that exposure.

The second case shows why changing randomization level changes both information and identifiable questions. A cluster design can reduce contamination but does not create information about exposure combinations it excludes. Two clusters are far too few for routine large-cluster standard errors.

## Transfer to a marketplace

If treated buyers obtain scarce inventory that controls would otherwise receive, the mixed contrast may include displacement. Full rollout removes that same comparison and may change supply or pricing. Market clusters, two-sided designs, switchbacks or randomized saturation can target a better-defined policy, but each needs explicit exposure and boundary assumptions.

**Answered discussion: Can we discover the correct network solely from observed similarity?** No. Similar users may connect because of shared causes or selection. Missing edges can hide spillovers; observed edges can be irrelevant to the treatment. Explain which pathway the exposure mapping represents and test design sensitivity to plausible alternatives.

Continue to [switchbacks](11-switchbacks-and-carryover.md). Primary reference: [multilevel designs for spillover effects](https://isps.yale.edu/resource/detecting-spillover-effects-design-and-analysis-of-multilevel-experiments). Related chapter: [networks](../../chapters/31-network-and-graph-analysis.md).
