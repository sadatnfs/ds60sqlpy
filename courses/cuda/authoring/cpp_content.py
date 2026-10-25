#!/usr/bin/env python3
"""Regenerate CUDA foundation/C++ guides, worksheets and checked CPU references.

Only this author's subtree and cpp_manifest.json are written. The integration
owner assembles the whole subject's track.json and lessons.json from fragments.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import textwrap
from pathlib import Path

from cpp_gpu_sources import references, starter

ROOT = Path(__file__).resolve().parents[3]
AUTHORING = Path(__file__).resolve().parent
PREFIX = "courses/cuda/cpp"

EQUATIONS = {
    1: (
        r"T_{\mathrm{new}}=T_{\mathrm{serial}}+\frac{T_{\mathrm{parallel}}}{s}+T_{\mathrm{transfer}}",
        "Times use the same units; s is the speedup of only the parallel portion. Launch and other overhead must also be included when present.",
    ),
    4: (
        r"\operatorname{exclusive}(x)_i=\sum_{j=0}^{i-1}x_j",
        "The empty prefix at index zero has sum zero. This definition specifies semantics independently of the parallel scan algorithm.",
    ),
    5: (
        r"\operatorname{byteOffset}(r,c)=(r s+c)b",
        "Here r is row, c is column, s is row stride in elements, and b is bytes per element. All indices must satisfy logical bounds.",
    ),
    6: (
        r"|y-\widehat y|\leq\operatorname{atol}+\operatorname{rtol}|\widehat y|",
        "The observed value is y and the reference is y-hat. Require finite values unless exceptional outputs are explicitly part of the contract.",
    ),
    7: (
        r"P\leq\min(P_{\mathrm{peak}},B I)",
        "P is operations per second, B is bytes per second, and I is operations per byte under the stated traffic model. This bound omits fixed overhead and many implementation effects.",
    ),
    14: (
        r"i=t+kG,\qquad 0\leq t<G,\quad k\geq0",
        "G is the positive grid stride and t is a unique starting thread index. Each valid i has a unique quotient and remainder, establishing coverage without duplicate ownership.",
    ),
    18: (
        r"C_{r,c}=\sum_{k=0}^{K-1}A_{r,k}B_{k,c}",
        "Rows r and columns c identify the output, while k is the contracted dimension. Empty contraction has a zero sum under this definition.",
    ),
    20: (
        r"s=\sum_{i=0}^{n-1}x_i",
        "This specifies the mathematical sum. The chosen parallel association affects finite-precision rounding, so an error policy is still required.",
    ),
    21: (
        r"p_i=\sum_{j=0}^{i-1}f_j,\qquad N_{\mathrm{out}}=\sum_{j=0}^{n-1}f_j",
        "Each selection flag f is zero or one. A selected element writes at its exclusive prefix p, preserving original order.",
    ),
    23: (
        r"y_i=\frac{x_{i-1}+x_i+x_{i+1}}{3}",
        "The formula requires a separately stated boundary policy for indices outside the input. Input and output are distinct during one time step.",
    ),
    29: (
        r"\mu=\frac{1}{n}\sum_i x_i,\qquad v=\frac{1}{n}\sum_i(x_i-\mu)^2",
        "This is population variance for nonempty data. Centering reduces cancellation relative to subtracting two large nearly equal moments, but does not make all rounding disappear.",
    ),
    31: (
        r"S=\frac{T_{\mathrm{baseline}}}{T_{\mathrm{candidate}}}",
        "Both durations must measure the same input, result and timing scope. A ratio of host request time to isolated kernel time compares different contracts.",
    ),
    34: (
        r"a_{\ell}=a_0+\ell s b",
        "Lane ell requests an address at stride s elements, with b bytes per element. Address span is a model input, not a measured transaction count.",
    ),
    36: (
        r"N_{\mathrm{blocks}}\leq\left\lfloor\frac{R_{\mathrm{SM}}}{R_{\mathrm{thread}}T_{\mathrm{block}}}\right\rfloor",
        "This simplified register-only bound ignores allocation granularity and all other hardware limits. Do not report it as actual achieved occupancy.",
    ),
    38: (
        r"S_{\mathrm{median}}=\frac{\operatorname{median}(T_b)}{\operatorname{median}(T_c)}",
        "Use a consistent summary policy and retain both raw sample sets. The ratio is scoped to the actual experiment.",
    ),
    40: (
        r"T_{\mathrm{ideal}}=u+c+d+(N-1)\max(u,c,d)",
        "For N chunks, u/c/d are upload, compute and download durations. This ideal pipeline assumes enough independent engines and correctly ordered reusable buffers.",
    ),
    43: (
        r"N_{\mathrm{break-even}}=\frac{T_{\mathrm{setup}}}{T_{\mathrm{ordinary}}-T_{\mathrm{replay}}}",
        "The denominator must be positive and the compared iteration work must be equivalent. Strict improvement needs more repetitions than equality at break-even.",
    ),
    46: (
        r"C\leftarrow\alpha A B+\beta C",
        "Dimensions, layout and compute type must match the selected GEMM interface. The old output contributes when beta is nonzero.",
    ),
    47: (
        r"X_k=\sum_{n=0}^{N-1}x_n e^{-2\pi\mathrm{i}kn/N}",
        "This forward DFT convention uses a negative exponent and no forward normalization. The matching inverse needs its corresponding scaling.",
    ),
    48: (
        r"y_r=\sum_{j=\mathrm{rowptr}[r]}^{\mathrm{rowptr}[r+1]-1}\mathrm{value}[j]x_{\mathrm{column}[j]}",
        "Offsets and columns here are zero-based. Empty rows have equal adjacent offsets and therefore an empty sum.",
    ),
    49: (
        r"r=b-A\widehat x",
        "The residual r measures equation satisfaction by the computed x-hat. Small residual alone does not imply small forward error for an ill-conditioned matrix.",
    ),
    50: (
        r"\operatorname{SE}(\overline X)\approx\frac{s}{\sqrt n}",
        "This familiar sampling-error estimate assumes independent draws and suitable finite variance. Duplicated streams violate the independent-sample interpretation.",
    ),
    51: (
        r"p_i=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},\qquad m=\max_j z_j",
        "Subtracting one shared row maximum preserves ratios and prevents overflow from a large finite maximum. Exceptional/all-masked rows still need an explicit policy.",
    ),
    52: (
        r"y_i=\frac{x_i-\mu}{\sqrt{v+\epsilon}}",
        "This centered population normalization puts epsilon inside the square root. RMS normalization and epsilon outside the root are different formulas.",
    ),
    54: (
        r"\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right)V",
        "The mask M, softmax axis and scaling dimension d_k are part of the model contract. The first tiny example deliberately states that its scores are unscaled.",
    ),
    60: (
        r"E_p=\frac{S_p}{p}",
        "Strong-scaling efficiency E uses speedup S for fixed total work on p devices with the same result and timing scope.",
    ),
    64: (
        r"\frac{\partial}{\partial x_i}\sum_j(a x_j+b)=a",
        "This derivative assumes a and b are constant with respect to the input. Parameter gradients require their own declared contract.",
    ),
}


def lesson_id(number: int) -> str:
    return f"cuda-{number:03}"


def cpu_starter(unit: dict) -> str:
    """Keep only supplied literal fixtures/imports, never the solved model."""
    identity = lesson_id(unit["n"])
    tree = ast.parse(unit["code"])
    fixtures = []
    for statement in tree.body:
        if isinstance(statement, (ast.Assign, ast.AnnAssign)):
            try:
                ast.literal_eval(statement.value)
            except (ValueError, TypeError, SyntaxError):
                continue
            fixtures.append(ast.get_source_segment(unit["code"], statement))
    instructions = [
        "CPU model practice: " + unit["title"],
        "Reconstruct the first worked model and its stated assertions in this lesson's saved pad.",
        "Then extend your own code for Exercise 3: " + unit["tasks"][0]["question"],
        "Check the boundary from Exercise 5: " + unit["tasks"][2]["question"],
        "These are supplied literal fixtures, not a completed algorithm or CUDA execution.",
    ]
    comments = "\n".join(
        "# " + line for instruction in instructions for line in textwrap.wrap(instruction, width=86)
    )
    return (
        f'"""{identity}: answer-free CPU model practice."""\n\n'
        + comments
        + ("\n\n" + "\n".join(fixtures) if fixtures else "")
        + '\n\nraise NotImplementedError("Implement the CPU model and boundary assertions above.")\n'
    )


def render(unit: dict, gpu: dict[int, str]) -> dict[str, str]:
    number = unit["n"]
    identity = lesson_id(number)
    title = unit["title"]
    level = "beginner" if number <= 16 else "intermediate" if number <= 44 else "advanced"
    prerequisites = (
        ", ".join(f"`{x}`" for x in unit["prerequisites"])
        or "None within this subject. Basic loops and arrays help; revisit Python or C++ foundations when needed."
    )
    guide_path = f"{PREFIX}/guides/{identity}.md"
    worksheet_path = f"{PREFIX}/lessons/{identity}.md"
    explanation_path = f"{PREFIX}/solutions/{identity}_solutions.md"
    cpu_path = f"{PREFIX}/references/{identity}_cpu.py"
    exercise_pairs = [
        (
            "Predict and trace the first worked example before running its CPU reference. Write every intermediate quantity that leads to the stated result, including units or ownership where applicable.",
            unit["example1"],
        ),
        (
            "Reconstruct the second worked example without copying its conclusion. Identify the changed input or condition, show the resulting calculation or dependency, and explain why it differs from the first example.",
            unit["example2"],
        ),
        *[(entry["question"], entry["answer"]) for entry in unit["tasks"]],
    ]
    exercises = []
    worksheet = [
        f"# {identity}: learner worksheet\n",
        "Use this saved worksheet on any classroom platform. Optional CPU and NVIDIA observations have separate evidence labels. Do not claim a GPU run from a CPU model.\n",
    ]
    solutions = [
        f"# {identity}: explanatory solutions\n",
        f"## Mechanism review\n\n{unit['mechanism']}\n",
        f"The separate [CPU reference](../references/{identity}_cpu.py) checks the chapter's bounded model. It does not execute CUDA or establish GPU timing. Compare after attempting the worksheet or explicitly choosing to reveal solutions.\n",
    ]
    for index, (question, answer) in enumerate(exercise_pairs, 1):
        hint1 = (
            "Start with the literal input and intermediate quantities in worked example 1."
            if index == 1
            else "Identify exactly which condition changes in worked example 2."
            if index == 2
            else "Use the first worked example to establish the relevant quantities, then change only the requested input."
            if index == 3
            else "Locate the failed phase or violated dependency before proposing a repair."
            if index == 4
            else "Check what the algorithm is allowed to read, write or assume at this boundary."
            if index == 5
            else "State the output contract and which observations are needed in the new application."
        )
        exercises.append(
            f"### Exercise {index}\n\n{question}\n\n**Self-check:** Retain the requested calculation, output, diagram or explicit failure policy so another reader can compare it with the worked cases.\n\n**Hint 1:** {hint1}\n\n**Hint 2:** Review the mechanism paragraph and the relevant bounded CPU assertion; separate mathematical reasoning from optional device evidence.\n"
        )
        worksheet.append(
            f"## Exercise {index}\n\n{question}\n\nMy prediction or design:\n\nMy calculation, trace or observation:\n\nEvidence surface (reading / CPU reference / actual NVIDIA execution):\n\nWhat this does not establish:\n"
        )
        solutions.append(f"## Exercise {index}\n\n{answer}\n")
    equation = ""
    if number in EQUATIONS:
        expression, meaning = EQUATIONS[number]
        equation = f"## Mathematical contract\n\n\\[\n{expression}\n\\]\n\n{meaning}\n\n"
    optional = ""
    if number in gpu:
        optional = f"""## Optional CUDA C++ laboratory

A complete [GPU reference](../references/{identity}_gpu.cu) and separate
[GPU learner source](../lessons/{identity}_gpu.cu) accompany this chapter.
They are standalone files with bounded fixtures, checked runtime calls and host
validation. The learner source intentionally reports incomplete implementation
until you add the chapter's algorithm and assertions. It must never return a
fake GPU success on a CPU machine. Follow the [manual GPU workflow](../README.md)
for exact compilation and execution paths. If the classroom offers the optional
CUDA C++ variant, its capability notice must confirm actual runtime readiness.

The reference contains an explicit no-device failure, launch and completion
checks, and returned-value validation. Source review and CPU reference checks do
not qualify this .cu file on your hardware. Preserve compilation, actual device
execution and sanitizer evidence separately. Exercise 4 is a reasoning diagnosis;
do not deliberately launch a hanging kernel or reset a shared GPU to reproduce it.

"""
    sources = unit["sources"] or [
        ["CUDA Programming Guide", "https://docs.nvidia.com/cuda/cuda-programming-guide/"]
    ]
    if number == 45:
        sources = [["CUDA Core Compute Libraries", "https://nvidia.github.io/cccl/"]]
    links = "\n".join(f"- [{label}]({url})" for label, url in sources)
    guide = f"""# {identity}: {title}

## Level and prerequisites

{level.capitalize()}; about {90 if number <= 16 else 110 if number <= 44 else 130} minutes, plus any optional hardware experiment. Direct prerequisites: {prerequisites}

The order supports learning at your own pace. Reading and CPU reasoning remain
available when NVIDIA hardware is absent. Advanced hardware features need their
own capability checks and are not prerequisites for opening this chapter.

## Learning objectives

Explain {title[0].lower() + title[1:]} using the concrete cases below. Produce {unit["evidence"][0].lower() + unit["evidence"][1:]}
Distinguish an algorithmic calculation, a compiled artifact and an actual device
observation when explaining what your work establishes.

## Purpose, vocabulary and mental model

{unit["mechanism"]}

{equation}## How to run and study this lesson

Open this chapter in `/classroom` and use its saved reading worksheet. The primary
reading pad does not execute CUDA. The two examples, six tasks and separate
explanations are usable offline on macOS, Linux and Windows through WSL 2 with
the ordinary classroom. An AMD, Intel or Apple GPU does not make this CUDA C++
source executable through Docker.

For the bounded CPU calculation, select **CPU model (Python)** in this lesson.
That variant keeps its own source and result history under the same chapter. Its
answer-free starter supplies literal fixtures and the task contract; implement
the model and assertions before replacing its deliberate incomplete-work error.
The separate [CPU reference](../references/{identity}_cpu.py) uses only Python's
standard library. For an optional terminal workflow, run this from the repository
root in a prepared Python environment:

```sh
python {cpu_path}
```

The assertions check the stated numerical result or model invariant. Console text
is evidence of this CPU reference only. The [CUDA C++ study workflow](../README.md)
explains optional GPU compilation, paths, hardware requirements and evidence labels.
No lesson opening downloads a model, installs a driver or starts a GPU job.

## Worked example 1: trace the mechanism

{unit["example1"]}

The complete CPU model below intentionally models only the named arithmetic,
layout, dependency or capability decision. It does not model GPU scheduling,
caches, instruction timing or device memory visibility.

```python
{unit["code"]}
```

**Expected observation:** Every assertion succeeds. A representative CPU output is:

```text
{unit["expected_output"]}
```

Tiny floating-point display differences across platforms are acceptable only
where the explicit assertions use a tolerance; integers, shapes and ordering
must still satisfy their exact contracts. A printed hypothetical duration is a
model output, not a measured GPU benchmark.

## Worked example 2: change a meaningful condition

{unit["example2"]}

Before applying this example to your own program, write down which inputs are
read, which result is produced, and the condition that makes the comparison
valid. Keep the original case as a regression check when changing a boundary.

{optional}## Six progressive exercises

{chr(10).join(exercises)}
## Common mistakes and diagnosis

A tempting but incorrect claim in this chapter is: **{unit["mistake"]}**

For the concrete failure exercise, {unit["tasks"][1]["question"][0].lower() + unit["tasks"][1]["question"][1:]}
Preserve the original input and the stage where behavior diverged. Compare with
the CPU model or dependency diagram before changing hardware configuration.
A compiler result, synthetic timing model, profiler counter and returned numeric
answer support different claims. Record unavailable hardware honestly.

## Self-check, retrieval and transfer

Explain the first example without its code, then use the second example to state
one assumption that matters. Complete Exercise 3 independently, use Exercise 4 to
diagnose a plausible defect, check the boundary in Exercise 5, and retain the
application contract from Exercise 6. Compare the [separate explanations](../solutions/{identity}_solutions.md)
only after your attempt or a deliberate reveal. A reading marker records your
choice; it does not certify hardware qualification or expert mastery.

## Primary references

These are further technical references. The chapter and local CPU model remain
readable offline. Check the documentation matching your deliberately prepared
toolkit before optional hardware execution.

{links}

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {identity}: {title}.
Read {guide_path} and {worksheet_path}.
Direct prerequisites: {prerequisites}
Review my own explanation and worksheet; give one progressive hint at a time.
Keep {explanation_path} and GPU references closed until I request comparison.
Treat {cpu_path} as CPU model evidence, never a CUDA execution receipt.
Do not install drivers, download packages, run external jobs, reset devices or change my saved work without my instruction.
Ask me to explain the boundary case and which observation would disprove my answer.
```
"""
    solutions.append(
        f"## Numerical reference and its limits\n\nThe complete CPU model is [here](../references/{identity}_cpu.py). Its assertions check the exact small model shown in the guide, including its explicit tolerance where present. It does not claim CUDA execution, concurrency safety or a performance measurement.\n\n## Transfer review\n\n{unit['tasks'][3]['answer']}\n\nA complete explanation must name its inputs, the unchanged mathematical contract, the changed boundary or resource condition, and the evidence still needed on actual hardware. Preserve a CPU baseline even after a GPU path becomes available.\n"
    )
    result = {
        guide_path: guide,
        worksheet_path: "\n".join(worksheet),
        explanation_path: "\n".join(solutions),
        cpu_path: (
            f'"""{identity}: CPU reference only, not CUDA execution."""\n\n'
            + ("\n" if unit["code"].startswith("def ") else "")
            + unit["code"]
            + "\n"
        ),
        f"{PREFIX}/lessons/{identity}_cpu.py": cpu_starter(unit),
    }
    if number in gpu:
        result[f"{PREFIX}/references/{identity}_gpu.cu"] = gpu[number]
        result[f"{PREFIX}/lessons/{identity}_gpu.cu"] = starter(number)
    return result


def artifacts() -> dict[str, str]:
    units = json.loads((AUTHORING / "cpp_units.json").read_text(encoding="utf-8"))
    assert [unit["n"] for unit in units] == list(range(1, 65))
    gpu = references()
    files: dict[str, str] = {}
    track, admissions = [], []
    for unit in units:
        n, identity = unit["n"], lesson_id(unit["n"])
        files.update(render(unit, gpu))
        track.append(
            {
                "id": identity,
                "title": unit["title"],
                "level": "beginner" if n <= 16 else "intermediate" if n <= 44 else "advanced",
                "minutes": 90 if n <= 16 else 110 if n <= 44 else 130,
                "prerequisites": unit["prerequisites"],
                "runtime": "reading",
                "concepts": [unit["title"], "CPU reference and explicit GPU evidence"],
                "outcome": unit["evidence"],
                "lab": unit["tasks"][0]["question"],
                "verification": unit["tasks"][0]["answer"],
            }
        )
        admission = {
            "id": identity,
            "status": "authored",
            "language": "markdown",
            "runtime_profile": "reading",
            "guide_path": f"{PREFIX}/guides/{identity}.md",
            "source_path": f"{PREFIX}/lessons/{identity}.md",
            "solution_paths": [f"{PREFIX}/solutions/{identity}_solutions.md"],
            "verification_id": None,
        }
        admission["variants"] = [
            {
                "id": "cpu-model",
                "title": "CPU model (Python)",
                "language": "python",
                "runtime_profile": "python-core",
                "source_path": f"{PREFIX}/lessons/{identity}_cpu.py",
                "solution_paths": [
                    f"{PREFIX}/references/{identity}_cpu.py",
                    f"{PREFIX}/solutions/{identity}_solutions.md",
                ],
                "verification_id": None,
            }
        ]
        admissions.append(admission)
    files["courses/cuda/authoring/cpp_manifest.json"] = (
        json.dumps({"track_lessons": track, "admissions": admissions}, indent=2) + "\n"
    )
    variants = {
        lesson_id(n): {
            "id": "cuda-cpp",
            "title": "Optional NVIDIA CUDA C++",
            "language": "cpp",
            "runtime_profile": "cuda-cpp",
            "source_path": f"{PREFIX}/lessons/{lesson_id(n)}_gpu.cu",
            "solution_paths": [
                f"{PREFIX}/references/{lesson_id(n)}_gpu.cu",
                f"{PREFIX}/solutions/{lesson_id(n)}_solutions.md",
            ],
            "verification_id": None,
        }
        for n in sorted(gpu)
    }
    files["courses/cuda/authoring/cpp_optional_gpu_variants.json"] = (
        json.dumps(variants, indent=2) + "\n"
    )
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Check generated artifacts without writing."
    )
    parser.add_argument(
        "--test-models",
        action="store_true",
        help="Execute all 64 bounded CPU references; never run GPU code.",
    )
    args = parser.parse_args()
    expected = artifacts()
    mismatches = []
    for relative, text in expected.items():
        path = ROOT / relative
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                mismatches.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if mismatches:
        print("Generated CUDA C++ artifacts differ:\n" + "\n".join(mismatches), file=sys.stderr)
        return 1
    if args.test_models:
        for number in range(1, 65):
            path = ROOT / PREFIX / "references" / f"{lesson_id(number)}_cpu.py"
            result = subprocess.run(
                [sys.executable, str(path)], text=True, capture_output=True, timeout=10, check=False
            )
            if result.returncode:
                print(f"{path.name} failed:\n{result.stdout}\n{result.stderr}", file=sys.stderr)
                return 1
        print("64 CPU model references passed. CUDA compilation/execution was not performed.")
    print(
        f"CUDA C++ artifacts {'checked' if args.check else 'generated'}: {len(expected)} files; 64 chapters; 8 optional GPU bundles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
