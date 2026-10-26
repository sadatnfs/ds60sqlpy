# JAX course authoring

Follow the root guidance and the repository's add-learning-path skill. No em dashes. Maintain a complete route from first JAX contact through independent CPU scientific and machine-learning work. Define shapes, state, random keys, transformations, numerical assumptions and evidence before API names.

The ordinary runtime is the separately qualified `jax-cpu` profile. Programs use JAX, JAXLIB and NumPy only, with tiny deterministic offline inputs. No package installation, download, network, GPU or external service belongs in a default example. Optional GPU, TPU, multi-host, Pallas and FFI capabilities require their separately stated hardware and lifecycle qualification. Logical or mapped CPU axes do not establish accelerator scaling.

Durable content lives in `authoring/`. `build.py` writes only this subject's plan, authored manifest and lesson bundles. Use `--check` for drift. Keep complete equations in explicit LaTeX delimiters, and keep executable text literal. Preserve stable IDs and existing saved-state namespaces.

Each practice unit contains original connected explanation, two changed-condition worked cases, six concrete tasks with expected observations, progressive hints and separate executable/explanatory references. Source runs from a fresh process; examples within one Run may share setup only when stated. A reference pass is not mastery or a production-quality result.

Keep runtime integration outside the content generator. JIT compilation caches and temporary checkpoint files do not survive classroom Runs. Persistent project artifacts, interactive profiling and multi-host orchestration need separate prepared workflows. Benchmark synchronized results and separate compilation, transfers and warm execution.
