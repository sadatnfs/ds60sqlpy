# llm-029: explanatory solutions

Read these scaling laws and the limits of a toy experiment answers after attempting *Read a longer training run* through *Write a bounded conclusion*, or after asking for a reveal. They reuse the guide's literals, so a mismatch in *Calculate a local ratio* points to one step. `llm-029_solution.py` holds the assertions; this page explains how they test scaling relationship. Then try *Write a bounded conclusion* on a fresh input you chose before looking.

## Mechanism review

A scaling law is an empirical relationship measured under a specified family of models, data and training procedures. A small table can suggest a trend, but it cannot identify a universal law or justify extrapolation to frontier systems. Model parameters, training tokens and optimization steps interact through the compute budget. If several change together, a loss difference cannot be attributed to only one. A power-law fit also needs a domain and uncertainty; a straight line through two log-scale points has no independent evidence about curvature. This worksheet uses invented local measurements to practice controlled comparison and to distinguish interpolation from unsupported extrapolation.

**Scaling relationship:** An observed dependence within a declared experimental regime.

**Confounder:** Another changed factor that prevents attributing an effect to one cause.

**Extrapolation:** A prediction outside the range of observed conditions.

## Reading the implementation

Read each row as one experiment with parameters P, tokens D, steps S, compute C and held-out loss L. Compare rows only after marking which columns differ. A ratio compares multiplicative change. A log-log slope is \(\frac{\log(\frac{L_{2}}{L_{1}})}{\log(\frac{C_{2}}{C_{1}})}\), meaningful only for the specified quantities and regime. Do not hide a changed tokenizer or test distribution inside a loss column.

## Exercise 1: Read a longer training run

The question is: Compare row A with row F (P 1000, D 10000, S 400, C 4, L 1.7). Identify what changed and calculate the F/A loss ratio.

Only the number of updates and the compute it consumes differ, so the comparison is controlled for parameters and data. The decrease is measured relative to A, the baseline row.

```text
Run P     D     S   C L
A   1000  10000 100 1 2.0
F   1000  10000 400 4 1.7
Controlled: P, D, evaluation protocol. Changed: S, C.
1.7 / 2.0 = 0.85; (2.0 - 1.7) / 2.0 = 0.15
```

**Expected:** steps and compute quadrupled; parameters and data fixed; ratio 0.85, a 15 percent decrease.

**Verify:** Check that both rows keep P 1000 and D 10000, that only S and C are marked as changed, and that 1.7/2.0 reproduces the ratio 0.85.

## Exercise 2: Isolate a data change

The question is: Row H uses P 1000, D 20000, S 100 with measured C 2 and L 1.95. State which factors changed relative to A and the percent decrease.

Compute is a measured consequence of the run, not an independent knob, so it changes with D here. The comparison isolates the data-size choice only because P, S and the evaluation protocol are held fixed.

```text
Run P     D     S   C L
A   1000  10000 100 1 2.0
H   1000  20000 100 2 1.95
Controlled: P, S, evaluation protocol. Changed: D, C.
1.95 / 2.0 = 0.975; (2.0 - 1.95) / 2.0 = 0.025
```

**Expected:** data and compute changed; parameters and steps fixed; ratio 0.975, a 2.5 percent decrease.

**Verify:** Check that the comparison holds P 1000 and S 100 fixed, lists D and C as the changed columns, and that 1.95/2.0 reproduces 0.975.

## Exercise 3: Calculate a local ratio

The question is: Calculate the B/A loss ratio and the percent decrease relative to A.

A ten-percent relative decrease is different from an absolute decrease of 0.2 loss units. Keep the denominator and units explicit.

```text
1.8 / 2.0 = 0.9
(2.0 - 1.8) / 2.0 = 0.10
```

**Expected:** ratio 0.9; decrease 10 percent.

**Verify:** Recompute 1.8/2.0 and (2.0 - 1.8)/2.0 from the table: the worksheet shows 0.9 and 0.10, with the decrease measured relative to A rather than B.

## Exercise 4: Reject an unsupported forecast

The question is: A reviewer predicts loss 0.1 at compute 1000000 from rows A, B. Evaluate the claim.

Two nearby measurements do not establish the relationship over six orders of magnitude. A fitted equation can produce a number without making that number evidence-backed.

```text
Observed compute range: [1,2]
Claimed compute: 1000000
Missing: regime checks, more runs, uncertainty, data/optimization policy.
```

**Expected:** unsupported extrapolation far outside compute 1..2.

**Verify:** Check that the answer states the observed compute range 1 to 2 and names at least two missing kinds of evidence before rejecting the forecast at compute 1000000.

## Exercise 5: Design a discriminating next run

The question is: Propose a run testing parameter count while holding training data and update policy fixed.

Holding steps fixed does not hold compute fixed when the model grows. The design should state which budget is controlled and measure the resulting other quantity.

```text
Next run: P 2000, D 10000, S 100
Keep the tokenizer, split and optimizer policy fixed.
Measure actual C and held-out L; repeat seeds if studying variation.
```

**Expected:** D 10000, S 100, a declared larger P; compute measured separately.

**Verify:** Check the proposed row against row A: only P differs (D 10000 and S 100 unchanged), and C and L are listed as quantities to measure rather than assumed values.

## Exercise 6: Write a bounded conclusion

The question is: Summarize A, B and C without calling a toy trend a frontier scaling law.

A precise limited conclusion is more useful than a sweeping claim. It identifies both the observation and the experiment still needed to answer the next question.

```text
Within this toy setup, doubling updates from A to B reduced loss from 2.0 to 1.8.
C has lower loss but changes several factors.
No frontier-performance prediction is supported.
```

**Expected:** conclusion names local fixture and confounded C.

**Verify:** Check that the conclusion cites the A-to-B decrease from 2.0 to 1.8, marks row C as confounded and contains no prediction outside the observed rows.

## Review after comparison

Change one input to *Reject an unsupported forecast* and predict the result first; keep *Design a discriminating next run* failing beside the repair. Log a missing the Python standard library separately from a wrong scaling relationship value in `llm-029`.
