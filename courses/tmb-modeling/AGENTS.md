# TMB modeling authoring

This is an original tutorial and a separately prepared R/C++ project. Source is
`guides/`, `examples/` and `projects/tmb-local/`. Do not copy GPL examples from TMB,
PyMB or ar.matrix into this Apache-licensed source tree. Cite their research and
retain installed dependency licenses. Never claim that the ordinary R pad can
compile a multi-file TMB project. The maintained manifests are `track.json` and `lessons.json`. Preserve their stable
IDs and the explicit base-R companion versus native-project capability boundary.
New proposals stay outside admission until their referenced artifacts exist.

Validate normalized likelihoods, derivatives, optimizers, random-effect
integration and predictive targets independently. A small gradient or an optimizer
success code does not establish identifiability. Use original bounded synthetic
data. Record R/TMB/Matrix/compiler/framework/architecture with results. Model DLLs
are process-local and ABI-specific; never serialize an external pointer to Spark.

Run `python3 projects/tmb-local/tests/test_reference.py` for host algebra and input
checks. Actual TMB acceptance is `Rscript --vanilla tests/acceptance.R` from the
prepared project, with `TMB_BUILD_DIR` pointing to the prepared model libraries.
Do not build heavy images until the release coordinator assigns the slot. Keep
compiled products and learner results outside this source directory.

The complete tutorial reserves `tmb-001` through `tmb-048`. `api-inventory.json`
is the maintained public API map for TMB1.9.25: 30 explicit exports, nine
registered S3 methods with overlap, and separately labeled documented GK.
`API-REFERENCE.md` gives exact signatures and original explanations. Update both
when the package changes, and keep `tests/public_api_exports.json` synchronized.
Never infer public export status solely from a manual page. Public API execution
scopes remain distinct from inventory coverage and from experimental options.

`tests/public_api.R` exercises the ordinary prepared API in a one-CPU/one-GiB
container. Its tiny benchmark uses a fixed 10,000-evaluation budget because
two-evaluation durations rounded to zero. Raw Newton requires the appropriate
symmetric compressed sparse Hessian representation. Preserve these diagnosed
contracts rather than weakening checks. All R fences match their executable
companions; after formatting a companion, synchronize its complete-code fence.

The model-authoring C++ surface has a separate map in `cpp-api-families.json`
and `CPP-API-FAMILIES.md`. The five original family probes under
`projects/tmb-cpp-api/` are separate from the frozen nine-model project.
Keep covariance/precision meaning, scale Jacobians, separable array-axis order,
conditional tape behavior and custom atomic derivative orders in their checks.
Do not claim coverage of every private Eigen or AD-engine symbol.
