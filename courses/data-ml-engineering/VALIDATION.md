# Book validation and evidence boundaries

Maintain the original chapter/program fragments, then regenerate this book with:

```sh
python courses/data-ml-engineering/authoring/build.py --source-check
python courses/data-ml-engineering/authoring/build.py
python courses/data-ml-engineering/authoring/build.py --check
```

The publisher requires all 72 stable chapter records, complete sources, exact
worked-program insertion, earlier prerequisite IDs and declared result contracts.
Do not edit generated guides, track.json, lessons.json, figure-contracts.json or
the generated subject README directly. Shared classroom HTML and TeX generation
belong to the repository integration pass after this publisher succeeds.

Run the focused semantic and source/reader tests in the prepared contributor
Python environment, with its declared scientific dependencies:

```sh
PYTHONPATH=src python -m pytest -n 4 --dist loadgroup \
  tests/test_data_ml_engineering_book.py \
  tests/test_dme_ingestion_foundations.py \
  tests/test_dme_execution_foundations.py \
  tests/test_dme_storage_foundations.py \
  tests/test_dme_operations_foundations.py \
  tests/test_dme_capstone_foundations.py
```

The ML-lifecycle and serving fragments have additional owner-maintained focused
tests and project checks. A missing optional scientific package can skip a host
unit test; that skip is not native runtime qualification. The authoritative
ordinary reference inventory comes from the actual module catalog:

```sh
python scripts/check_module_references.py \
  --profiles 'python-core data-engineering spark-local-python llm-torch-cpu' \
  --list-only --report work/dme-reference-inventory.json
```

That inventory includes other subjects using those profiles. The maintained CI
and disposable classroom gates execute the complete matching corpus and validate
its source identities, failures and required outputs. Never run an acceptance
gate against someone's active learning state. Follow the repository validation
instructions for a separately owned disposable classroom project.

During authoring, programs were executed in prepared native Linux ARM64 workers
with network disabled, a read-only image, a non-root user, bounded temporary
storage and the actual profile entrypoint. Spark ran through spark-submit;
Feast, MLflow, DuckDB, Parquet, ASGI and child-process examples executed their
real implementations. This is distinct from a classroom HTTP/UI gate and from
native AMD64 qualification, which belongs to its native runner. Do not substitute
emulation or CPU evidence for another architecture or GPU execution.

The maintained data-product and inference-service projects have separate real
HTTP, controlled failure, stop/resume and replacement checks. Read each project's
README before preparing or starting it. Their state is private to a copied owned
workshop directory and must not enter course archives or Git. A project checker
must preserve exact receipts and accepted state without replaying completed work.

Reader tests render explicit mathematics and accurately tagged code through the
actual reader. Required table, Plotly and JSON outputs use the shared result
validator and per-chapter contracts. A source change invalidates earlier source-
bound evidence; rerun the relevant checks and refresh the actual runtime receipts.
No test count or successful local run is a guarantee that no possible defect
exists. State precisely which source, environment and behavior were verified.
