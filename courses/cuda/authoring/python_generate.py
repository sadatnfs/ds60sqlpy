#!/usr/bin/env python3
"""Regenerate CUDA Python and Spark teaching bundles from owned authoring data."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from python_deep_notes import DETAILS
from python_gpu_labs import CUPY, TORCH, cupy_program, tensorflow_program, torch_program
from python_lessons import LESSONS
from spark_lessons import SPARK_LESSONS
from spark_programs import PYSPARK_BODY, pyspark_program, scala_program

ROOT = Path(__file__).resolve().parents[3]
PREREQUISITES = {
    1: [3, 5],
    2: [65],
    3: [66],
    4: [66, 67],
    5: [6, 68],
    6: [68],
    7: [7, 8, 67, 70],
    8: [3, 65, 71],
    9: [66, 72],
    10: [4, 73],
    11: [66, 74],
    12: [2, 75],
    13: [6, 74, 76],
    14: [76, 77],
    15: [7, 71, 75, 76],
    16: [73, 74],
    17: [66, 70, 72],
    18: [67, 71, 81],
    19: [3, 73, 82],
    20: [9, 11, 73, 82],
    21: [68, 71],
    22: [77, 81, 82, 85],
    23: [66, 67, 72],
    24: [71, 87],
    25: [70, 87],
    26: [6, 87, 89],
    27: [66, 87, 90],
    28: [71, 88, 89],
    29: [87, 92],
    30: [69, 87],
    31: [87, 90, 92],
    32: [88, 89, 90, 92, 94, 95],
    33: [11, 13, 17, 82, 84, 87],
    34: [97],
    35: [89, 90, 94],
    36: [87, 90, 92],
    37: [94, 99, 100],
    38: [95, 100],
    39: [87, 88, 92, 94],
    40: [85, 92, 96],
    41: [103],
    42: [74, 76, 79, 85],
    43: [82, 85],
    44: [68, 81, 85],
    45: [90, 95],
    46: [61, 97, 98],
    47: [79, 85, 92],
    48: [71, 85, 92],
    49: [3, 5],
    50: [113],
    51: [113, 114],
    52: [115],
    53: [116],
    54: [113, 117],
    55: [114, 115],
    56: [118, 119],
    57: [117, 120],
    58: [118, 119, 120],
    59: [115, 121, 122],
    60: [116, 118],
    61: [114, 119, 122],
    62: [120, 122, 125],
    63: [117, 121, 123, 124],
    64: [123, 126, 127],
}
SOURCE_GROUPS = {
    "arrays": [("CuPy array and installation documentation", "https://docs.cupy.dev/en/v13.6.0/")],
    "kernel": [
        (
            "NVIDIA CUDA Python introduction",
            "https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-python.html",
        ),
        ("Maintained numba-cuda project", "https://github.com/NVIDIA/numba-cuda"),
    ],
    "interop": [
        ("DLPack Python specification", "https://dmlc.github.io/dlpack/latest/python_spec.html"),
        (
            "CuPy interoperability",
            "https://docs.cupy.dev/en/stable/user_guide/interoperability.html",
        ),
    ],
    "framework": [
        ("PyTorch CUDA semantics", "https://docs.pytorch.org/docs/2.9/notes/cuda.html"),
        ("TensorFlow GPU guide", "https://www.tensorflow.org/guide/gpu"),
    ],
    "spark": [
        (
            "cuDF Spark plugin release and compatibility matrix",
            "https://nvidia.github.io/cudf-spark/docs/download.html",
        ),
        (
            "Supported Spark operators and expression types",
            "https://nvidia.github.io/cudf-spark/docs/supported_ops.html",
        ),
        ("GPU Spark tuning guide", "https://docs.nvidia.com/cudf-spark/latest/tuning-guide.html"),
        (
            "Apache Spark SQL performance tuning",
            "https://spark.apache.org/docs/latest/sql-performance-tuning.html",
        ),
    ],
}
FRAMEWORK_NOTES = {
    23: (
        "Create tensors and parameters on the chosen torch.device, zero gradients, compute mean loss, call backward and step. Inspect w.device and compare the derived gradient before changing the model.",
        "Create variables and operations in an explicit tf.device scope, use GradientTape, and apply the resulting gradients. Inspect variable placement and compare the same mean-loss derivative.",
    ),
    24: (
        "Use a bounded DataLoader with num_workers=0 for the tiny baseline. Compare deliberately prepared pinned batches and non_blocking transfers only on the CUDA lane.",
        "Build a finite tf.data pipeline with explicit batch and bounded prefetch. Limit the private thread pool in the teaching program and inspect preprocessing versus device work.",
    ),
    25: (
        "Distinguish memory_allocated from memory_reserved. Retained tensors and attached loss histories keep graph storage live; scalar summaries should be detached deliberately.",
        "Configure memory growth before device initialization when using it. Inspect current/peak allocator observations where supported and separate reservation policy from the required live tensors.",
    ),
    26: (
        "Use torch.autocast around supported forward/loss operations. The CUDA fp16 workflow can use torch.amp.GradScaler; unscale before gradient clipping, then step and update the scaler.",
        "Select a Keras mixed-precision policy before building layers. Use the pinned release's loss-scaling optimizer contract and inspect variable, compute and output dtypes separately.",
    ),
    27: (
        "Understand NCHW shapes and channels-last memory format as separate concepts. Compare the native convolution expression and gradients before benchmarking layout transformations.",
        "Understand NHWC/NCHW data_format and the exact tensor shape expected by tf.nn or Keras layers. Preserve cross-correlation convention and include conversions in timing.",
    ),
    28: (
        "Capture a bounded torch.profiler schedule with CPU and CUDA activities when available, add named ranges, then verify the hypothesis with ordinary synchronized timing.",
        "Capture a short TensorFlow Profiler trace using the prepared external tooling. Use input-pipeline and device views together, then repeat without profiling overhead.",
    ),
    29: (
        "Compare eager and torch.compile with the same initial state. Record compilation latency, shape guards, graph breaks and accepted shape changes; do not claim every graph uses CUDA Graph replay.",
        "Compare eager and tf.function with a stated input signature. Count retraces, then evaluate XLA as a separate configuration and preserve both outputs and gradients.",
    ),
    30: (
        "Checkpoint model and optimizer state, scaler and RNG state as applicable. The included in-memory momentum restore proves the numerical state contract; it is not durable storage or a process snapshot.",
        "Use tracked variables and tf.train.Checkpoint for a durable prepared project. The included in-memory weight/velocity restore isolates the mathematical contract before file and optimizer-trackable integration.",
    ),
    31: (
        "Use model.eval to select evaluation behavior and torch.inference_mode to avoid autograd work. They solve different problems. Materialize the final output inside response-latency timing.",
        "Call relevant layers with training=False and define a SavedModel serving signature for the external deployment route. Check output dtypes/shapes and first-call versus warm behavior.",
    ),
    32: (
        "Submit the PyTorch state and data ledger, reference loss/gradient tests, complete timing, memory observations and restart evidence. GPU-only claims need the CUDA variant on real hardware.",
        "Submit the TensorFlow variable/optimizer and input-pipeline ledger with equally complete numerical, timing, memory and restart evidence. One framework's successful run does not qualify the other.",
    ),
    33: (
        "Use a prepared custom-operator project with a registered schema, dispatch implementation, metadata behavior where needed, and explicit mutation/alias contracts. Python-level callable success is insufficient.",
        "Use a separately prepared TensorFlow custom-op project defining the op schema, shape behavior and device OpKernel. Match the framework build ABI and test placement and unsupported inputs independently.",
    ),
    34: (
        "Register a mathematically correct backward and test vector-Jacobian products with double-precision gradcheck away from kinks. An op registration check is not a substitute for derivative verification.",
        "Use the supported registered-gradient or custom_gradient mechanism. Compare GradientTape results with a native reference and finite differences, including documented nondifferentiable boundaries.",
    ),
    35: (
        "Normalize each microbatch contribution by total effective examples and step once. Evaluate checkpoint recomputation separately, including random-state and nonreentrant/reentrant API choices for the pinned release.",
        "Accumulate GradientTape gradients with example-count weighting. Use the prepared recomputation mechanism only after checking variable capture and stateful behavior; evaluate memory and extra forward work separately.",
    ),
    36: (
        "Compare scaled_dot_product_attention with explicit scores, masks, softmax and value multiplication. Record actual backend selection when exposed; test dropout policy and backward separately.",
        "Build the explicit tf.matmul/mask/softmax reference first. Compare an optional prepared optimized attention path with the same shapes and gradients rather than assuming every Keras attention layer selects the same kernel.",
    ),
    37: (
        "Freeze base parameters explicitly and construct the optimizer from intended trainable tensors. The included low-rank matrix example demonstrates storage and trainability separately before any full transformer adaptation.",
        "Set base variables nontrainable, track adapter variables and pass the intended gradient-variable pairs to the optimizer. Report all resident variables as well as trainable counts.",
    ),
    38: (
        "Keep cache tensors' batch, sequence, head and dtype contracts explicit. Compare cached token logits with uncached computation under inference mode and the same positional encoding.",
        "Represent cache state with explicit tensors or model inputs/outputs and preserve graph signatures across accepted lengths. Compare each cached step with the uncached reference before export.",
    ),
    39: (
        "Use an explicitly owned one-process-per-device DDP job with appropriate collective backend and bounded rendezvous. Validate the effective global batch and every rank's sample coverage.",
        "Use MirroredStrategy for an explicitly prepared multi-device host. In custom loops apply the distribution-aware loss normalization and compare the resulting update with a single-device reference.",
    ),
    40: (
        "Choose either a single-device or a separately qualified distributed/custom-op PyTorch path. Preserve an ordinary eager baseline and source-bound evidence for every claimed gain.",
        "Choose the equivalent bounded TensorFlow path, preserve an eager baseline and report graph/placement changes. TensorFlow needs its own acceptance evidence, not a copied PyTorch benchmark.",
    ),
}


def lower_initial(text):
    return text[:1].lower() + text[1:]


def put(relative, text):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def variant(label, title, profile, source, solution, explanation):
    return dict(
        id=label,
        title=title,
        language="python",
        runtime_profile=profile,
        source_path=source,
        solution_paths=[solution, explanation],
        verification_id=None,
    )


def build(record):
    n = record["n"]
    number = n + 64
    ident = f"cuda-{number:03d}"
    area = "python" if n <= 48 else "spark"
    base = f"courses/cuda/{area}"
    guide = f"{base}/guides/{ident}.md"
    learner = f"{base}/lessons/{ident}.md"
    explanation = f"{base}/solutions/{ident}_solutions.md"
    reference = f"{base}/references/{ident}_cpu.py"
    source = f"{base}/lessons/{ident}_cpu.py"
    exercises = record["exercise"].split(";")
    answers = record["answer"].split(";")
    assert len(exercises) == len(answers) == 6
    level = "beginner" if n <= 8 else "intermediate" if n <= 32 or n in (49, 50, 51) else "advanced"
    ids = [f"cuda-{value:03d}" for value in PREREQUISITES[n]]
    if n == 49:
        ids.append("spark-013")
    concepts = [
        word.strip() for word in record["title"].replace(":", ",").split(",") if word.strip()
    ]
    group = (
        "spark"
        if n > 48
        else "arrays"
        if n <= 8
        else "kernel"
        if n <= 16
        else "interop"
        if n <= 22
        else "framework"
    )
    sources = "\n".join(f"- [{title}]({url})" for title, url in SOURCE_GROUPS[group])
    prereq = ", ".join(f"`{value}`" for value in ids)
    theory = record["mechanism"] + "\n\n" + DETAILS.get(n, "")
    worked = "\n\n".join(
        f"### Worked example {i + 1}\n\n{text}" for i, text in enumerate(record["examples"])
    )
    tasks = "\n\n".join(
        f"### Exercise {i + 1}: {text}\n\nWrite your prediction and reasoning in the worksheet. Where numerical, show intermediate values and units; where architectural, draw the boundary and state the observable evidence. Exercise {i + 1} targets **{lower_initial(text)}** in the examples above."
        for i, text in enumerate(exercises)
    )
    # Each hint points to a different part of this lesson's reasoning rather than
    # revealing the answer. Explanatory answers remain in a separate artifact.
    hints = [
        f'Start from worked example 1 and mark the quantities needed for the task "{exercises[0]}".',
        f"Change one assumption in worked example 2 while preserving the declared contract: {lower_initial(exercises[1])}.",
        f"Trace the CPU program's variables before adding hardware behavior: {lower_initial(exercises[2])}.",
        f'Draw producers, consumers and the exact operation boundary for the task "{exercises[3]}".',
        f"Separate what the small fixture establishes from what the real runtime must show: {lower_initial(exercises[4])}.",
        f"Write a counterexample to an overbroad claim before you {lower_initial(exercises[5])}.",
    ]
    hints_text = "\n".join(f"{i + 1}. {hint}" for i, hint in enumerate(hints))
    framework = ""
    if n in FRAMEWORK_NOTES:
        torch_note, tf_note = FRAMEWORK_NOTES[n]
        framework = f"\n## Equal framework lanes\n\n### PyTorch\n\n{torch_note}\n\n### TensorFlow\n\n{tf_note}\n\nChoose either lane first, then compare the other using identical mathematical inputs. Framework-specific shape, mode and optimizer rules must be checked separately. Both use offline synthetic examples; no model hub or dataset download is triggered.\n"
    gpu_section = ""
    variants = [
        variant("cpu-model", "CPU reference model", "python-core", source, reference, explanation)
    ]
    source_code = record["code"]
    # The learner receives an editable worked example, not answers to all six
    # reasoning exercises. Reference copy adds the same behavioral assertions.
    starter_lines = source_code.splitlines()
    starter = (
        '"""Editable CPU worked example. This does not execute or simulate a GPU.\n\nComplete the six guide exercises separately; modify one bounded case at a time.\n"""\n'
        + "\n".join(starter_lines)
        + "\n"
    )
    # Reject malformed authoring data before publishing an editable example.
    ast.parse(starter)
    put(source, starter)
    put(
        reference,
        '"""Independent CPU reference with deterministic contract assertions."""\n' + source_code,
    )
    if n in CUPY:
        gpu_source = f"{base}/lessons/{ident}_cupy.py"
        gpu_solution = f"{base}/references/{ident}_cupy.py"
        code = cupy_program(n)
        put(gpu_source, code)
        put(gpu_solution, code)
        variants.append(
            variant(
                "cupy-cuda",
                "CuPy on NVIDIA CUDA",
                "cuda-python",
                gpu_source,
                gpu_solution,
                explanation,
            )
        )
        gpu_section += (
            "\n## Optional NVIDIA CUDA lab\n\nThe **CuPy on NVIDIA CUDA** variant executes the actual operation with CuPy in the separately prepared `cuda-python` profile. It refuses a missing device instead of switching to CPU. Keep inputs bounded as supplied; inspect the device, synchronize and compare with the CPU reference. The profile must pass real host/device readiness checks. Successful syntax checking on a Mac is not GPU qualification.\n\n```python\n"
            + code
            + "```\n"
        )
    if n in TORCH:
        for backend, title, profile, maker in [
            ("torch", "PyTorch", "llm-torch-cpu", torch_program),
            ("tensorflow", "TensorFlow", "tensorflow-cpu", tensorflow_program),
        ]:
            for gpu in (False, True):
                label = backend + ("-cuda" if gpu else "-cpu")
                src = f"{base}/lessons/{ident}_{label}.py"
                sol = f"{base}/references/{ident}_{label}.py"
                code = maker(n, gpu)
                put(src, code)
                put(sol, code)
                runtime = (
                    ("pytorch-cuda" if backend == "torch" else "tensorflow-cuda")
                    if gpu
                    else profile
                )
                variants.append(
                    variant(
                        label,
                        title + (" on NVIDIA CUDA" if gpu else " on CPU"),
                        runtime,
                        src,
                        sol,
                        explanation,
                    )
                )
        gpu_section += "\n## Executable framework practice\n\nThe variant chooser offers **PyTorch on CPU**, **TensorFlow on CPU**, and separate **NVIDIA CUDA** versions. CPU versions force CPU placement. CUDA versions require the named GPU profile and refuse to silently fall back. Each complete program uses the same tiny deterministic objective, bounded tensors and local synthetic data. Read its source before running; a framework pass establishes only that variant and environment.\n\nThe checkpoint demonstration is in-memory. It teaches what state must be saved; it does not export a durable model artifact or preserve an in-flight device context. Advanced custom-op, distributed and engine-building projects remain separately prepared external workflows.\n"
    if n in PYSPARK_BODY:
        for label, title, language, profile, suffix, maker in [
            (
                "pyspark-cpu",
                "PySpark on CPU",
                "python",
                "spark-local-python",
                "py",
                pyspark_program,
            ),
            (
                "scala-cpu",
                "Scala Spark on CPU",
                "scala",
                "spark-local-scala",
                "scala",
                scala_program,
            ),
        ]:
            src = f"{base}/lessons/{ident}_{label}.{suffix}"
            sol = f"{base}/references/{ident}_{label}.{suffix}"
            put(src, maker(n))
            put(sol, maker(n))
            entry = variant(label, title, profile, src, sol, explanation)
            entry["language"] = language
            variants.append(entry)
        gpu_section += "\n## Scala and PySpark parity lab\n\nChoose **Scala Spark on CPU** or **PySpark on CPU** to run the same bounded query in the ordinary Spark workers. Both use explicit schemas, local fixtures, at most two local threads, a disabled GPU SQL setting and a finally-block session stop. They assert the same expected result. These are CPU Spark observations, not GPU plugin qualification.\n\nFor external GPU comparison, retain the same relational expressions and expected result but use a separately reviewed launcher and compatibility matrix. Do not change the classroom source into an arbitrary cluster connection.\n"
    boundary = """## Platform and evidence contract

The reading worksheet and CPU reference model work through the ordinary Linux Docker classroom on macOS, Linux and Windows using WSL 2. They do not require an NVIDIA GPU. Their results are labeled CPU models or semantic oracles, not simulated hardware performance.

Real CUDA work needs supported NVIDIA hardware, a compatible host driver and an explicitly prepared GPU runtime. An Apple GPU does not execute CUDA kernels. PyTorch MPS on a supported native Mac, ROCm on supported AMD hardware, or other vendor backends can provide separate accelerator learning routes; they need their own package and operation qualification and are not CUDA evidence. The ordinary Linux Docker classroom does not expose native Mac MPS automatically.

Do not download packages, models or data by opening this lesson. Do not attach an engine socket, ambient cluster credentials or an arbitrary remote endpoint. A CPU pass, imported package, successful compilation, real GPU result and measured performance are distinct observations. Record the actual backend, data shape/dtype, source revision, versions and pending checks. A saved completion marker records learning progress, not hardware certification.
"""
    if n > 48:
        boundary += "\nGPU Spark is a separate owned external workflow. The ordinary `spark-local-scala` and `spark-local-python` profiles are CPU Spark. Keep the GPU plugin disabled or absent for a CPU-only baseline. Per-operator CPU fallback inside a working GPU plugin environment is a different condition from having no compatible GPU. Never mount a host Docker socket or ambient kubeconfig into an ordinary lesson worker.\n"
    content = f"""# {ident}: {record["title"]}

**Route:** CUDA Python and machine learning{" / GPU Spark specialization" if n > 48 else ""}. **Stage:** {level}. **Prerequisites:** {prereq}. Allow several sessions when the hardware experiment is new; the chapter is not a deadline.

## What you will be able to explain

By the end, you can **{lower_initial(exercises[0])}**, **{lower_initial(exercises[3])}**, and **{lower_initial(exercises[5])}** with evidence. Start with the two worked cases, then use the editable CPU model to make the quantities concrete.

## Mechanism and vocabulary

{theory}

## Worked examples

{worked}

## Portable executable model

The **CPU reference model** variant runs this bounded worked example using `python-core`. It uses only the Python standard library, small synthetic values and no network. Its purpose is to expose the arithmetic or contract behind the chapter. The separate reference includes assertions for the stated observations.

```python
{source_code}```

**Expected observation:** {record["expected"]}

Treat printed timing values as synthetic whenever the program says model, fixture or trace. They are not measurements of your GPU. Before editing, predict the output; after editing, compare your observation with the exact contract that changed.
{framework}{gpu_section}
## Practice and transfer

{tasks}

## Progressive hints

Use one hint at a time. The separate solution explains each answer after you have recorded an attempt.

{hints_text}

## Common mistakes and self-review

Confusing a correct tiny example with a general implementation is the central review risk. For this chapter, challenge the assumption in worked example 2, then ask whether your change preserves the mechanism described above. If you change dtype, layout, ordering, batch size or backend, update the acceptance contract rather than silently reusing the old observation. Explain an unexpected result before trying random configuration changes.

Keep a small evidence table with columns **claim**, **input**, **expected observation**, **actual observation** and **limit**. For the first claim use `{exercises[0]}`. For the final claim use `{exercises[5]}`. An unperformed GPU or cluster experiment remains pending even when the CPU model is correct.

{boundary}
## Ask an AI tutor about this lesson

> I am studying `{ident}` using `courses/cuda/{area}/guides/{ident}.md` and `courses/cuda/{area}/lessons/{ident}.md`. Help me reason about {record["title"]}. Start with my current attempt and the two worked examples. Ask which backend actually ran, give one progressive hint, and do not reveal the separate solution or mark progress unless I request it.

## Primary references

{sources}

Use the version-matched documentation of your prepared environment. These references describe interfaces and supported boundaries; the chapter's synthetic examples and CPU models are original teaching material.
"""
    put(guide, content)
    worksheet = f"# {ident}: {record['title']} worksheet\n\nRecord predictions and reasoning here. This reading pad does not execute GPU or cluster commands. The CPU reference model is a separate optional variant.\n\n"
    worksheet += "\n\n".join(
        f"## Exercise {i + 1}: {task}\n\nPrediction:\n\nReasoning:\n\nEvidence and limitations:\n"
        for i, task in enumerate(exercises)
    )
    put(learner, worksheet)
    solution = f"# {ident}: explained solutions\n\nThese answers explain the six practice tasks. CPU reference programs are mathematical or semantic checks, not proof of CUDA execution.\n\n"
    solution += "\n\n".join(
        f"## Exercise {i + 1}: {task}\n\n{answer}.\n\nConnect this conclusion to "
        + ("worked example 1" if i % 2 == 0 else "worked example 2")
        + f" and the declared contract. State what additional observation would be needed on your actual backend before claiming **{lower_initial(task)}** is qualified there."
        for i, (task, answer) in enumerate(zip(exercises, answers, strict=True))
    )
    solution += f"\n\n## Reference observation\n\n{record['expected']}\n\nThe reference file is `{reference}`. It includes deterministic assertions. These assertions establish the supplied bounded CPU example; hardware execution and architecture-specific performance remain separate checks.\n"
    put(explanation, solution)
    track = dict(
        id=ident,
        title=record["title"],
        level=level,
        minutes=100 if n < 33 else 140,
        prerequisites=ids,
        runtime="reading",
        concepts=concepts,
        outcome=exercises[0] + " and justify the backend evidence.",
        lab="Complete the two worked cases, six exercises and bounded CPU reference model.",
        verification=record["expected"]
        + " GPU and external cluster evidence must be recorded separately.",
    )
    admission = dict(
        id=ident,
        status="authored",
        language="markdown",
        runtime_profile="reading",
        guide_path=guide,
        source_path=learner,
        solution_paths=[explanation],
        verification_id=None,
        variants=variants,
    )
    return track, admission


def main():
    python_records = [row for row in LESSONS if row["n"] <= 48]
    assert len(python_records) == 48 and len(SPARK_LESSONS) == 16
    for name, records in [("python", python_records), ("spark", SPARK_LESSONS)]:
        built = [build(row) for row in records]
        fragment = dict(
            schema_version=1,
            track_lessons=[row[0] for row in built],
            admissions=[row[1] for row in built],
        )
        put(f"courses/cuda/authoring/{name}_manifest.json", json.dumps(fragment, indent=2))
    print("Generated 48 CUDA Python/ML and 16 GPU Spark chapters with portable CPU models.")


if __name__ == "__main__":
    main()
