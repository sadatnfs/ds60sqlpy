# Numerical validation and evidence boundaries

The twenty complete programs were executed with PyTorch 2.9.1+cpu in the existing native ARM64 image `ds60sqlpy-worker-llm-torch-cpu:1.0.0`, image ID `sha256:c7cec4cab01e32440a3279d8f705cf5170aab9192379f05e95db2b4dc5ed734c`. The disposable runs used no network, a read-only course mount, a temporary filesystem, two CPUs and a 1 GiB memory ceiling. No learner volume was attached.

All 20 programs returned finite JSON diagnostics. The independent unittest suite in `tests/test_custom_likelihood_pytorch.py` passed all 24 tests, including a loop executing every program. Host source checks passed three tests; its 21 numerical tests explicitly skipped because Torch is absent there. Skips are not numerical acceptance.

The numerical checks include changed-parameter analytic gradients, Gaussian closed-form MLEs, exact support failures, independent scalar mixture densities, the AR(1) conditional innovation factorization, penalized minimizers, a fully enumerated empirical cluster bootstrap and capstone conditional forecasts. The finite-difference decay gradient maximum error reached about 3.4e-11 on the declared fixture. The capstone final gradient maximum was about 3.0e-7 and its minimum information eigenvalue about 10.72. These are tiny CPU correctness investigations, not performance measurements or interval-coverage studies.

Maintainers can reproduce the source checks with:

```bash
python courses/custom-likelihood-pytorch/authoring/build.py --check
python -m unittest discover -s tests -p 'test_custom_likelihood_pytorch.py' -v
```

The second command requires the separately prepared Torch runtime for its numerical class. No package download is performed by any tutorial. Research references target the PyTorch 2.9 documentation; the actual qualified patch version is recorded above.

This course does not start Spark, DDP process groups, CUDA or external services. Browser rendering, the shared catalog, generated HTML readers and TeX compilation are integration checks owned by the classroom release. Their acceptance must not be inferred from these source and Torch checks. The DDP chapter performs serial gradient arithmetic and actual sampler membership inspection. Prediction covariance is supplied in Chapter 17; covariance parameters are supplied in Chapter 20, whose plug-in observation uncertainty omits specified joint-estimation terms.

The qualification runner preserves image identity, per-file SHA-256 values, full numeric JSON and test logs in the release task's `work/advanced-spark-tmb/clp-evidence/`. That local evidence directory is not a learner dependency. If numerical sources change, rerun the corresponding tests and refresh evidence before carrying these claims into a release.
