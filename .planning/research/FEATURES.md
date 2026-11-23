# Feature Landscape

**Domain:** Desktop-first local classroom for self-directed programming, data, statistics, machine learning, and applied science learning  
**Researched:** 2026-11-23  
**Confidence:** MEDIUM — strong computing-education design sources, but little directly addresses adult self-study in a local multi-track classroom.

## Scope and Baseline

This is a subsequent-milestone feature map, not a proposal to recreate the product. The project already has a local browser classroom, prepared Docker worker profiles, saved progress/drafts/run records, a broad catalog, lesson rendering, and an initial Python/SQL step-through implementation. The overhaul should make the lessons and their operation consistently teachable across the existing tracks. Preserve stable lesson identities, local execution boundaries, saved state, and the explicit distinction between planned and authored lessons.

Current course roots include advanced spark modeling, Apache data platforms, applied science, Bayesian computing, C/C++/C#/CUDA, data/ML engineering, data visualization, DAX, dbt, deep learning (PyTorch/TensorFlow), Docker, Go, Java, JavaScript/TypeScript, JAX, Julia, Kubernetes, LLM application/evaluation/theory, ML engineering, NLP, Polars, Python web, R, Rust, Scala/Spark, Spark deployment, statistics/ML, Swift, and TMB modeling. Treat this as a course-inventory check, not a promise that every lesson needs an identical activity or runtime.

## Table Stakes

Features users expect from a serious beginner classroom. In this overhaul, “table stakes” means necessary to meet the project's all-tracks quality requirement; it does not mean missing baseline infrastructure.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **A beginner-readable lesson contract in every track** | Self-directed learners need to know what they will be able to do, what they need first, which runtime/data they need, and what completion looks like without an instructor interpreting the page. | Medium | Give each lesson observable, appropriately scoped outcomes; direct prerequisites; essential terms; a short concept explanation; a relevant worked example; practice; and an explained resolution. Keep stable lesson IDs. Use course-specific language and depth rather than copy/pasting Python prose into every track. |
| **A guided, repeatable lesson loop** | Beginners need a bridge from explanation to independent work, not a jump from reading to a blank editor. | High | Make the intended sequence explicit: goal/context → explain one idea → inspect a small working example → predict or reason → run/observe → investigate → make a bounded change → solve a nearby problem → summarize and choose next step. Cycle or omit stages when the subject warrants it; do not force every lesson into a rigid wizard. For non-code lessons, substitute a model, plot, query result, scientific assumption, or system configuration for “source line.” |
| **A substantive worked example with a walkthrough** | A runnable artifact alone demonstrates output but often hides why the steps, assumptions, and intermediate values matter. | High | Explain important lines/cells or conceptual steps, inputs, state/transformation, intermediate result, output, and interpretation. Python and SQL are the quality references, not the only tracks. For code, support a guided walkthrough with readable annotations even when a runtime-specific automatic tracer is not available. For statistics/science, show the question, assumptions, method, diagnostics, and decision/interpretation—not just code. |
| **Practice that ramps from supported to independent** | Novices can be overwhelmed by open-ended code writing before they can recognize or reason about a working solution. | Medium–High | Include at least one check of understanding and a concrete task that changes or applies the example, followed by a less scaffolded transfer task or explicit next step. Select task forms per topic: predict output, trace state, explain a result, fill a missing step, debug a seeded fault, alter an input/assumption, or create a small solution. |
| **Feedback that tells the learner what to inspect next** | A bare “failed” or compiler dump leaves a self-directed beginner without the instructor who would normally interpret it. | Medium–High | Keep raw output available, identify the relevant location or expected/observed difference where possible, and add course-reviewed guidance for frequent misconceptions. Distinguish content/test feedback from runtime failure, timeout, or unsupported operation. Do not silently rewrite learner work or claim a diagnostic explanation is certain. |
| **Predictable desktop lesson operation and recovery** | The learner must move between lesson, editable work, run action, and results without losing the instructional context or saved work. | Medium | Improve the current classroom around a clear “read → do → run/inspect → continue” loop: visible current lesson/activity, recognizable actions, result placement, and a reliable resume point. Preserve drafts and receipts; never treat changing the guided flow as permission to reset stored learner data. Keep the requested desktop target. |
| **Consistent quality coverage across the catalog** | A polished Python/SQL showcase would not satisfy the explicit all-existing-tracks scope. | High | Maintain a track/lesson matrix for objective, prerequisites, explanation, worked example, practice, feedback/answer rationale, runtime or data dependencies, and verification evidence. Mark “not applicable” with a reason; do not let an empty planned lesson count as authored or qualified. |
| **Runnable, bounded lesson artifacts where execution is part of the outcome** | In programming and computational subjects, learners should be able to compare an explanation with real local behavior; other lessons may be deliberately reading-only. | High | Bind runnable work to declared profiles and supported operations. Keep examples reproducible, offline-compatible after runtime preparation, and matched to the track's actual toolchain. A page that teaches a conceptual topic without execution can still be complete if its learning check assesses that concept. |

## Differentiators

Valuable capabilities that can make DS60 unusually effective, but should follow the all-track minimum lesson contract.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Interactive code walkthrough mode** | Lets learners inspect execution instead of treating code as an opaque block. | High | Qualify the current Python/SQL implementation first: tests for trace/planner behavior, bounded execution, result rendering, and edge cases are prerequisites (the codebase concern map identifies missing step-through test coverage). Then extend through explicit per-language adapters or authored walkthrough steps for C-family, Java, JS/TS, R, Julia, Rust, Go, and other executable tracks. A shared UI contract is useful; pretending one parser can explain every language is not. |
| **Prediction → run → explanation reveal** | Turns each code/result example into an inexpensive active check and makes misconceptions visible to the learner. | Medium | Ask for a prediction before revealing output; then explain the difference between prediction and observation. Use carefully authored distractors/questions tied to a specific concept. Keep this low-stakes and allow learners to inspect the answer rather than treating a wrong guess as a grade. |
| **Multiple investigation formats** | Offers a low-friction alternative when free-form coding is too hard, without eliminating the eventual need to write or interpret code. | Medium | Add selected Parsons/code-ordering, missing-line, trace-table, output-prediction, and “find/fix the bug” tasks. Research supports these as useful formats to investigate, not as universally superior replacements for writing code. Use only where answer criteria are unambiguous and feedback can be meaningful. |
| **Analysis-story lessons for data and science tracks** | Helps learners connect methods and commands to valid interpretation, rather than memorizing APIs or producing a plot/model without reasoning. | High | Build selected end-to-end labs around question → data and provenance → assumptions → operation/model → diagnostic or visualization → uncertainty/limitations → interpretation/decision. Reuse small local fixtures and include a deliberate contrast (e.g., a changed assumption or failure case). Particularly relevant to statistics/ML, Bayesian, visualization, scientific, TMB, data engineering, and ML tracks. |
| **Track-aware “what next?” routes** | Gives self-paced learners a route through a large catalog without flattening different subjects into one linear course. | Medium | Explain why a lesson is recommended and which prerequisites it satisfies; offer foundational, applied, and deeper routes where authored content supports them. Respect the existing direct-prerequisite graph and course boundaries. Do not infer mastery solely from page views or run counts. |
| **Visible answer rationale and worked solution variants** | Encourages learners to compare approaches and learn from complete examples without imposing exam anxiety. | Medium | Show a solution with the reasoning, expected intermediate result, and common alternative where appropriate. In scientific topics, explain assumptions and limitations. Do not hide a solution behind a completion gate. |
| **Content-quality checks as a maintained product capability** | Prevents unevenness from returning as lessons are edited across many runtimes and subjects. | High | Pair a human rubric with automated checks for stable IDs/links, declared runtime/profile, example presence, runnable-example probes where practical, and required lesson fields. Automation can detect omissions and regressions, not certify pedagogical quality or scientific validity. |

## Anti-Features

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Python/SQL-only overhaul** | It directly conflicts with the owner's explicit all-existing-tracks scope. | Use Python and SQL as reference implementations, then track parity and deliberate exceptions across every catalog root. |
| **One universal automatic stepper/parser for every language and subject** | Syntax, runtime semantics, SQL dialects, notebooks, statistical interpretation, and infrastructure workflows are not one tracing problem. Incorrect walkthroughs damage trust. | Share the interaction contract, but use tested runtime-specific adapters, carefully authored steps, or non-code conceptual walkthroughs according to what each lesson can safely explain. |
| **Blank-page-first exercises or copy/paste presented as instruction** | It adds syntax and typing burden before learners have a model of what the code does; the activity alone does not teach interpretation. | Begin with a short explained artifact, prediction or observation, then scaffold modifications and fade support toward independent work. Retain appropriate code-writing practice. |
| **Gamified completion as a proxy for learning** | Streaks, badges, page completion, or one green test can reward navigation rather than comprehension and can make self-paced exploration feel punitive. | Use transparent objectives and formative evidence; let learners revisit, skip familiar material, and read worked solutions. |
| **Generic feedback or AI-generated “fixes” as the main tutor** | Compiler output alone may be opaque, while an unverified explanation can be confidently wrong, particularly for SQL dialects, statistical assumptions, or complex runtimes. | Keep feedback deterministic and lesson-authored where possible; preserve raw errors and clearly label uncertainty. Treat any future AI help as optional, bounded, and separately evaluated—not a substitute for authored content. |
| **New subject families, shared hosting, or social-classroom scope creep** | These displace the requested work and conflict with the local single-learner product and trusted-local-code boundary. | Improve authored content and operation in existing tracks; keep local Docker/runtime and learner-state guarantees intact. |
| **Testing that deletes or resets learner state** | It undermines the core value of being able to keep work and progress. | Qualify features with disposable test state and verify retained learner data remains untouched. |

## Feature Dependencies

```text
Existing catalog inventory + stable lesson identities
  → per-track quality rubric and completeness matrix
    → authored objectives, explanations, examples, and practice
      → declared runtime/data/operation contracts
        → guided lesson UI, result feedback, and walkthrough behavior
          → automated content/runtime checks + desktop acceptance
            → release qualification

Python/SQL step-through qualification (tests + bounded behavior)
  → shared walkthrough interaction contract
    → per-language adapters or authored traces
      → coverage across other executable tracks

Stable lesson IDs + existing local persistence
  → resumable in-lesson activity state
    → safe navigation and “continue where I left off”
```

Walkthroughs are a content-and-runtime feature, not just a UI toggle. The mapped architecture distinguishes planned from authored lessons and binds authored work to registered runtime profiles; keep those contracts explicit. Do not encode arbitrary shell commands in curriculum manifests.

## MVP Recommendation

Prioritize:

1. **Catalog-wide content audit and lesson contract.** Inventory every existing track and identify concrete gaps against the same beginner-facing rubric. Preserve IDs and distinguish authored, planned, and intentionally reading-only lessons.
2. **Guided lesson operation.** Establish the desktop pattern for objective/context, worked example, learner action, result interpretation, and next step. Preserve drafts, progress, and run evidence.
3. **Qualify Python/SQL walkthroughs as the reference.** Add focused automated coverage for trace/planning, response, and edge cases before expanding the pattern. Make the reference explain code behavior, not merely highlight a line.
4. **Fill the all-track minimum.** Improve one representative sequence per current programming/data/science course family, then close the per-lesson coverage gaps. Adapt exercise type and example semantics to each subject.
5. **Add formative practice and understandable feedback.** Start with reviewed, deterministic checks and explanations; use Parsons/debugging/fill-in activities selectively.
6. **Verify consistency.** Run content checks, applicable profile/runtime probes, saved-state checks, and bounded desktop review before calling a track complete.

Defer: adaptive sequencing based on inferred mastery, social/classroom features, general-purpose AI tutoring, new subject families, and a universal auto-tracer. Add them only after the course-wide content floor and evidence of a concrete learner need.

## Sources

- **PRIMM research project and materials** (research team; page includes framework steps, study history, and publications; current project page accessed 2026-11-23). Useful for programming lesson sequencing; its main quasi-experimental study was school-aged learners, so transfer to adult self-study is plausible but not established here. **Confidence: MEDIUM.** [Project page](https://computingeducationresearch.org/projects/primm/) · [2019 study DOI](https://doi.org/10.1080/08993408.2019.1608781)
- **The Carpentries, “Preparing to Teach”** (updated 2026-06-01). Supports explicit novice-level, assessable objectives and planning checkpoints for formative assessment. Instructor/workshop guidance, not a direct study of this product. **Confidence: MEDIUM.** [Lesson](https://carpentries.github.io/instructor-training/18-preparation)
- Thangaraj, Ward & O’Riordan, **“A Systematic Review of Formative Assessment to Support Students Learning Computer Programming”** (ICPEC 2023; reviews 17 peer-reviewed articles from 2013–2023). Relevant to feedback/check design; authors note a relatively small evidence base and that most studies were in higher education. **Confidence: MEDIUM.** [DOI and open abstract](https://doi.org/10.4230/OASIcs.ICPEC.2023.7)
- Ericson et al., **“Parsons Problems and Beyond: Systematic Literature Review and Empirical Study Designs”** (ITiCSE Working Group Reports 2022). Supports constrained code-ordering practice as one option while documenting evidence gaps. **Confidence: MEDIUM.** [Aalto open-access record](https://aaltodoc.aalto.fi/items/a77c8afa-0f57-4ef6-85d2-4f982776677c) · [ACM DOI](https://doi.org/10.1145/3571785.3574127)
- Barba et al., **Teaching and Learning with Jupyter** (2019). Community handbook covering narrative plus executable code/output, lesson writing, assignments, assessment, and active learning for computational teaching across science and other fields. Useful pattern reference; older publication. **Confidence: MEDIUM.** [Open book](https://jupyter4edu.github.io/jupyter-edu-book/index.html)
- **DS60 project context** (checked 2026-11-23): `.planning/PROJECT.md`, `.planning/codebase/ARCHITECTURE.md`, and `.planning/codebase/CONCERNS.md`. These define scope, existing product capabilities/architecture, and the untested Python/SQL step-through risk. **Confidence: HIGH for repository context; not external efficacy evidence.**
