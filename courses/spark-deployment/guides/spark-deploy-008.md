# spark-deploy-008: Distribute Python, JVM and native dependencies

Tutorial mode. Stage: intermediate. Direct prerequisites: `spark-deploy-002`, `spark-deploy-004`.

Read this tutorial in the classroom. Its commands run only in the separately prepared [owned workshop](../projects/cluster-lab/README.md); there is no pad Run action. Examples describe expected observations. Check the workshop qualification ledger for actual execution evidence.

## Place each dependency beside the process that imports it

A Python driver import, executor Python import, JVM class and native executable have different installation boundaries. Shipping a Python source archive does not install its shared libraries. Shipping a JAR does not make its native library match the worker's architecture. Treat an environment as an artifact with a version and identity rather than a set of ad hoc installation cells.

The workshop's Spark runtime is prepared before services start. Runtime network isolation intentionally prevents a missing dependency from being repaired silently by downloading it during a task. The notebook image can add notebook tools, but executor numerical packages must still exist in the worker image or in an explicitly supported distributed environment archive.

## Key terms

- **Installation boundary:** The process, such as driver Python, executor Python or the JVM, in which a dependency must actually exist.
- **Python wheel:** A built Python package archive that may contain architecture-specific native libraries and must import in every process that uses it.
- **Native ABI:** The binary interface a shared library expects; a JAR or archive cannot make it match the worker's architecture.
- **SparkFiles:** The Spark mechanism that distributes files to executors and resolves their executor-local paths.
- **Runtime network isolation:** The rule that tasks cannot download a missing dependency, so preparation must supply it in advance.

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

## Worked example: importing a shipped source archive and proving where it came from

```python
import hashlib
import io
import sys
import zipfile
from pathlib import Path

archive = Path("feature_rules.zip")
entry = zipfile.ZipInfo("feature_rules/__init__.py", date_time=(2020, 1, 1, 0, 0, 0))
entry.create_system = 3
entry.external_attr = 0o644 << 16
buffer = io.BytesIO()
with zipfile.ZipFile(buffer, "w") as zf:
    zf.writestr(entry, "VERSION = '1.2.0'\ndef clip(x):\n    return min(max(x, 0), 100)\n")
archive.write_bytes(buffer.getvalue())
sys.path.insert(0, str(archive))
import feature_rules

print("sha256", hashlib.sha256(archive.read_bytes()).hexdigest()[:16])
print("version", feature_rules.VERSION, "clip(140) =", feature_rules.clip(140))
print("loaded from", Path(feature_rules.__file__).parent.parent.name)
sys.path.remove(str(archive))
archive.unlink()
```

Output from running the block above:

```text
sha256 71643e7b37ffcc2e
version 1.2.0 clip(140) = 100
loaded from feature_rules.zip
```

The archive is built in memory with a fixed entry timestamp, creator system and permission bits, so its bytes and digest are identical on every run, and written to the working directory only so the import has a real file to load from; it stands in for the `feature_rules.zip` passed with `--py-files`. Putting a ZIP on `sys.path` is the same zipimport mechanism Spark relies on when it adds shipped Python files to each executor's path. The output binds three facts together: the archive digest prefix `71643e7b37ffcc2e`, the module's declared version 1.2.0 with a behavior check (`clip(140)` returns 100), and the location the module was loaded from, which is the ZIP rather than some stray checkout. In a real run, the same three lines should be produced inside an executor task, for example by a `mapPartitions` function that returns them, because a driver-side import only proves the gateway. If the digest printed by an executor differs from the one recorded at build time, two copies are in circulation and import precedence, not numerical logic, is the first thing to investigate.

## Worked example: matching wheel platform tags to worker architectures

```python
wheels = [
    "fitcore-0.4.1-cp312-cp312-manylinux_2_28_aarch64.whl",
    "fitcore-0.4.1-cp312-cp312-manylinux_2_28_x86_64.whl",
    "feature_rules-1.2.0-py3-none-any.whl",
]
workers = {
    "worker-a": ("cp312", "aarch64"),
    "gpu-pool-1": ("cp312", "x86_64"),
    "legacy": ("cp311", "x86_64"),
}
for wheel in wheels:
    _, _, python_tag, _, platform = wheel[:-4].split("-")
    ok = [
        name
        for name, (py, arch) in workers.items()
        if platform == "any" or (python_tag == py and platform.endswith(arch))
    ]
    print(f"{wheel:55} -> {ok}")
```

Output from running the block above:

```text
fitcore-0.4.1-cp312-cp312-manylinux_2_28_aarch64.whl    -> ['worker-a']
fitcore-0.4.1-cp312-cp312-manylinux_2_28_x86_64.whl     -> ['gpu-pool-1']
feature_rules-1.2.0-py3-none-any.whl                    -> ['worker-a', 'gpu-pool-1', 'legacy']
```

Wheel filenames encode the interpreter and platform they were built for, so a quick parse catches the ARM64 versus AMD64 mismatch described in the changed-condition example before any task runs. The `aarch64` build of `fitcore` matches only worker-a, the `x86_64` build matches only `gpu-pool-1`, and the `legacy` worker on CPython 3.11 matches neither native wheel because its `cp311` tag differs from `cp312`. Only the pure `py3-none-any` archive installs everywhere, which is exactly why `--py-files` works for pure source and fails silently for compiled code. The worker inventory here is invented for illustration; a real one should come from each executor reporting `platform.machine()` and `sys.version_info` from inside a task. This check is necessary but not sufficient: a matching tag still says nothing about the glibc version behind `manylinux_2_28`, missing system libraries, or whether the loaded binary was built from the source revision you recorded.

## Diagnose and transfer

Record whether the failure is module lookup, binary ABI, missing system library, source-identity mismatch or model admission. Copying more files into the image without understanding the failing boundary can create two implementations with ambiguous import precedence. Test a noneditable installation in a clean copied project, without the original checkout on the import path.

Do not bundle Spark itself inside an application JAR unless the supported deployment specifically requires it. Keep Spark/Scala versions explicit, license notices with native dependencies and private build caches outside the distributable source. Artifact availability is necessary; successful executor loading and computation remain separate evidence.

## Primary references

- [Spark Python package management](https://spark.apache.org/docs/4.0.1/api/python/tutorial/python_packaging.html)
- [Application dependency bundling](https://spark.apache.org/docs/4.0.1/submitting-applications.html)
