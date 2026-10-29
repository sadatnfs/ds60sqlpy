# Custom likelihoods in PyTorch

Twenty worked tutorials from observation models and automatic differentiation to nonlinear panel maximum likelihood, uncertainty and distributed-gradient contracts.

Start with basic Python, tensors and elementary probability. The first five chapters develop likelihood notation and numerical oracles before progressing to custom distributions, dependence, inference and forecasting. Each chapter contains two contrasting worked cases, full float64 CPU source and answered modeling discussions. All data are original tiny offline fixtures.

Use the classroom path selector and the separately prepared `llm-torch-cpu` runtime. Save edited code, notes and reading progress through the ordinary classroom controls. A successful run reproduces a numerical investigation; it is not an exam result or evidence of scientific mastery. Chapter 19 executes serial DDP scaling arithmetic and the actual sampler, not distributed training. The capstone estimates shared mean parameters with supplied covariance, and its plug-in prediction uncertainties are explicitly approximate.

Start with the [classroom installation guide](../../README.md). These are complete worked tutorials. Sources and notes are saved; reading markers do not certify mastery.

| Unit | Topic | Runtime |
| --- | --- | --- |
| [clp-001](guides/clp-001.md) | Observation, parameter and likelihood | llm-torch-cpu |
| [clp-002](guides/clp-002.md) | Reduction and weight contracts | llm-torch-cpu |
| [clp-003](guides/clp-003.md) | Analytic, finite-difference and AD gradients | llm-torch-cpu |
| [clp-004](guides/clp-004.md) | Constraints and density transformations | llm-torch-cpu |
| [clp-005](guides/clp-005.md) | Gaussian linear MLE from first principles | llm-torch-cpu |
| [clp-006](guides/clp-006.md) | Nonlinear decay and forecasting | llm-torch-cpu |
| [clp-007](guides/clp-007.md) | Binary logistic likelihood | llm-torch-cpu |
| [clp-008](guides/clp-008.md) | Count models and exposure | llm-torch-cpu |
| [clp-009](guides/clp-009.md) | Censoring contributes survival probability | llm-torch-cpu |
| [clp-010](guides/clp-010.md) | Heteroskedastic observation models | llm-torch-cpu |
| [clp-011](guides/clp-011.md) | Mixture likelihoods and stable log sums | llm-torch-cpu |
| [clp-012](guides/clp-012.md) | Correlated panel residuals | llm-torch-cpu |
| [clp-013](guides/clp-013.md) | Penalty, prior and objective placement | llm-torch-cpu |
| [clp-014](guides/clp-014.md) | Identifiability and profile likelihood | llm-torch-cpu |
| [clp-015](guides/clp-015.md) | Optimizers and closure semantics | llm-torch-cpu |
| [clp-016](guides/clp-016.md) | Gradient and curvature audits | llm-torch-cpu |
| [clp-017](guides/clp-017.md) | Prediction is a distinct estimand | llm-torch-cpu |
| [clp-018](guides/clp-018.md) | Frequentist uncertainty and limits | llm-torch-cpu |
| [clp-019](guides/clp-019.md) | Minibatch and DDP gradient scaling | llm-torch-cpu |
| [clp-020](guides/clp-020.md) | Reproducible nonlinear panel dossier | llm-torch-cpu |

See [authoring ownership](authoring/README.md) and [coverage](coverage.json).
