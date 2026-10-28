## The deliverable is a reconstructable argument

An evaluation report should let another analyst reconstruct the population, data, transformations, estimates and decision. A single leaderboard number cannot explain whether a system met its intended use, which failures occurred or what remains unknown. The Research Support Desk case therefore ends its evaluation sequence with a small decision packet.

The packet records a protocol identity, system versions, dataset identity, eligibility and labeling rules, effect and uncertainty estimates, coverage and operational constraints. Every gate has a named criterion and evidence status. A no-go result can be a complete and useful evaluation when it identifies what failed and what new evidence would support reconsideration.

A content digest binds a serialized artifact to its bytes under a declared encoding. It detects later modification when compared with a trusted recorded digest. It does not establish who created the artifact, whether the protocol was followed or whether the scientific assumptions are valid. Authentication, access control and study validity are separate concerns.

## Worked case A: calculate the packet from the held-out ledger

The complete program embeds the shared synthetic fixture and selects only its operations and policy families, both assigned to the test partition. It requires labels for every eligible held-out request to be available by day 6. If any label is still missing, the program rejects the final packet instead of silently dropping that request. The training and development families do not enter the final calculation. Eight eligible requests remain. The program computes paired correctness differences, averages them within family, enumerates the four empirical family-bootstrap draws and records inverse-CDF percentile endpoints.

The estimated equal-family effect is zero, with an empirical interval from -0.25 to 0.25. Answer coverage is 0.75, one critical failure is present, and the maximum latency is 160 milliseconds. Under the authored thresholds, all four quantitative gates fail. The memo is no-go and preserves each reason. With only two synthetic families, this interval demonstrates the computation and its weakness; it is not reliable population evidence.

{{WORKED_A}}

## Worked case B: retain exact evidence through a review

The second program seals the computed packet using canonical JSON and checks it before use. Changing a score without updating the recorded digest is rejected. The original packet remains available. This is a small artifact-integrity mechanism, not a cryptographic signature or a substitute for an experiment registry with controlled access.

{{WORKED_B}}

## What the written decision should contain

State the intended users and request population, system configuration and allowed actions. Describe data selection, group/time splitting, annotation and adjudication. Give effect estimates and uncertainty using the declared sampling unit. Include missing-label coverage, abstention behavior, important slices, retrieval/evidence diagnostics, critical failures, latency and cost where relevant.

Explain the selection history. A final score should identify which choices were frozen before final assessment. If a model was revised after a failed test, identify the new development cycle and the independent evidence used afterward. Keep original failed results rather than replacing them with a later successful summary.

## Limits and follow-up

Small synthetic data can establish arithmetic and software behavior, but not a real product's quality. The effect interval here is actually computed from the held-out family differences, and the packet names its two-family limitation. More resamples would not add independent families. The second case also computes a separate hypothetical one-sided binomial upper bound \(1-\alpha^{1/n}\) for zero failures in 200 independent trials. It is not the failure rate from the main ledger, which has one observed critical failure. This calculation explains why even a hypothetical zero-failure campaign does not establish zero population risk.

A responsible memo identifies which conditions could change the decision: more independent families, mature labels, a corrected access policy, an altered target mix or a different cost assumption. Define monitoring and rollback owners before a rollout. The planned monitoring rule should match the promised decision, including how uncertain and missing signals are handled.

The six investigations ask you to vary a real gate, trace an artifact change and explain an inference limit. They do not ask you to turn every no-go into a go. The objective is a transparent decision that follows its declared evidence, including a decision to withhold deployment.
