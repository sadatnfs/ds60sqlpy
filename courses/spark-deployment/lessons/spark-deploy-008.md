# spark-deploy-008: Distribute Python, JVM and native dependencies

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-002`, `spark-deploy-004`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Place each dependency beside the process that imports it

A Python driver import, executor Python import, JVM class and native executable have different installation boundaries. Shipping a Python source archive does not install its shared libraries. Shipping a JAR does not make its native library match the worker's architecture. Treat an environment as an artifact with a version and identity rather than a set of ad hoc installation cells.

The workshop's Spark runtime is prepared before services start. Runtime network isolation intentionally prevents a missing dependency from being repaired silently by downloading it during a task. The notebook image can add notebook tools, but executor numerical packages must still exist in the worker image or in an explicitly supported distributed environment archive.

## Worked case A: distribute pure Python source

```sh
spark-submit \
  --master spark://master:7077 \
  --deploy-mode client \
  --py-files feature_rules.zip \
  --conf spark.driver.host=driver \
  --conf spark.driver.bindAddress=0.0.0.0 \
  application.py
```

This is a command template for a prepared gateway. `feature_rules.zip` contains importable pure Python source. Verify its digest and import it inside an actual executor task, then record interpreter version and the module's source identity. A successful import in the gateway alone proves only driver preparation. Spark's `--py-files` mechanism is not a general wheel installer.

## Worked case B: add a native numerical dependency

```text
Pure archive: Python source only
Wheel: may contain architecture-specific ELF libraries
Native worker: executable plus runtime libraries and model/source binding
JVM adapter: compiled against the selected Spark/Scala ABI
```

For a native package, build its wheel, executable and JAR using the package's own documented tooling. Install or distribute them according to that package's actual contract. The Spark/TMBad project, for example, binds source and build identity and distributes verified artifacts through SparkFiles; do not replace that with a driver-only absolute path assumption. Keep the package's independent copied-folder test separate from this classroom workshop.

A changed-condition example uses an ARM64 native artifact on an AMD64 worker. The correct result is a clear architecture or loader rejection before claiming a numerical result. Never emulate another architecture on a machine whose local qualification scope is native-only. Use an authorized native hosted runner for the other architecture.

## Diagnose and transfer

Record whether the failure is module lookup, binary ABI, missing system library, source-identity mismatch or model admission. Copying more files into the image without understanding the failing boundary can create two implementations with ambiguous import precedence. Test a noneditable installation in a clean copied project, without the original checkout on the import path.

Do not bundle Spark itself inside an application JAR unless the supported deployment specifically requires it. Keep Spark/Scala versions explicit, license notices with native dependencies and private build caches outside the distributable source. Artifact availability is necessary; successful executor loading and computation remain separate evidence.

## Primary references

- [Spark Python package management](https://spark.apache.org/docs/4.0.1/api/python/tutorial/python_packaging.html)
- [Application dependency bundling](https://spark.apache.org/docs/4.0.1/submitting-applications.html)
