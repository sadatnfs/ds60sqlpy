# Classroom content presentation audit

This record covers the unified classroom presentation migration. The public
entrypoint is `/classroom` for all fourteen subjects. The UI and Docker
acceptance checkpoint records runtime and browser checks separately.

## Authoring and reproducibility

Run the consolidated authoring pipeline after subject generation and before
building the HTML readers:

```sh
python scripts/normalize_lesson_prose.py --write --report work/prose-proofreading.json
python scripts/build_lesson_readers.py
```

Run the same first command without `--write` to check for pending changes.
Unreviewed joined count/word forms require editorial review. The pipeline uses
explicit reviewed inputs in `curriculum/prose-repairs.json` and
`curriculum/math-prose.json`; it does not guess word boundaries from a dictionary
at generation time. New source should already use correctly spaced prose,
explicit LaTeX and accurate fenced-code language tags.

The prose pass scans learning Markdown, notebook Markdown, README files,
current documentation, the ten subject-plan JSON documents and selected prose
slots in 75 authoring Python files. It leaves the supplied statistics outline,
fixture files and historical implementation records intact. Metadata edits are
restricted to descriptive fields. IDs, paths, ordering, prerequisites, runtime
profiles and execution data remain outside that boundary.

Exact corrections cover joined counts, words attached to English connectors,
API names attached to surrounding prose, sentence-ending forms and obsolete
navigation instructions. Home-page summaries now describe authored subjects
with readable counts. Current Spark guidance distinguishes the configured
Spark 4.0.1 classroom worker from the earlier candidate version in design
examples. The historical design-preview documents remain explicitly archival.

## Mathematical rendering

The migration converts older ASCII formulas into explicit inline or displayed
LaTeX. The Welch comparison now defines means, sample variances, group sizes,
the test statistic and approximate degrees of freedom. LLM material typesets
attention, losses, gradients, normalization, low-rank adaptation, routing and
sampling calculations. Statistics, NLP and framework explanations receive the
same rendering path.

The offline renderer audit found **3,390 rendered MathML expressions with no
fallback formulas** across 1,521 authored Markdown/notebook files. Every LaTeX
rule in the migration registry also has a direct renderer compatibility test.
Typesetting and a successful parser are distinct from mathematical correctness;
representative Welch, attention, Jacobian and LoRA derivations received a
separate human-readable review of symbols and numerical meaning.

## Preservation evidence

The final source-preservation audit compared the current content with the
previously delivered `DS60LearningLab-0.3.0-One-Command-Classroom.zip`, whose
SHA-256 is
`6b5a62f502d810dace0ceefb9ecbedfd2a5f850d52037fd55b439c98034a22cb`.
It verified the following protected surfaces without drift:

| Surface | Compared |
| --- | ---: |
| Markdown sources | 1,320 |
| Existing code blocks | 5,895 |
| Existing inline code spans | 40,427 |
| Executable program files, byte for byte | 1,178 |
| Notebook code cells, outputs and metadata | 122 notebooks |
| Authoring Python executable structure and non-prose strings | 75 files |

The stateful scanner independently recognized 121 indented code blocks and
99 multiline inline-code spans in that earlier package. It also has regression
tests for longer closing fences and unterminated fences through end of file.
These cases remain protected even when a simple triple-backtick regular
expression would miss them. New code annotations in prose do not replace or
modify an existing executable example.

## Validation and limits

The focused authoring/statistics suite passed 96 tests. Ruff and MyPy passed
for both normalizers. Curriculum validation passed all 26 checks with no
warnings, including 122 valid notebooks and 3,864 local Markdown links. The
teaching-document fence inventory had no untagged code blocks; `text` remains
the deliberate language for transcripts and non-executable prompts.

Candidate scans are editorial aids. Valid words and technical names such as
`async`, `overfitting`, `isfinite`, `noexcept`, `float32` and `BM25` must not be
split merely because a dictionary can divide them into shorter words. Reviewed
exceptions are retained in the registry. A clean targeted scan does not prove
that no future typo or unsupported mathematical macro can ever be authored.
Runtime acceptance belongs to the Docker/browser evidence in
[the implementation checkpoint](implementation/CHECKPOINT.md).
