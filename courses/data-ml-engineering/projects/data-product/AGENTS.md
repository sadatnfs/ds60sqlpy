# Data-product workshop maintenance

Read the root repository guidance, the Data and ML Engineering authoring contract
and this project's DESIGN.md before changing behavior. This is a complete
synthetic snapshot project with separate actual HTTP raw acceptance, real
Polars/DuckDB analytical preparation, immutable Parquet versions and a verified
active pointer. It is not a CDC broker or an ordinary background pad process.

Keep state exclusively under .workshop/ and source under product/ and fixtures/.
Never mount the entire project root as source because it contains private state.
The API can write raw snapshots and only read publication/private mounts. The
publisher has no network and has the separately authorized publication/control
mounts. No Docker socket, host SDK, automatic package installation or ambient
cloud credentials belong inside these containers.

Preserve owner, batch, generation, version, operation and receipt identities.
Raw replay returns the original canonical receipt. Publication validates typed
quality, actual aggregation and immutable bytes before pointer replacement.
The prepared manifest hash must match again immediately before activation.
Pointer activation and observation storage remain separate; a failed observation
cannot be rewritten as though nothing was published. Recovery reads and
reconciles actual state without automatic ingestion, recomputation or activation.

Keep ordinary generation high-water protection after explicit rollback. Old
accepted files and completed observations remain immutable. Unsupported schemas,
corruption, mismatched owners, busy writers and unknown outcomes need controlled
diagnostics, not resets or hidden retries.

Maintain Bash 3.2-compatible host control and the Compose 2.28 floor. Plain resume
uses start plus bounded inspection of the exact original container, with no
build, pull or recreation. Initial settings and port changes obey the same action
lock. Respect Docker context precedence and verify both container and network
ownership before mutation. Images must match the native engine; local release
work on the ARM Mac does not run AMD64 emulation.

Use tests/test_data_product_http.py, tests/test_data_product_launchers.py and the
maintained check_project.py. Real native acceptance includes HTTP replay/conflict
and malformed requests, independent route totals, pre/post-pointer process exits,
unchanged raw/immutable records during recovery, exact resume, replacement,
explicit rollback, stale-generation refusal and corruption rejection. Use a new
owned workspace, retain evidence before cleanup, and remove only verified owned
resources. Source packaging must exclude .workshop/ while retaining every public
module, fixture and guide. Keep native evidence distinct from source/policy tests.
