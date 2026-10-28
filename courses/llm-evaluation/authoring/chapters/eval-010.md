## A selective system changes which questions it answers

An assistant can answer, abstain or route a request to a reviewer. These actions have different costs and change the observed output population. An answer-only accuracy of 100% can be achieved by answering one easy item and refusing everything else. Its usefulness depends on coverage, refusal costs and which users are left without help.

For an answer indicator \(A_i(t)\) under threshold \(t\), coverage is \(\mathbb{E}[A_i(t)]\) and selective risk is \(\mathbb{E}[L_i\mid A_i(t)=1]\). The latter is undefined when nothing is answered. Keep that condition explicit. A risk-coverage curve shows several policies, but choosing the best-looking point and reporting its same-data performance introduces selection bias.

If a score is a calibrated probability of correctness \(p\), a simple two-action cost rule compares expected answer cost \(c_w(1-p)\) to abstention cost \(c_a\). With zero cost for a correct answer, answering is preferred when \(p\geq1-c_a/c_w\). Different loss structures, reviewer capacity or consequential subgroups require a different rule. A confidence-like number is not automatically a calibrated probability.

## Worked case A: an empirical policy choice

The development fixture has scores 0.9,0.8,0.4,0.2 and correctness 1,0,1,0. An incorrect answer costs 5 and an abstention costs 0.4. Among four prespecified thresholds,0.85 has the lowest observed development cost: it answers the first request and abstains on the remaining three. Its coverage is one quarter and its conditional accuracy is one.

That empirical threshold differs from the probability-based cutoff 0.92 because the fixture's scores were not supplied as calibrated probabilities and the development set is tiny. The program does not equate a tuned threshold with a Bayes-optimal policy.

{{WORKED_A}}

## Worked case B: frozen thresholds can fail on new data

A held-out fixture assigns high scores to two incorrect answers and low scores to two correct ones. Applying the frozen 0.85 threshold gives poor selective performance. Retuning on these labels would invalidate their role as final assessment. The adverse case demonstrates a calibration or distribution-shift problem that conditional accuracy on the development set concealed.

{{WORKED_B}}

## Capacity and subgroup tradeoffs

A reviewer queue has finite capacity, so abstention cost can depend on load and delay. A selective policy may also concentrate refusals on rare languages, unfamiliar domains or difficult user groups. Report coverage and loss by relevant slices with uncertainty; a favorable overall score can hide an unacceptable allocation of service.

A threshold policy is only as useful as its score. Calibration should be evaluated on appropriate held-out data, and calibration drift monitored after deployment. A score derived from a model's self-reported confidence can be systematically biased. Token likelihood, a learned correctness predictor and a human judgment measure different things and need their own validation.

## Diagnose the complete decision

Print counts for all eligible requests, answered requests, wrong answers and abstentions. Inspect empty-answer cases and missing correctness labels. If abstained items have no labels, the performance of a counterfactual always-answer system is not directly observed. Do not impute those labels from the fact that the system abstained.

The reference checks exact costs and invalid inputs on constructed outcomes. It does not estimate the costs of a real product or prove that a particular threshold transfers. A deployment study should state who bears each cost, how the score was calibrated, how the threshold was selected and what independent data supported the final decision. Preserve a fallback route for conditions outside the evaluated scope.
