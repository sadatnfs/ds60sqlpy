# llm-029: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A scaling law is an empirical relationship measured under a specified family of models, data and training procedures. A small table can suggest a trend, but it cannot identify a universal law or justify extrapolation to frontier systems. Model parameters, training tokens and optimization steps interact through the compute budget. If several change together, a loss difference cannot be attributed to only one. A power-law fit also needs a domain and uncertainty; a straight line through two log-scale points has no independent evidence about curvature. This worksheet uses invented local measurements to practice controlled comparison and to distinguish interpolation from unsupported extrapolation.

**Scaling relationship:** An observed dependence within a declared experimental regime.

**Confounder:** Another changed factor that prevents attributing an effect to one cause.

**Extrapolation:** A prediction outside the range of observed conditions.

## Reading the implementation

Read each row as one experiment with parametersP,tokensD,stepsS,computeC and held-out lossL. Compare rows only after marking which columns differ. A ratio compares multiplicative change. A log-log slope is log(L2/L1)/log(C2/C1), meaningful only for the specified quantities and regime. Do not hide a changed tokenizer or test distribution inside a loss column.

## Exercise 1: Read a controlled comparison

The question is: Inspect rowsA(P1000,D10000,S100,C1,L2.0) andB(P1000,D10000,S200,C2,L1.8). Identify what changed.

The comparison is evidence about additional optimization under this setup. It is not a direct experiment on model size because parameter count stayed fixed.

```text
Run P     D     S   C L
A   1000  10000 100 1 2.0
B   1000  10000 200 2 1.8
Controlled: P,D,evaluation protocol. Changed: S,C.
```

**Expected:** steps and compute doubled; parameters and data fixed; loss fell.2.

**Verify:** Compare the computed values or written argument with steps and compute doubled; parameters and data fixed; loss fell.2.

## Exercise 2: Find a confounded row

The question is: CompareA withC(P2000,D20000,S200,C8,L1.5). Can the gain be assigned only to parameters?

Several plausible mechanisms explain the difference. A larger model, more data and more updates each change the experiment, so the table does not isolate one effect.

```text
A -> C:
P x2; D x2; S x2; C x8; L 2.0 -> 1.5
Attribution to P alone is unsupported.
```

**Expected:** No;P,D,S,C all changed.

**Verify:** Compare the computed values or written argument with No;P,D,S,C all changed.

## Exercise 3: Calculate a local ratio

The question is: CalculateB/A loss ratio and percent decrease relative toA.

A ten-percent relative decrease is different from an absolute decrease of0.2 loss units. Keep the denominator and units explicit.

```text
1.8 / 2.0 = 0.9
(2.0 - 1.8) / 2.0 = 0.10
```

**Expected:** ratio.9; decrease10percent.

**Verify:** Compare the computed values or written argument with ratio.9; decrease10percent.

## Exercise 4: Reject an unsupported forecast

The question is: A reviewer predicts loss.1 at compute1000000 from rowsA,B. Evaluate the claim.

Two nearby measurements do not establish the relationship over six orders of magnitude. A fitted equation can produce a number without making that number evidence-backed.

```text
Observed compute range: [1,2]
Claimed compute: 1000000
Missing: regime checks, more runs, uncertainty, data/optimization policy.
```

**Expected:** unsupported extrapolation far outside compute1..2.

**Verify:** Compare the computed values or written argument with unsupported extrapolation far outside compute1..2.

## Exercise 5: Design a discriminating next run

The question is: Propose a run testing parameter count while holding training data and update policy fixed.

Holding steps fixed does not hold compute fixed when the model grows. The design should state which budget is controlled and measure the resulting other quantity.

```text
Next run: P2000,D10000,S100
Keep tokenizer,split,optimizer policy fixed.
Measure actual C and held-out L; repeat seeds if studying variation.
```

**Expected:** D10000,S100,declared largerP; compute measured separately.

**Verify:** Compare the computed values or written argument with D10000,S100,declared largerP; compute measured separately.

## Exercise 6: Write a bounded conclusion

The question is: SummarizeA/B/C without calling a toy trend a frontier scaling law.

A precise limited conclusion is more useful than a sweeping claim. It identifies both the observation and the experiment still needed to answer the next question.

```text
Within this toy setup, doubling updates from A to B reduced loss from2.0 to1.8.
C has lower loss but changes several factors.
No frontier-performance prediction is supported.
```

**Expected:** conclusion names local fixture and confoundedC.

**Verify:** Compare the computed values or written argument with conclusion names local fixture and confoundedC.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
