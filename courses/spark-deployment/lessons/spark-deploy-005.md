# spark-deploy-005: Run supported Standalone cluster jobs

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-004`, `spark-009`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Put a supported driver on a worker

Spark Standalone 4.0.1 supports JVM cluster-mode applications. It does not support Python cluster deploy mode. A PySpark program running in a separate driver container is still client mode. Use the supported language/manager pair rather than changing a label in a receipt.

An application JAR contains its entrypoint and nonprovided dependencies. Spark and the matching Scala binary API are normally supplied by the runtime. Packaging a different Spark distribution inside the JAR can create class conflicts. The example uses Spark's bundled Scala SparkPi program to focus on driver placement; its Monte Carlo number is not a correctness oracle for the bounded linear fit.

## Key terms

- **Cluster deploy mode:** A mode in which the cluster manager launches the driver on a worker rather than in the submitting process.
- **Application JAR:** A Java archive containing the entrypoint and nonprovided dependencies, without its own copy of Spark.
- **Scala binary version:** The Scala ABI line, here 2.13, that application classes must share with the Spark runtime.
- **Language and manager pair:** The supported combination: Standalone 4.0.1 runs JVM applications in cluster mode but not Python applications.
- **Class conflict:** A failure caused by packaging a different Spark or Scala distribution inside the application JAR.

## Worked case A: submit the bundled JVM example

In an explicitly prepared Spark 4.0.1 gateway on the same private network, locate the exact bundled examples JAR first:

```sh
ls /opt/spark/examples/jars/spark-examples_2.13-4.0.1.jar
/opt/spark/bin/spark-submit \
  --master spark://master:7077 \
  --deploy-mode cluster \
  --class org.apache.spark.examples.SparkPi \
  --conf spark.standalone.submit.waitAppCompletion=true \
  --conf spark.eventLog.enabled=false \
  /opt/spark/examples/jars/spark-examples_2.13-4.0.1.jar 4
```

These commands run inside the prepared gateway environment, not blindly in the host terminal. The application artifact must be reachable through the supported Standalone submission path. The expected evidence is a driver launched by a worker, a completed application and its driver/executor logs. Capture actual host identities. A submission acknowledgment alone proves acceptance of a request, not job completion. Event logging is explicitly disabled here because this gateway recipe does not supply shared event storage on every possible worker-hosted driver.

## Worked case B: change only the deploy mode for Python

```text
Application: bounded_job.py
Manager: Standalone
Requested deploy mode: cluster
Expected result: unsupported manager/language combination
Supported repair: client mode with reachable driver, or Kubernetes cluster mode
```

Do not treat this expected refusal as a reason to downgrade the version or hide the error. Keeping the Python program unchanged while selecting Kubernetes is a deployment change with new image, API identity and storage requirements. The Kubernetes submission chapter supplies those dependencies explicitly.

## Worked example: a submission matrix for manager, language and deploy mode

```python
SUPPORTED = {
    ("standalone", "jvm", "client"),
    ("standalone", "jvm", "cluster"),
    ("standalone", "python", "client"),
    ("kubernetes", "jvm", "client"),
    ("kubernetes", "jvm", "cluster"),
    ("kubernetes", "python", "client"),
    ("kubernetes", "python", "cluster"),
}


def review(master, app, mode):
    manager = "kubernetes" if master.startswith("k8s://") else "standalone"
    language = "python" if app.endswith(".py") else "jvm"
    verdict = "supported" if (manager, language, mode) in SUPPORTED else "refuse before submitting"
    return f"{manager:10} {language:6} {mode:7} -> {verdict}"


print(review("spark://master:7077", "spark-examples_2.13-4.0.1.jar", "cluster"))
print(review("spark://master:7077", "bounded_job.py", "cluster"))
print(review("spark://master:7077", "bounded_job.py", "client"))
print(review("k8s://https://API_SERVER:6443", "local:///opt/app/bounded_job.py", "cluster"))
```

Output from running the block above:

```text
standalone jvm    cluster -> supported
standalone python cluster -> refuse before submitting
standalone python client  -> supported
kubernetes python cluster -> supported
```

The table encodes the rule from the chapter for Spark 4.0.1: Standalone accepts JVM applications in cluster mode, but a Python application must run in client mode, while Kubernetes accepts both languages in both modes. The review function decides manager and language from the master URL and the application path, then refuses the unsupported pair before spark-submit is called. The Standalone JVM cluster row is the SparkPi submission from worked case A. The Python cluster row is worked case B, and the two repairs appear on the following lines: keep Standalone with a reachable client mode driver, or move the unchanged program to Kubernetes, where the local:// scheme means the file is already inside the image. Refusing early produces a clearer receipt than letting spark-submit fail and then editing the receipt's mode label.

## Worked example: checking an application JAR for a bundled Spark copy

```python
import io
import zipfile

buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w") as jar:
    jar.writestr("META-INF/MANIFEST.MF", "Main-Class: com.example.FitJob\n")
    jar.writestr("com/example/FitJob.class", b"\xca\xfe\xba\xbe")
    jar.writestr("org/apache/spark/SparkContext.class", b"\xca\xfe\xba\xbe")
    jar.writestr("scala/collection/immutable/List.class", b"\xca\xfe\xba\xbe")

with zipfile.ZipFile(buffer) as jar:
    names = jar.namelist()
    main = jar.read("META-INF/MANIFEST.MF").decode().split(":", 1)[1].strip()
provided = [n for n in names if n.startswith(("org/apache/spark/", "scala/"))]
print("main class:", main, "| present:", main.replace(".", "/") + ".class" in names)
print("runtime-provided classes bundled:", provided)
```

Output from running the block above:

```text
main class: com.example.FitJob | present: True
runtime-provided classes bundled: ['org/apache/spark/SparkContext.class', 'scala/collection/immutable/List.class']
```

An in memory ZIP stands in for a built application JAR so the inspection can run without a JVM build. The manifest names com.example.FitJob and that class file is present, which rules out the simplest class not found cause. The scan then finds org/apache/spark and scala classes inside the JAR, which the runtime already provides. Shipping a second copy of SparkContext or the Scala standard library is the class conflict the chapter warns about: whichever copy the class loader finds first wins, and a method not found error can appear even though the class exists. The repair is to mark Spark and Scala as provided in the build, rebuild and record the new artifact hash together with Spark 4.0.1 and Scala 2.13 in the submission receipt.

## Worked example: a supervised cluster submission with an idempotent output

```bash
RUN_ID=fit-2026-01-15
/opt/spark/bin/spark-submit \
  --master spark://master:7077 \
  --deploy-mode cluster \
  --supervise \
  --class com.example.FitJob \
  --conf spark.eventLog.enabled=false \
  /shared/jars/fit-job-1.0.jar \
  --output "/results/$RUN_ID" --mode write-once
```

This is a planning command, shown without output because no cluster was run while writing it. The --supervise flag asks the Standalone master to restart the driver if it exits with a failure, so the application may run its write step more than once. The command therefore passes an explicit run identity, fit-2026-01-15, and a write once mode that the application is assumed to implement by refusing to overwrite an existing output directory. Without that contract a supervised restart can append a second copy of results or partially overwrite the first. The JAR path under /shared assumes storage every worker can read, because in cluster mode any worker may host the driver. Event logging stays disabled for the same reason as worked case A: this recipe provides no shared event directory for a worker hosted driver.

## Diagnose and transfer

If a custom JVM job fails with a class-not-found error, inspect its main-class name, JAR contents and supplied dependency list. An ABI mismatch can surface as a method-not-found error despite the class existing. Record Spark version, Scala binary version and the compiled artifact hash together. A successful compile on the host does not establish executor loading.

Standalone supervision can restart a failed driver when deliberately enabled, but a restarted application can repeat external effects. Decide whether the job is safe to restart and persist an idempotent output identity before using supervision. Worker-loss recovery, driver restart and recovery of external state are separate experiments.

## Primary references

- [Supported submission modes](https://spark.apache.org/docs/4.0.1/submitting-applications.html)
- [Standalone cluster submission and supervision](https://spark.apache.org/docs/4.0.1/spark-standalone.html)
