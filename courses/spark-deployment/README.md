# Spark deployment: Compose, notebooks and Kubernetes

This eighteen-unit tutorial extends the existing Scala/Spark and Kubernetes
foundations with a complete deployment investigation. Read it in the classroom,
then use the separately prepared [owned workshop](projects/cluster-lab/README.md)
for external commands. The classroom does not execute these operations in a pad.
The route is a tutorial with complete worked cases and no hidden solution gate.

Begin with [processes and modes](guides/spark-deploy-001.md), then [image
preparation](guides/spark-deploy-002.md), [isolated Compose](guides/spark-deploy-003.md)
and [bounded fitting](guides/spark-deploy-004.md). Continue through JVM cluster
submission, Jupyter, driver DNS, dependencies, live/history UIs, storage,
resources and controlled worker loss. The final five units cover Kubernetes
jobs, notebook client lifecycle, identity/policy, portable cloud choices and an
evidence dossier.

Spark 4.0.1 Standalone does not support Python cluster deploy mode. A separate
PySpark driver container and a notebook kernel use client mode. Kubernetes
cluster submission is a separate supported route with explicit preparation.

Local source checks, actual Compose acceptance, notebook preparation and cloud
execution remain distinct. The [qualification ledger](projects/cluster-lab/QUALIFICATION.md)
names what actually ran. This infrastructure fixture is not acceptance for the
independent Spark modeling packages, which need their own copied-project and
fit/predict/forecast/recovery checks.

Maintainers use [the authoring contract](authoring/README.md). Existing Spark,
Kubernetes and modeling lesson IDs remain unchanged.
