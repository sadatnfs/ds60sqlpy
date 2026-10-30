# Original modeling studies

Keep study code, synthetic fixtures, mathematical references and observed reports
separate. Both packages remain independent libraries; studies must not import the
classroom application or silently modify either package's core. Use the existing
qualified APIs where possible and record unavailable interfaces explicitly.

Preserve existing lesson IDs. The sim-* IDs in this directory are study-design
IDs, not admitted classroom lessons. Shared readers/catalogs are updated only in
a separately coordinated curriculum integration phase. Do not edit a generator's
outputs directly or label a planned lesson executable.

Use original synthetic data and implementations. The pinned glmmTMB source is
AGPL-3; analyze and cite it without copying implementation into this MIT package.
Historical AFModel operations, credentials, endpoints and datasets are not study
inputs. No external services or downloads run inside a simulation.

Every inference result states its target, coordinate measure, penalty convention,
scientific independence unit, prediction conditioning and uncertainty layers.
MAP is not posterior sampling. Random-effect Laplace is not a parameter-posterior
Laplace approximation. Exact lasso needs a nonsmooth solver and KKT validation,
not a smooth L2 optimizer or a smoothed absolute-value substitute.

A CPU smoke validates bounded code paths. A Monte Carlo claim needs the actual
replication count, failed-fit accounting, MCSE and leakage-safe evaluation.
Record fixture, source, environment and prepared-artifact identities. Keep large
runs explicitly selected and coordinate heavy Spark/runtime work with the active
release owner. No image build, registry publication, learner-state cleanup or
core mutation is implicit in running a study. Use parallel work with disjoint
ownership and no em dashes.
