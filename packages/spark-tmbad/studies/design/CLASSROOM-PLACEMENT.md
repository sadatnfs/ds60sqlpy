# Classroom placement plan

No existing lesson ID, draft namespace, prerequisite or reader is changed by
this plan. The current source inventory has clp-001..020, asm-001..038,
tmb-001..048 and bayes-001..024. The sim-* names are study-design identifiers only;
no catalog or runtime admission has been created for them.

| Study block | Existing teaching anchors | Proposed integration |
| --- | --- | --- |
| sim-001/002 | clp-002, clp-013, asm-008 | Add a worked study appendix on weights, global reduction and one penalty |
| sim-003..005 | clp-013/014, bayes-013 | Selected ridge, exact lasso/KKT and nested regularization tuning |
| sim-006/007 | clp-006/020, tmb-010/024 | Nonlinear growth/decay coordinates, extrapolation and multi-start evidence |
| sim-008/009 | asm-003/033, tmb-016 | Shared versus independent models, imbalance and boundary estimates |
| sim-010/011 | bayes-003/004, clp-004, asm-036 | Prior coordinates, MAP and exact posterior contrasts |
| sim-012..017 | tmb-015/018/021/024, bayes-016 | Leakage-safe known/unseen group forecasting and uncertainty layers |
| sim-018..027 | clp-007..011, tmb-011, bayes-011/021 | Rich observation families and model selection on shared synthetic data |
| sim-028..033 | clp-012, tmb-008/015/016, asm-011 | Covariance structures, independence, identification and ML versus REML |
| sim-037 | asm-011, tmb-015, bayes-016 | Exact low-rank globally coupled Gaussian likelihood from distributed sufficient statistics |
| sim-034..036 | clp-018, bayes-008/015, tmb-014/031 | Robust uncertainty, posterior calibration, MCSE and failure ledgers |

The preferred first integration is an additive tutorial path, tentatively
`modeling-simulation-studies`, whose chapters link to the stable prerequisite
lessons and the original shared fixtures. Before assigning permanent lesson IDs,
check the live catalog for collisions and review each unit's runtime evidence.
An appendix can be linked from an existing lesson without renumbering it.

Every admitted study needs an explanatory chapter, at least two scientifically
changed worked cases, exact TeX notation, accurately tagged code, expected
observations, a failure/diagnostic discussion and answered interview questions.
Teach the estimand and data-generating process before the API call. Distinguish
source-only proposals, serial references, actual package execution and actual
Spark observations in the learner-facing capability notice.

Source scripts and fixed commands remain in this study project. Future classroom
wrappers should reuse the existing separately prepared Spark/Torch or native
project rather than introduce another UI. Large Monte Carlo experiments are
explicit project runs, not unrestricted ordinary coding-pad operations. Outputs
should provide compact tables/Plotly JSON for chapter viewing, with full bounded
reports retained in the owned project directory. TeX compilation, math inventory,
reader regeneration, relative-link checks and browser observations happen only
in the later coordinated admission phase.

The statistics tutorial remains a learning book with worked answers. This plan
does not introduce exams, hidden solution gates or mastery claims based on merely
running a study. The same fixture can support Python and Scala readers without
duplicating or diverging scientific definitions.
