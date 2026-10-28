## A backtest is a reconstruction of historical information

A forecast predicts an outcome that is not yet known at a particular origin. A credible historical evaluation must reconstruct the records that were available at that origin. Event time says when a measurement belongs in the world; availability time says when an analyst could have used it. Revisions add another dimension because the latest value today may differ from the value first reported.

Represent a record as \((t,a,v)\), with event time \(t\), availability time \(a\), and value \(v\). At cutoff \(c\), first retain records with \(a\le c\). Then select the latest eligible record for each event. Reversing those operations can discard a valid older record or introduce a later revision. A single current-value table cannot reproduce this history after earlier versions are overwritten.

The tiny fixture follows an exact linear series: 10,12,14,16,18. An event-two value of 14 is later revised to 50. This extreme revision makes leakage visible. It is a teaching contrast, not a realistic claim about the frequency or magnitude of revisions in an operational dataset.

## Worked case 1: a vintage-aware forecast

At cutoff four, the available series through event three is 10,12,14,16. Least squares fits its trend and extrapolates event four to 18. The `as_of` function filters by availability and sorts by event/availability to construct the valid snapshot. Its explicit assertions verify both the older and current values of the revised event.

If the revised event-two value is leaked into the historical training table, the same extrapolation changes to 36. A revision to another time point can have different leverage, so the program tests the actual numerical contrast rather than assuming every corrupted input must change every prediction. This matters in test design: a fixture that accidentally leaves the result unchanged does not demonstrate protection against the intended defect.

The model is deliberately simple. The purpose is to establish an information contract that applies equally to a sophisticated forecasting system. A model with excellent backtest loss can still be unusable if the features, labels or revisions used during fitting were unavailable at forecast time. Model selection should compare procedures that obey the same cutoff rules.

## Worked case 2: overlapping horizons create dependence

Forecasts issued at origins two and three for horizons one and two include a shared target time. The program lists the origin/horizon/target triples and proves that the number of unique targets is smaller than the number of forecast errors. Treating those errors as independent observations would overstate how much distinct evidence was collected.

There are several distinct questions. Accuracy for a particular horizon should usually be summarized by horizon. Accuracy for a repeated operational schedule may weight origins and horizons according to their use. A deployment decision may instead depend on a cost function, capacity limit or service level. Specify that aggregation before examining model rankings.

For uncertainty about performance, preserve the relevant dependence with a time-aware or cluster-aware method. Resampling individual errors arbitrarily can break shared-target and serial structure. A block length is also a modeling choice: a very short block may ignore dependence, while a long block leaves few effectively independent pieces of evidence. Report sensitivity rather than treating one resampling configuration as a universal answer.

## Separate fitting, selection and final assessment

A rolling-origin backtest emulates repeated refitting, but it does not automatically supply a pristine final test. If its results are repeatedly used to choose features, model families or thresholds, it becomes part of model selection. A final untouched period or a deliberately nested temporal procedure provides a different layer of evidence.

Record the origin schedule, training window, revision policy, label delay, covariate availability, refitting cadence and losses. A future calendar indicator can be known in advance; a future realized price or weather observation usually cannot be substituted without an explicit forecast or scenario. Exogenous regressors require the same information audit as the target.

Numerical accuracy is not the only operational criterion. Forecasts must arrive before the decision deadline, handle missing updates and preserve versioned inputs. An immutable prediction record should link its origin, source snapshot, model version and decision. Otherwise a later revised warehouse can make an incorrect historical forecast appear correct or prevent a good one from being reproduced.

## Answered scientific discussion

**Should all revised data be excluded forever?** No. At a later origin, a revision that is already available can legitimately enter training. The requirement is to reproduce what was known at each origin, not to prohibit useful information.

**Does the example prove that linear regression is a good forecaster?** It proves that a linear procedure recovers a deliberately linear fixture under a valid information snapshot. Its larger lesson is procedural: changing the information boundary can dominate the apparent choice of forecasting algorithm.
