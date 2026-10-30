# Independent CPU environment preparation

These tools are explicit setup commands for the copied package. Package imports,
likelihood evaluation, fitting and prediction never invoke them or download
dependencies. All new preparation code is Apache-2.0; dependencies retain their
own licenses, and Spark's existing Apache license headers remain intact.

`locks/torch.arm64.lock` and `locks/torch.amd64.lock` own CPU Torch 2.9.1+cpu,
NumPy 2.2.6 and their pinned dependencies. `locks/scientific.lock` owns the
additional SciPy 1.15.3, pandas 2.2.3, PyArrow 19.0.1 and Lightning 2.6.1 stack.
These locks target native Linux and Python 3.12. `locks/build.lock` pins the
separate wheel builder to setuptools 80.9.0 and wheel 0.45.1. Runtime setuptools
retains the CPU lock's version; build tools run in a separate Docker stage.
The source origins and unchanged requirement hashes are retained in
`lock-provenance.json`. Those origin paths are provenance, not build inputs.

The Dockerfile consumes these package-local locks. An offline build additionally
needs the exact wheels in `tooling/wheelhouse/`. In a deliberately prepared native
Linux Python 3.12 environment, populate that directory explicitly with:

```sh
python3 tooling/download_wheels.py --output tooling/wheelhouse
```

This command contacts the public CPU Torch index and PyPI with exact hashes;
it is preparation, not model execution. It does not obtain Docker base images.
Download receipts are not installation or runtime qualification. Do not use this
command implicitly from a fit or notebook cell that is supposed to be offline.

`build_wheel.py` builds a noneditable wheel from a temporary copy, with no
dependency resolution or build isolation downloads. Install the pinned build
tools first. The source project is checked for changes during the build:

```sh
python3 -m pip install --require-hashes -r tooling/locks/build.lock
python3 tooling/build_wheel.py --output /owned/fresh-wheels
```

`prepare_environment.py --apply` creates one managed `.pth` file selecting the
bundled Spark/Py4J archives and calls the installed package's existing trusted
Spark 4.0.1 launcher preparation. It does not duplicate or weaken that correction.
Unknown wrapper source is rejected; a different managed Spark path is rejected.
Without `--apply`, it checks preparation without patching anything.

`check_environment.py` imports the prepared dependencies, checks exact versions,
Java, the selected PySpark archive and noneditable package source parity. It
starts no Spark application and performs no fit or distributed training. Actual
execution belongs to `examples/` and the separately owned `integration/` harness.

Run the lightweight setup-control checks without scientific dependencies:

```sh
python3 -m unittest discover -s tooling/tests -v
```

The [preparation guide](../docs/PREPARATION.md) distinguishes default neutral
bases, explicit prepared-image compatibility overrides, copied-project builds,
installed-wheel checks and actual runtime evidence.
