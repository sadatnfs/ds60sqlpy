# Statistics reference comparison and learning depth

The original statistics book retains 40 chapter IDs and all 1,005 labels from its
source outline. That ledger establishes topic traceability. A heading or short
method capsule does not by itself establish the depth of a complete textbook.
The expansion therefore adds connected worked tutorials rather than assigning
new coverage claims to every existing label.

The comparison uses author-maintained or publisher contents and companion
resources. It does not claim that this classroom replaces each entire book.
Lesson text and synthetic examples are original.

| Reference | Curriculum question | Implemented route |
| --- | --- | --- |
| Kohavi, Tang and Xu, *Trustworthy Online Controlled Experiments* | Can a reader connect metric design, randomization, instrumentation, sensitivity, integrity and a release decision? | [Twelve experiment tutorials](../courses/statistics-ml/tutorials/experimentation/README.md), including A/A, SRM, CUPED, repeated monitoring, interference, switchbacks and ramping. [Publisher contents](https://assets.cambridge.org/97811087/24265/toc/9781108724265_toc.pdf). |
| Montgomery, *Design and Analysis of Experiments* | Does analysis follow the assigned experimental unit, blocking and factorial structure? | Original design chapter plus replicated factorial/alias and cluster/switchback tutorials. [Publisher resources](https://bcs.wiley.com/he-bcs/Books?action=contents&bcsId=11447&itemId=1119492440) and [NIST design guidance](https://www.itl.nist.gov/div898/handbook/pri/section3/pri3.htm). |
| *An Introduction to Statistical Learning with Applications in Python* | Are regression, classification, resampling, regularization, trees and unsupervised learning explained through complete workflows? | [Eight learning tutorials](../courses/statistics-ml/tutorials/learning/README.md) plus existing Python PCA, regularization, random-forest, XGBoost and model-search lessons. [Official labs](https://islp.readthedocs.io/en/stable/labs.html). |
| Hastie, Tibshirani and Friedman, *The Elements of Statistical Learning* | Can the reader connect optimization, regularization, ensembles, assessment and inference? | Geometry/calculus, likelihood, logistic curvature, forest diversity, boosting trajectories, PCA and procedure-level validation, followed by formal generalization bounds. [Publisher contents](https://link.springer.com/book/10.1007/978-0-387-84858-7). |
| Hernan and Robins, *Causal Inference: What If* | Are causal identification, estimation and longitudinal regimes distinguished? | Original causal chapters plus cross-fitted estimation/sensitivity and target-trial timing tutorials. [Author resource](https://miguelhernan.org/whatifbook). |

## Depth added to core methods

- Logistic regression now has a complete likelihood/gradient/Hessian explanation,
  odds interpretation, separation and decision-threshold cases.
- Forest examples use multiple features and measured tree diversity, with
  independent validation and explicit limitations of feature importance.
- Boosting connects gradients, curvature, shrinkage and early stopping. The
  existing Python XGBoost lesson remains a practical fitted-library route.
- PCA distinguishes reconstruction, variance retention and predictive utility,
  including scaling and held-out evaluation.
- Experimentation follows a common assignment/event fixture through metric
  contracts, missingness, integrity checks, effect estimates and a decision memo.
- Scientific tutorials connect causal estimation, posterior prediction,
  vintage-aware forecasting, censoring, ranking/policy evaluation, constrained
  decisions, research synthesis and an integrated analysis workflow.
- The dedicated PyMC example fits a hierarchy, performs predictive checks and
  reports actual chain diagnostics using its pinned API contract.

## Using the reference and tutorial together

Start with the tutorial matching the current question, then use the original
chapters for definitions and neighboring methods. Its listed direct prerequisites
identify concepts needed for the worked case. A beginner does not need every
specialist chapter before a first logistic regression or A/B comparison.

The specialist method capsules remain surveys unless accompanied by a developed
case. Advanced proofs, every domain-specific estimator, large-scale sampling and
external production systems require their own focused study. Keep that boundary
explicit when extending coverage. Correct code and readable mathematics are
necessary checks; they do not establish that an analysis answers the right
scientific question.
