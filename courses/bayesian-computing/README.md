# Bayesian computing: exact inference, PyMC and Stan

A complete worked route from probability and exact oracles through actual PyMC computation and self-contained Stan compilation, sampling, diagnostics and decisions.

The course assumes basic Python and probability, with direct links to prerequisite concepts. Units 001-008 use Python Core, 009-016 use the prepared PyMC 5/ArviZ 0.23 InferenceData environment, and 017-024 compile real Stan in stan-cpu. PyMC demos use two serial chains with 120 warmup and 120 retained draws each. Stan pads use two seeded chains with 100 warmup and 100 retained draws, target acceptance 0.9. These small budgets demonstrate mechanisms and diagnostic limitations; they do not certify convergence. Stan pad data are explicit transformed-data constants. The separate [normal-mean project](projects/normal-mean/README.md) teaches real data.json workflows without implying a JSON editor exists in the classroom.

Start with the [classroom installation guide](../../README.md). These are complete worked tutorials. Sources and notes are saved; reading markers do not certify mastery.

| Unit | Topic | Runtime |
| --- | --- | --- |
| [bayes-001](guides/bayes-001.md) | Generative questions, conditioning and repeated evidence | python-core |
| [bayes-002](guides/bayes-002.md) | Log densities, normalization and exact numerical oracles | python-core |
| [bayes-003](guides/bayes-003.md) | Conjugacy, posterior prediction and duplicated observations | python-core |
| [bayes-004](guides/bayes-004.md) | Probability transformations and Jacobian accounting | python-core |
| [bayes-005](guides/bayes-005.md) | Posterior decisions, loss and regret | python-core |
| [bayes-006](guides/bayes-006.md) | Markov chains, autocorrelation and deceptive acceptance rates | python-core |
| [bayes-007](guides/bayes-007.md) | Hamiltonian geometry, integration and NUTS motivation | python-core |
| [bayes-008](guides/bayes-008.md) | Simulation-based calibration and tests that can miss errors | python-core |
| [bayes-009](guides/bayes-009.md) | An actual PyMC regression and its diagnostic record | bayesian-cpu |
| [bayes-010](guides/bayes-010.md) | Centered and noncentered hierarchical computation | bayesian-cpu |
| [bayes-011](guides/bayes-011.md) | Robust likelihoods and predictive criticism | bayesian-cpu |
| [bayes-012](guides/bayes-012.md) | Count models, exposure and overdispersion | bayesian-cpu |
| [bayes-013](guides/bayes-013.md) | Posterior geometry with weakly identified predictors | bayesian-cpu |
| [bayes-014](guides/bayes-014.md) | Pointwise predictive evaluation, PSIS and the held-out unit | bayesian-cpu |
| [bayes-015](guides/bayes-015.md) | Bayesian resource decisions and Monte Carlo uncertainty | bayesian-cpu |
| [bayes-016](guides/bayes-016.md) | Gaussian processes and conditional versus integrated uncertainty | bayesian-cpu |
| [bayes-017](guides/bayes-017.md) | Stan blocks and a conjugate reference model | stan-cpu |
| [bayes-018](guides/bayes-018.md) | Stan matrix regression and typed shape contracts | stan-cpu |
| [bayes-019](guides/bayes-019.md) | Stan constraints, log-rate transformations and Jacobians | stan-cpu |
| [bayes-020](guides/bayes-020.md) | Stan noncentered hierarchies and prediction targets | stan-cpu |
| [bayes-021](guides/bayes-021.md) | Stan logistic likelihoods and separation-aware priors | stan-cpu |
| [bayes-022](guides/bayes-022.md) | Stan marginalized mixtures and label conventions | stan-cpu |
| [bayes-023](guides/bayes-023.md) | Stan stationary dynamics and multi-step prediction | stan-cpu |
| [bayes-024](guides/bayes-024.md) | Stan censored survival workflow and decision dossier | stan-cpu |

See [authoring ownership](authoring/README.md) and [coverage](coverage.json).
