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
from cpp_study_notes import STUDY_NOTES

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
        r"\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^{\mathsf T}}{\sqrt{d_k}}+M\right)V",
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


REASONING_PARTS = (
    ("approach", "Approach"),
    ("why", "Why it is correct"),
    ("wrong", "A plausible wrong approach"),
    ("verify", "How to verify"),
)


def check_reasoning(unit: dict) -> None:
    """Require four non-empty, dash-free reasoning parts for each of six exercises."""

    reasoning = unit.get("reasoning")
    assert isinstance(reasoning, list) and len(reasoning) == 6, unit["n"]
    for entry in reasoning:
        assert set(entry) == {key for key, _ in REASONING_PARTS}, unit["n"]
        for key, _ in REASONING_PARTS:
            text = entry[key]
            assert isinstance(text, str) and text.strip(), (unit["n"], key)
            assert "\u2014" not in text and "\u2013" not in text, (unit["n"], key)


def reasoning_markdown(entry: dict[str, str]) -> str:
    return "\n\n".join(f"**{label}:** {entry[key]}" for key, label in REASONING_PARTS)


def lesson_id(number: int) -> str:
    return f"cuda-{number:03}"


def sentence_case(text: str) -> str:
    """Capitalize a data fragment unless it opens with code or a number."""
    return text[:1].upper() + text[1:] if text[:1].isalpha() else text


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


def kernel_excerpt(source: str) -> str:
    """Return every top-level __global__ function (with a template line) from a .cu file."""
    lines = source.splitlines()
    blocks = []
    for index, line in enumerate(lines):
        if not line.startswith("__global__"):
            continue
        start = index - 1 if index and lines[index - 1].startswith("template") else index
        end = next(j for j in range(index, len(lines)) if lines[j] == "}")
        blocks.append("\n".join(lines[start : end + 1]))
    return "\n\n".join(blocks)


def listing_section(unit: dict, identity: str, gpu: dict[int, str]) -> str:
    """Render the chapter's CUDA C++ kernel listing, authored or excerpted from its lab."""
    if "listing" in unit:
        intro, code = unit["listing"]["intro"], unit["listing"]["code"].rstrip("\n")
    elif unit["n"] in gpu:
        intro = f"An excerpt from the chapter's complete [GPU reference](../references/{identity}_gpu.cu); the reading pad does not compile it."
        code = kernel_excerpt(gpu[unit["n"]])
    else:
        return ""
    return "## CUDA C++ kernel listing\n\n" + intro + "\n\n" + "```cpp\n" + code + "\n```\n\n"


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
    reasoning = unit["reasoning"]
    notes = STUDY_NOTES[number]
    exercise_pairs = [
        (
            "Reconstruct worked example 1 on paper before running its CPU reference. "
            + reasoning[0]["approach"],
            unit["example1"],
        ),
        (
            "Rework worked example 2 without copying its conclusion. " + reasoning[1]["approach"],
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
            f"### Exercise {index}\n\n{question}\n\n**Trap to avoid:** {reasoning[index - 1]['wrong']}\n\n**Hint:** {hint1}\n"
        )
        worksheet.append(
            f"## Exercise {index}\n\n{question}\n\nMy prediction or design:\n\nMy calculation, trace or observation:\n\nEvidence surface (reading / CPU reference / actual NVIDIA execution):\n\nWhat this does not establish:\n"
        )
        explained = reasoning_markdown(reasoning[index - 1])
        solutions.append(f"## Exercise {index}\n\n{answer}\n\n{explained}\n")
    equation = ""
    if number in EQUATIONS:
        expression, meaning = EQUATIONS[number]
        equation = f"## Mathematical contract\n\n\\[\n{expression}\n\\]\n\n{meaning}\n\n"
    optional = ""
    if number in gpu:
        optional = (
            "## Optional CUDA C++ laboratory\n\n"
            f"- [GPU learner source](../lessons/{identity}_gpu.cu)\n"
            f"- [GPU reference](../references/{identity}_gpu.cu)\n\n"
            "Read the [laboratory rules](../../STUDY-GUIDE.md#optional-native-cuda-laboratories) before compiling.\n\n"
        )
    sources = unit["sources"] or [
        ["CUDA Programming Guide", "https://docs.nvidia.com/cuda/cuda-programming-guide/"]
    ]
    if number == 45:
        sources = [["CUDA Core Compute Libraries", "https://nvidia.github.io/cccl/"]]
    links = "\n".join(f"- [{label}]({url})" for label, url in sources)
    key_terms = "\n".join(
        f"- **{term}:** {definition}" for term, definition in unit["key_terms"].items()
    )
    scope = sentence_case(unit["theory"].split(". ")[0].rstrip(".") + ".")
    self_checks = "\n".join(
        f"{index}. {question}" for index, (question, _) in enumerate(notes["self_check"], 1)
    )
    guide = f"""# {identity}: {title}

## Level and prerequisites

{level.capitalize()}; about {90 if number <= 16 else 110 if number <= 44 else 130} minutes, plus any optional hardware experiment. Direct prerequisites: {prerequisites}
{(chr(10) + unit["prerequisite_note"] + chr(10)) if "prerequisite_note" in unit else ""}
Pacing, evidence labels and platform rules for every chapter are in the [CUDA study guide](../../STUDY-GUIDE.md).

## Learning objectives

{unit["outcome"]}

**Scope:** {scope}

**Evidence to produce:** {sentence_case(unit["evidence"])}

## Purpose, vocabulary and mental model

{unit["mechanism"]}

### Key terms

{key_terms}

{equation}## How to run and study this lesson

Trace worked example 1 by hand, then run the [CPU reference](../references/{identity}_cpu.py) from the repository root:

```sh
python {cpu_path}
```

{listing_section(unit, identity, gpu)}## Worked example 1: trace the mechanism

{unit["example1"]}

**Why:** {reasoning[0]["why"]}

```python
{unit["code"]}
```

**Expected observation:** every assertion succeeds, and the CPU model prints:

```text
{unit["expected_output"]}
```

**Check:** {reasoning[0]["verify"]}

## Worked example 2: change a meaningful condition

{unit["example2"]}

**Why:** {reasoning[1]["why"]}

**Check:** {reasoning[1]["verify"]}

{optional}## Six progressive exercises

{chr(10).join(exercises)}
## Common mistakes and diagnosis

A tempting but incorrect claim: **{sentence_case(unit["mistake"])}** {notes["mistake_fix"]}

## Self-check, retrieval and transfer

{self_checks}

Short answers are in the [separate explanations](../solutions/{identity}_solutions.md#self-check-answers); compare only after an attempt.

## Primary references

Use the documentation that matches your prepared toolkit.

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
    answers = "\n".join(
        f"{index}. **{question}** {answer}"
        for index, (question, answer) in enumerate(notes["self_check"], 1)
    )
    answer_checks = (
        f"\n\nIt also asserts an exercise answer you derive yourself: `{unit['reference_checks']}`"
        if "reference_checks" in unit
        else ""
    )
    solutions.append(
        f"## Self-check answers\n\n{answers}\n\n"
        f"## Numerical reference and its limits\n\nThe [CPU reference](../references/{identity}_cpu.py) reproduces worked example 1 and prints `{unit['expected_output']}`.{answer_checks}\n\n"
        f"## Transfer review\n\n{unit['tasks'][3]['answer']}\n"
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
            + (unit["reference_checks"] + "\n" if "reference_checks" in unit else "")
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
    for unit in units:
        assert unit["outcome"][:1].isupper() and len(unit["outcome"].split()) >= 4, unit["n"]
        assert 3 <= len(unit["key_terms"]) <= 5, unit["n"]
        notes = STUDY_NOTES.get(unit["n"], {})
        assert notes.get("mistake_fix") and len(notes.get("self_check", [])) >= 3, unit["n"]
        check_reasoning(unit)
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
                "outcome": unit["outcome"],
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
