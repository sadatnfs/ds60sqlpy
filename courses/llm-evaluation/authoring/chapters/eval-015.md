## Monitoring observes a changing process

A deployed assistant receives a changing mix of requests, permissions, documents and user behavior. Its model may stay fixed while its inputs or evaluation labels change. Monitoring should therefore retain the system version, event time, label-availability time, eligibility rules and denominator for every reported metric.

Fast labels can be selected labels. Easy successful requests may receive immediate confirmation, while difficult failures are investigated later. Reporting correctness only among currently labeled items can make early performance look favorable even when the full cohort will not be. A mature-cohort rule can compare outcomes after a common follow-up window, but its assumptions must match the actual label process.

Distribution shift and quality degradation are also distinct. An input histogram can change without altering conditional task performance. Quality can deteriorate with an unchanged coarse histogram if the model or an unmonitored feature changes. Use drift measures as diagnostic signals alongside outcome, coverage, latency and critical-error measurements.

## Worked case A: the same cohort changes as labels arrive

Two requests occur on day 1. The success label arrives on day 2; the failure label arrives on day 10. At day 2 the observed-label accuracy is one with half the cohort labeled. At day 10 it is one half with complete label coverage. No model changed between these reports. Comparing the two numbers without maturity information would create a false story about performance decay.

{{WORKED_A}}

## Worked case B: drift is a bounded diagnostic

The Jensen-Shannon divergence compares two categorical distributions through their midpoint \(M=(P+Q)/2\):

\[
\operatorname{JS}(P,Q)=\tfrac12 D_{KL}(P\Vert M)+\tfrac12 D_{KL}(Q\Vert M).
\]

With natural logarithms it lies between zero and \(\log 2\). The helper treats zero-probability terms as zero contributions, validates the probability vectors and reports a finite diagnostic for a changed traffic mix. A large value does not directly measure answer correctness or identify the cause of a change. SciPy `jensenshannon` returns the square root of this divergence, which is a distance; square that return value to compare with this helper. SciPy also normalizes its inputs, while this teaching helper deliberately rejects an invalid probability vector.

{{WORKED_B}}

## Online experiments need stable assignment

If comparing a new policy online, define the randomization unit and keep assignment stable for that unit. Requests from the same user can share history and affect one another. Randomizing every request may expose a user to both policies and violate a no-interference assumption. Conversely, user-level assignment requires user-level or cluster-aware analysis, even when many request rows are observed.

Version the entire treatment: model, prompt, retrieval policy, tools and fallback behavior. Record assignment and actual exposure separately. Failures before a response is returned remain part of an intention-to-treat analysis when that is the declared estimand. Analyze delayed labels with the planned maturity policy rather than peeking at whichever outcomes arrived first.

## Guardrails and incident decisions

Monitor latency and timeout rates as well as semantic quality. A correct answer returned after an operational deadline can have low utility. Keep critical policy failures separate from averages and define a rollback path that restores a known configuration with its artifacts. Alert thresholds should be calibrated to the monitoring procedure and the consequences of false alarms and missed incidents.

When a signal changes, inspect cohort composition, label coverage, missingness, infrastructure events and configuration history before attributing it to the model. A drift alert is a reason to investigate. It is not, by itself, a causal estimate of a model effect or a mandate to retrain.

The programs demonstrate delayed-label accounting and exact categorical divergence on synthetic data. They do not run a live monitoring service. An operational deployment needs reliable instrumentation, ownership, privacy review and a validated decision process, with the same explicit distinction between observed data and the claim it can support.
