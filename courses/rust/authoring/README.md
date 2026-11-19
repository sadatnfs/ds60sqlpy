# Reproducible Rust authoring

Prepare Python and the [pinned shared formatting toolchain](../../../docker/formatting/README.md),
including `rustfmt` from Rust 1.99.1, edition 2024, and the shared toolchain's
locked syntax parsers. Any other supported language fences require their
prepared formatter/parser too. Then run from the repository root:

```sh
python courses/rust/authoring/build.py
```

The original specifications are foundations.py, composition.py and advanced.py.
render.py writes the route, manifest, guides, unfinished learners and separate
references/explanations as UTF-8 with LF. Its central writer passes Markdown
through `scripts.format_inline_code.canonical_markdown` in memory before the
normal write, retaining the existing final-newline rule. The shared policy
must explicitly admit each generated Markdown output path. Unsupported
snippets, transcripts and opaque Rust macro regions retain their bytes with
preservation diagnostics. Missing prepared tools/parsers or a genuine
formatting failure stop generation; there is no silent fallback or automatic
download.

Specification order defines stable rust-001 through rust-048 IDs. Do not reorder or renumber published lessons. Each stage contains sixteen chapters. Additive work needs a reviewed stable-ID strategy. The generator touches only this subject and never generates shared HTML.

Verify reproducibility by hashing the generated artifacts, rerunning build.py and comparing hashes. Project fixtures are directly authored source, not generator output. Reference compilation must use the pinned Rust/Arrow worker; a host compiler without the prepared Arrow library cannot qualify those chapters.

Every reference checks both worked scenarios with always-active assertions. Independent and transfer tasks can admit several designs, so explanations focus on invariants and diagnostic reasoning. Do not present printed markers as automatic mastery verification. Use real malformed, null, boundary and ownership cases rather than weakening an assertion to get a pass.

`answers.py` maps a lesson number to reference answers keyed by task number. A `code` answer, written in the formatter's canonical style, is appended to the reference program as a `// Task N: <task name>` block after the worked scenarios, so it runs under the same checks. The explanation's Task answers section shows the same statements wrapped in `fn main` as a complete file that rustfmt can check, names any lesson helper it uses, and adds the `observe` and `explain` text. A `written` answer is shown as prose. Every other task gets lesson-specific guidance that states plainly that no reference answer exists yet. `outcomes.py` holds one specific outcome sentence per lesson (render.py stops when one is missing or merely repeats the transfer task) and `MINUTES` for durations that differ from the stage default. A lesson's `lab` and `verification` both describe task 3: the task and its reference observation when task 3 has a code answer, otherwise reproducing Examples A and B and their observations. Generation prints how many tasks have executed, written or no reference answers. After editing an answer, run the changed reference in the `rust-stable` worker.

## Shared maintenance gates

Use [CONTRIBUTING](../../../CONTRIBUTING.md) for the prepared environment and
[validation](../../../docs/validation.md) for shared formatting, generated-reader,
link and grouped-test gates. Run only this directory's documented generator;
`make generate` refreshes shared views, not every subject's authoring source.
Check the generated diff and execute changed references in their declared
runtime. A generation pass, parser result or historical receipt is not new
runtime evidence. Preserve learner data and immutable evidence files.
