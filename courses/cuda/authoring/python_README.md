# CUDA Python and GPU Spark authoring

The durable content is `python_lessons.py`, `python_deep_notes.py`,
`python_gpu_labs.py`, `spark_lessons.py` and `spark_programs.py` in this directory.
These files contain original explanations, worked cases, targeted exercises,
answers and bounded programs. They do not fetch packages, generate benchmark
results or operate a GPU/cluster while generating documentation.

From the repository root:

```sh
python courses/cuda/authoring/python_generate.py
python courses/cuda/authoring/python_check.py
./scripts/format-repo --language python --language scala
```

Generation owns `courses/cuda/python/`, `courses/cuda/spark/`,
`python_manifest.json` and `spark_manifest.json`. The root CUDA assembly combines
these fragments with the C++ route. Do not run this generator over another
subject or hand-edit generated guides, references or worksheets.

The default checker executes 64 CPU references and 64 editable CPU examples in
parallel, parses all Python programs, and checks content/admission consistency.
It does not claim GPU, Scala or framework execution. In a deliberately prepared
matching environment, independently run:

```sh
python courses/cuda/authoring/python_check.py --framework torch
python courses/cuda/authoring/python_check.py --framework tensorflow
python courses/cuda/authoring/python_check.py --pyspark
```

Framework checks run sequentially to bound memory and isolate runtime global
state. Scala examples require the prepared `spark-local-scala` worker and its
reviewed compile/run adapter. NVIDIA variants require actual GPU-capable workers
and source-bound results; parsing those files on CPU is only syntax evidence.

Keep the default route readable and runnable as CPU models on every ordinary
classroom host. GPU Spark remains an owned external workflow; no ordinary pad
gets an engine socket, arbitrary cluster endpoint, package installer or ambient
kubeconfig. Keep source, textbook guide, exact task answers and external runtime
claims consistent when extending this route.
