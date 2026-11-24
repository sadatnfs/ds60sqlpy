# Fit a hierarchical model and inspect what the sampler actually learned

Tutorial ID: `statistics-science-009`. Prerequisites: `statistics-science-002`, `statistics-018`. Complete program: [science_09.py](examples/science_09.py). Execution profile: **bayesian-cpu**, with deliberately pinned PyMC 5.28.5 and ArviZ 0.23.4. This is a separately prepared optional scientific runtime; reading the tutorial does not install or execute anything.

## Key terms

- **Noncentered parameterization:** Writing each group mean as the population center plus a scale times a standard normal \(z\), which can improve sampler geometry when group information is weak.
- **R-hat:** A rank-normalized split diagnostic that compares between-chain and within-chain variability; values below 1.01 suggest the chains agree.
- **Effective sample size:** The number of independent draws carrying the same information as the autocorrelated MCMC draws, reported separately for the bulk and tails.
- **Divergence:** A Hamiltonian sampler warning that a trajectory failed in difficult posterior geometry; reported runs should show none after warmup.
- **Posterior predictive check:** Comparing observed features such as spread, group means and tails with outcomes simulated from posterior draws plus new observation noise.

## Define a complete generative model

Six groups have unequal sample sizes 3,5,8,10,12,15. Observations vary around group means with common noise. Instead of treating population center and variances as known, estimate them jointly:

\[
\mu\sim N(0,2^2),\quad \tau\sim\operatorname{HalfNormal}(1),\quad
z_j\sim N(0,1),\quad \theta_j=\mu+\tau z_j,
\]
\[
\sigma\sim\operatorname{HalfNormal}(2),\qquad
Y_{ij}\sim N(\theta_j,\sigma^2).
\]

The noncentered z representation can improve geometry when group information is weak. It is not universally superior; informative groups can favor other parameterizations. The prior scales are in outcome units, so rescaling observations requires reconsidering the priors.

## Simulate before conditioning

Prior predictive draws generate population parameters, group means and complete outcomes. Inspect their spread and tails against what the measurement scale permits. A mathematically proper prior can still imply absurd datasets. The example reports prior predictive spread, then samples the posterior using two chains, 600 warmup iterations and 600 retained draws per chain, with one CPU process and a fixed seed.

These bounded settings support a small teaching case. They are not a general recommendation for every posterior. The first invocation may compile model operations, while later process behavior depends on the prepared runtime's cache contract. Do not claim an interactive session persists across classroom Run actions.

## Distinguish sampling diagnostics from model adequacy

ArviZ's summary reports rank-based R-hat, bulk and tail effective sample sizes, and Monte Carlo SE. R-hat near one is useful evidence that chains behave similarly; it does not prove they explored every isolated mode. Effective sample size differs from raw draw count because draws are autocorrelated. Monte Carlo SE measures simulation error in posterior summaries, not scientific uncertainty in the parameter. As a minimum screen, current guidance (Vehtari and colleagues, 2021) runs at least four chains and asks, for every reported quantity, for rank-normalized split R-hat below 1.01 and bulk and tail effective sample sizes of at least about 100 per chain (400 in total for four chains); Hamiltonian runs should also report zero divergences after warmup. PyMC 5.28.5 reports convergence messages at exactly these R-hat and per-chain effective-sample-size values and recommends at least four chains. Passing the screen is necessary, not sufficient: no single threshold certifies every posterior quantity.

The program reports divergences and preserves diagnostic values even when they are unfavorable. It does not assert that a finite posterior mean or a successful sampler return establishes convergence. Divergences can reveal difficult posterior geometry; inspect parameterization, priors and the model before simply increasing the acceptance target or discarding problematic draws.

For example, a bounded run can report no divergences while its maximum R-hat is about 1.02 and minimum bulk effective sample size is only about 133. Both values fail the screen above: 1.02 exceeds 1.01, and 133 effective draws across two chains is below 100 per chain. That is useful runtime and diagnostic evidence, but it is not adequate grounds to claim a well-explored posterior. This two-chain teaching run is sized for the classroom budget and is not expected to pass every production threshold. More chains/draws, diagnostic inspection and a model-appropriate investigation are needed before relying on precise posterior summaries. A CPU execution or a successful assertion must not erase this limitation.

This route intentionally uses the PyMC 5 / ArviZ 0.x `InferenceData` contract. If you install current PyMC instead, expect three visible changes: PyMC 6 with ArviZ 1 returns an `xarray.DataTree` whose child nodes carry the familiar groups such as `posterior`, `prior` and `sample_stats`; summaries default to 89% equal-tailed intervals instead of 94% highest-density intervals; and `sample_prior_predictive` accepts only `draws=`, not the deprecated `samples=`. Do not combine current-major example snippets with this pinned environment without a deliberate migration and new qualification.

## Worked example: split R-hat on synthetic chains

Optional PyMC is not needed to see what R-hat responds to. This numpy version splits each chain in half and compares between-part and within-part variance on four synthetic chains of 600 draws.

```python
import numpy as np


def split_rhat(chains):
    half = chains.shape[1] // 2
    parts = np.vstack([chains[:, :half], chains[:, half : 2 * half]])
    within = parts.var(axis=1, ddof=1).mean()
    between = half * parts.mean(axis=1).var(ddof=1)
    return np.sqrt(((half - 1) / half * within + between / half) / within)


rng = np.random.default_rng(1809)
mixed = rng.normal(size=(4, 600))
stuck = mixed + np.array([0, 0, 0, 0.5])[:, None]
drift = mixed + np.linspace(0, 1, 600)
for name, chains in (("mixed", mixed), ("one chain offset 0.5", stuck), ("slow drift", drift)):
    print(f"{name:21s} split R-hat {split_rhat(chains):.3f}")
```

```text
mixed                 split R-hat 1.000
one chain offset 0.5  split R-hat 1.026
slow drift            split R-hat 1.032
```

Well-mixed chains give 1.000. Shifting one of four chains by half a standard deviation raises the value to 1.026, and a slow upward drift within every chain gives 1.032, which the split detects because first and second halves disagree. Both failures exceed 1.01 yet sit below the older 1.1 rule, which is why the stricter screen in the previous section matters. This simplified version omits the rank normalization ArviZ applies, so it is less robust to heavy tails.

## Worked example: effective sample size and Monte Carlo error

Autocorrelated AR(1) chains of 600 draws show how dependence shrinks information. The estimator sums autocorrelations until they fall below 0.05, a crude truncation.

```python
import numpy as np


def ess(chain):
    x = chain - chain.mean()
    acf = np.correlate(x, x, "full")[len(x) - 1 :] / (x @ x)
    total = 0.0
    for k in range(1, len(x)):
        if acf[k] < 0.05:
            break
        total += acf[k]
    return len(x) / (1 + 2 * total)


rng = np.random.default_rng(1809)
for rho in (0.0, 0.5, 0.9):
    chain = np.zeros(600)
    for t in range(1, 600):
        chain[t] = rho * chain[t - 1] + rng.normal()
    n_eff = ess(chain)
    print(
        f"AR(1) rho {rho}: ESS {n_eff:6.1f} (theory {600 * (1 - rho) / (1 + rho):5.1f}) "
        f"MCSE of mean {chain.std(ddof=1) / np.sqrt(n_eff):.3f}"
    )
```

```text
AR(1) rho 0.0: ESS  600.0 (theory 600.0) MCSE of mean 0.043
AR(1) rho 0.5: ESS  243.6 (theory 200.0) MCSE of mean 0.075
AR(1) rho 0.9: ESS   44.0 (theory  31.6) MCSE of mean 0.336
```

Independent draws give the full 600. At \(\rho=0.5\) the estimate is 243.6 against a theoretical 200, and at \(\rho=0.9\) it is 44.0 against 31.6; the crude truncation stops early and overstates information for strongly dependent chains. The Monte Carlo SE of the mean grows from 0.043 to 0.336, larger both because fewer effective draws remain and because the AR(1) marginal variance itself grows with \(\rho\). This is why the guide asks for bulk and tail ESS for every reported quantity.

## Check predictive behavior and pooling

Posterior predictive draws add new observation noise to posterior parameter draws. Compare observed and predicted spread, group means, outliers and any decision-relevant tails. The example prints observed group means beside posterior group means, making shrinkage visible, and reports predictive versus observed spread. An overall SD agreement alone is a deliberately limited check; it can hide wrong subgroup tails or missing time structure.

The preceding exact-normal unit varies prior scale and computes a decision loss. Carry those questions into this fitted hierarchy: does stronger shrinkage change the action, and does the result remain stable under a scientifically plausible alternative likelihood? Comparing pooled and unpooled models should include predictive checks and the target decision, not just which table has narrower intervals.

**Answered discussion: What does the program's successful assertion establish?** It verifies the expected data structure, available diagnostics, finite predictive values and matching observation dimensions. It does not certify posterior convergence or that the normal model is adequate for a real dataset. Interpret the printed diagnostic evidence explicitly.

Versioned reference: [ArviZ 0.23.4 summary](https://python.arviz.org/en/v0.23.4/api/generated/arviz.summary.html). Model/API source: [PyMC 5.28.5 release](https://github.com/pymc-devs/pymc/releases/tag/v5.28.5). Return to [scientific cases](README.md).
