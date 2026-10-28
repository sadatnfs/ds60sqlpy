# Owned local ML system

This project trains two actual scikit-learn models from features retrieved through
Feast, logs their metrics and JSON artifacts with MLflow, materializes a local
SQLite feature store, and serves predictions over real loopback HTTP. It also
exercises version activation, rollback, freshness rejection and monitoring.
Inputs and outcomes are synthetic. This is a bounded local learning deployment,
not qualification of an external production population or service.

## Prepare an owned working copy

Use a Linux-container Docker engine. Windows users run these commands inside
WSL 2. From the main repository:

```sh
./classroom build --project ds60-data-tools --profile data-engineering
mkdir -p work
test ! -e work/ml-local && cp -R courses/ml-engineering/projects/local-system work/ml-local
cd work/ml-local
bash run.sh start
```

The final command prints the actual `http://127.0.0.1:PORT` URL. Open it to use the
small offline prediction form. The API schema is available at `/openapi.json`;
no CDN-backed documentation page or remote model is required. No host Python,
modeling package, database server or compiler installation is necessary.

The first start creates a private `.env` ownership marker and a unique Compose
project name. It trains in the owned `state/` directory, then starts the predictor.
It never overwrites an existing trained state. Later starts reuse the saved state
without rerunning training. Use `DS60_DATA_IMAGE` before the first start to select
another deliberately prepared image release.

## Data and modeling contract

The recorded training clock anchors 120 synthetic historical decisions. Each
row has feature availability and label availability times. Historical retrieval
must return all 120 identified requests with values matching the independently
computed input. Only 77 labels available at the training cutoff enter fitting;
40 later decisions form the validation set. All validation labels are mature at
the recorded evaluation clock. The fitted scaler uses training rows only.

Both models use the same declared three-feature schema. Their validation Brier
scores and accepted local-demo decisions are recorded in `training.json` and in
the actual MLflow SQLite backend. The acceptance threshold is an illustrative
fixture policy, not proof that either model should be deployed for a real use.

Model artifacts are bounded JSON containing feature order, scaling parameters,
coefficients and intercept. Inference validates schema, finiteness, positive
scales, version and exact artifact bytes before use. This avoids arbitrary
pickle deserialization in the service. Hashes establish integrity relative to
the accepted pointer; they do not authenticate an attacker-controlled pointer.

The same Feast feature contract supports historical training and online serving.
The service rejects missing, invalid or older-than-48-hour feature values. It
uses a retained feature timestamp for freshness, rather than assuming that a
successful online retrieval proves a recent measurement.

## Inspect and operate

Replace `PORT` with the printed port:

```sh
curl --fail http://127.0.0.1:PORT/health
curl --fail -H 'Content-Type: application/json' \
  -d '{"customer_id":1}' http://127.0.0.1:PORT/predict
curl --fail http://127.0.0.1:PORT/metrics
bash run.sh activate v2
bash run.sh activate v1
```

The control CLI validates a candidate before atomically replacing the version
pointer. The predictor reads state through a read-only mount and exposes no
administrative mutation endpoint. Its response includes the selected model
version and feature age. Both versioned predictions should be compared with
recorded training/validation evidence; a successful version switch is not a
causal claim about user outcomes.

The following deliberate failure exercise uses only this owned synthetic store:

```sh
bash run.sh inject-stale
# A prediction for customer 1 now returns HTTP 503 with a freshness diagnostic.
bash run.sh restore-features
```

Restoration republishes the original values and their original freshness
metadata. It does not falsely declare old data to be new. After enough real
elapsed time, the fixture itself becomes stale. Use a new owned copy for a fresh
training experiment and retain the previous state for comparison.

`/metrics` contains bounded process-level counts and latency samples. They reset
when the predictor process is replaced. The model/feature/tracking state is stored
separately and survives replacement. Process observations alone are not durable
monitoring history or a service-level guarantee.

## Pause, resume and remove containers

```sh
bash run.sh stop
bash run.sh resume
bash run.sh down
bash run.sh resume
```

`down` removes this project's containers and networks but retains the owned
`state/` directory. `resume` starts the predictor from that trained state without
rerunning the training service. The printed port can change after replacement.
This state is separate from normal classroom learner volumes.

Training and control use an internal project network. The predictor additionally
uses a dedicated ingress network because published ports require a suitable
bridge on supported engines. Host exposure is explicitly restricted to loopback.
No cloud credentials, engine socket or ambient feature service is supplied.
The service code makes no external requests; it is a local trusted workshop,
not a hardened multi-tenant internet execution platform.

## Reproduce the release checks

The host checker uses only Python's standard library plus the Docker CLI. It
requires a fresh project name, records resource ownership, verifies the actual
loopback address, and removes only its own containers/networks and temporary
state. Existing projects are rejected before mutation.

```sh
python courses/ml-engineering/projects/local-system/check.py \
  --project ds60-mle-check-example --confirm-disposable \
  --report work/ml-service-check.json
```

Run that command from the repository root in the prepared contributor environment.
It exercises actual training, HTTP prediction, input errors, monitoring, model
activation/rollback, stale-feature handling, byte-corruption rejection and
predictor replacement without retraining. Failed checks preserve a bounded
report. If cleanup ownership cannot be established, resources and the owned
work directory are retained for inspection instead of deleted speculatively.
