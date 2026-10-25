# CUDA learning path authoring

Read the root AGENTS.md, content authoring guide, module integration contract and
`.agents/skills/add-learning-path/SKILL.md` before edits. Preserve all canonical
IDs, variants and learner state. Use parallel agents for independent ownership.
Do not use em dashes.

CUDA is a subject spanning GPU architecture, C++ kernels, Python, ML and Spark.
A subject is not an execution profile. Reading and bounded CPU models must stay
useful on macOS, Windows through WSL 2, Linux and non-NVIDIA machines. CUDA
execution requires supported NVIDIA hardware and a qualified software path.
An AMD/Intel/Apple GPU backend is a separate runtime contract, not CUDA fallback.

## Authored sources and generation

The C++ branch uses `authoring/cpp_units.json` for original teaching prose,
practice questions, answers and standard-library CPU models.
`authoring/cpp_gpu_programs.json` stores the canonical complete standalone CUDA
references and answer-free learner harnesses. These JSON strings are normalized
to the repository's formatter settings; edit these durable sources before
regenerating, keeping `.py` and `.cu` output formatting in agreement.
Run `python courses/cuda/authoring/cpp_content.py`, then its `--check --test-models`
mode. See `authoring/CPP_README.md` for scope. Python/Spark authoring has separate
ownership and integration fragments. Regenerate only the branch being changed;
shared readers remain owned by their canonical builders.

The integration owner assembles track/lesson manifests from complete artifacts.
Never register a planned unit or claim a verifier exists. Keep verification IDs
null unless a trusted verifier is registered and tested. A `.cu` source link or
syntax lexer does not establish execution support. Optional variants must use
reviewed runtime profiles, not shell commands or arbitrary compiler arguments
from content metadata.

## Teaching contract

Every practice guide defines mechanisms before syntax, includes two explained
worked cases, six varied concrete tasks, progressive hints, a separate worksheet
and explanatory solution. Use explicit LaTeX delimiters for mathematics and real
language tags for code. Teach awkward sizes, empty cases, ownership, numerical
error and failure diagnosis. Provide complete CPU or reasoning alternatives;
never call their timing GPU performance. Explicitly label hypothetical timing
and bank/occupancy models, compiled-only evidence, actual device execution,
profiling and architecture-specific qualification.

GPU examples must be bounded, check CUDA/library status, check completion,
validate returned values and release owned resources. A process timeout does
not prove a hung GPU is safely recovered. Do not add infinite spin barriers,
shared-device resets, privileged containers, host Docker sockets or automatic
model/driver downloads. Advanced features need actual capability checks and a
portable baseline. Version and compute capability are different facts.

Multi-file CMake projects, Nsight, distributed Spark/NCCL and specialized
architecture labs remain explicit external or separately prepared workflows
unless reviewed bounded runtime support exists. Preserve default CPU ML workers
and ordinary `--all` behavior. No silently successful CPU fallback is allowed in
a CUDA capability probe or GPU-labelled result.

## Evidence and future teaching companion

Run CPU assertions and generator drift checks without a GPU. Run numerical,
error, cancellation, persistence and browser checks on an actually prepared GPU
before claiming that surface qualified. Sanitizer and profiler observations add
evidence but do not prove universal correctness. Do not invent timings or a
GPU receipt. Companion help begins by reading the learner's saved attempt and
capability notice, gives progressive hints, and reveals references only when
requested. Reading completion does not certify practical hardware competence.

See [the assembler guide](authoring/README.md) and
[Python/Spark authoring](authoring/python_README.md) for exact generation and
check commands. `build_catalog.py --check` validates assembled metadata without
writing. A GPU Spark entry should require shared GPU and Spark foundations,
not every optional dataframe elective. Current RAPIDS Accelerator/cuDF-plugin
names are discoverability labels; the supported Spark/Scala/JDK/CUDA matrix and
executed physical operators determine actual acceleration.
