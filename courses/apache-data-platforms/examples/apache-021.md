# Real Ballista entry point

Prepare this separate project rather than the ordinary DataFusion 55 worker.
From the repository root:

```bash
mkdir -p work
cp -R courses/apache-data-platforms/projects/ballista work/ballista
cd work/ballista
bash run.sh prepare
bash run.sh start
bash run.sh check
```

If an existing native Swift/Noble classroom image is used to avoid another base
pull, select the documented explicit fallback during preparation:

```bash
bash run.sh prepare --reuse-swift
```

The check compares actual Ballista and embedded DataFusion 54 results with a
separately derived fixture oracle. Its result records source identity and versions.
Consult README and QUALIFICATION for the exact observed platform, limits and
remaining acceptance gates.
