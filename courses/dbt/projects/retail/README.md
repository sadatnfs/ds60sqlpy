# Owned local retail project

This is a complete dbt Core/DuckDB project. The installed adapter builds its
relations, runs unit/data tests, records snapshots and generates real artifacts.
All input records and owner labels are synthetic. The data is historical, so no
current freshness claim is made. This fixture defines net amount as paid amounts
less refunds: paid 270 less refunded 25 gives net 245. It is a different metric
from the SQL model pad's paid-only total.

## Prepare and copy

From the repository root, prepare the image and create an owned copy. The copy
command refuses to replace an existing workshop directory:

```sh
./classroom build --project ds60-data-tools --profile data-engineering
mkdir -p work
test ! -e work/dbt-retail && cp -R courses/dbt/projects/retail work/dbt-retail
cd work/dbt-retail
bash run.sh deps
bash run.sh build
bash run.sh docs generate
```

Windows uses WSL 2 and its Linux-container engine. The helper runs with the host
user's numeric identity. Set DS60_DATA_IMAGE when using another prepared release.
Only this owned directory is mounted, and no engine socket, host credential or
network access is supplied. Its database/artifacts remain after each command.

## Inspect the product

The customer_revenue model has one row per current customer. Expected net amounts
are Ada 75, Ben 170 and Cy 0, totaling 245. Pending orders contribute zero. Inspect
the staging fields, macro and model before changing that policy.

The unit fixture tests refund/pending behavior independently of seed contents.
The singular test independently reconciles the net total. The snapshot preserves
observed customer changes; it cannot recover unobserved intermediate states.
The exposure describes a consumer but does not prove an external dashboard runs.

Inspect target/manifest.json for the graph, target/run_results.json for actual
invocation outcomes and target/catalog.json for observed database columns after
documentation generation. These artifacts establish different facts. The normal
classroom displays bounded evidence; it does not start dbt's separate docs server.

```sh
bash run.sh ls --select tag:data-product+
bash run.sh build --target review
```

Targets dev and review are separate schemas in this same owned local file, not
real production environments. Save an accepted manifest outside target/ before
state/defer experiments. Lessons dbt-019 through dbt-025 explain targets, CI,
diagnostics, governance and recovery. Try a duplicate customer key, observe the
failed test, then repair the identity under a stated rule. Do not suppress tests.

A failed build can leave candidate relations, so consumer publication needs its
own gate. Keep this workshop state separate from classroom learner volumes.
Never add real credentials or personal data to the maintained fixture. Stop any
optional server before removing only the owned workshop copy.
