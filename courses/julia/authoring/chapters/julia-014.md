## Three states with different meanings

`missing` represents unknown or unavailable data. `nothing` commonly represents the absence of a returned value. NaN is a floating-point value that often indicates an undefined numerical result. These states are not interchangeable, and a function should not collapse them into zero without a declared policy.

Operations involving `missing` can propagate uncertainty. The eager Boolean operators `&` and `|` support three-valued behavior when one part is unknown. An `if` condition and the controlling operand of `&&` or `||` still require a Boolean. `ismissing` produces a definite test. `skipmissing` iterates over observed values, while `coalesce` substitutes a stated replacement for missing data.

A vector that can hold missing values may have an element type such as `Union{Missing,Float64}`. This is a representation contract. It does not say whether missingness is random, whether deletion is valid or how uncertainty should be handled statistically.

## Worked case A: deletion and replacement change a mean

The observed values are 1 and 3, with one missing measurement. Averaging only observed values gives 2. Replacing missing with zero gives four thirds. The two results answer different questions. The program reports the observed count and total count so a reader can reconstruct the denominator.

{{WORKED_A}}

## Worked case B: skipmissing does not remove NaN

A NaN remains after missing values are skipped. The helper rejects it under its finite-measurement contract. A group with no observed values returns an explicit missing estimate and a zero observed count. This policy avoids inventing a perfect or zero-valued statistic for an empty observed set.

{{WORKED_B}}

## State the scientific assumption

Deleting incomplete rows can change a target population. Replacing a missing outcome with zero can also change the meaning of the metric. Imputation introduces modeling assumptions that need validation and uncertainty treatment. A data-manipulation function can implement a policy correctly while the policy remains unsuitable for the scientific question.

Preserve the original missingness indicators and rejected-row counts. If a downstream model requires complete numerical input, document which transformation produced it and whether it used information available at the intended prediction time. A convenient fill operation should not become an undocumented source of leakage.

## Diagnose propagation

Check the element type, count missing values, count nonfinite observed values and inspect the denominator before interpreting a surprising aggregate. A missing result may be a correct reflection of unavailable information. A NaN may instead indicate an arithmetic problem such as zero divided by zero. The appropriate response depends on provenance.

`something` handles absent `nothing` values under a separate convention. It does not silently replace every missing data value. This distinction is useful for an optional lookup result versus an unknown measurement stored in a table. Keep those contracts visible in returned records.

The examples establish the behavior of small authored arrays and one aggregation policy. They do not justify complete-case analysis, zero imputation or any other statistical strategy for an external dataset. Later table, time and modeling units retain these counts and assumptions through larger workflows.
