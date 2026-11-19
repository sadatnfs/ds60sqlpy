# Product

<!-- impeccable:product-schema 1 -->

Facts below come from the repository (README.md, AGENTS.md, docs/, the classroom
code and the course catalog). Items marked "(inferred)" were not confirmed by the
maintainer and should be reviewed.

## Platform

web

## Users

- Self-directed adult learners studying programming, data science, statistics,
  machine learning and systems on their own computer, usually one lesson at a time
  in sessions of 15 to 90 minutes (the classroom offers 15/30/60/90 minute session
  estimates).
- Beginners start with Python and PostgreSQL; experienced engineers jump straight
  to a specialist subject such as Kubernetes networking, CUDA or Spark internals.
  (inferred from the subject order and the "start here" on-ramps)
- Contributors and maintainers who author lessons and runtimes use the same
  classroom through `ds60 serve`.

## Product Purpose

DS60 is one local classroom for about 40 subjects and roughly 1,800 lessons and
tutorial chapters. Each lesson pairs a written guide and worked examples with a
code editor connected to a prepared Linux Docker runtime, so a learner can read,
predict, run and explain without installing language toolchains. Success means a
learner can open a lesson, understand it, run real code, see a trustworthy result
and keep their work across restarts.

## Positioning

Everything runs locally and offline after preparation: lessons, runtimes,
PostgreSQL and saved work live on the learner's machine in Docker volumes. Results
are tied to the exact source that produced them, and reading a past result never
reruns it. Practice lessons separate hints and reference solutions from the
learner's attempt; tutorial books expose complete worked answers.

## Operating Context

- Started with `./classroom` (macOS/Linux terminal, Windows via WSL 2); opened in
  a desktop browser at a loopback URL ending in `/classroom`.
- Typical screen: a laptop or desktop browser; mobile is a supported fallback for
  reading. (inferred)
- Learners move between the subject catalog, a lesson guide, the editor, run
  results, saved run history and notes.
- Offline rendering: bundled fonts, KaTeX math and syntax highlighting; no CDN.

## Capabilities and Constraints

- One browser application at `/classroom`; no second UI may be added.
- Subjects carry a stable id, a title, a summary and a per-subject color theme with
  a short text mark (for example `Py`, `SQL`, `K8s`); color never identifies a
  subject alone.
- Lesson identities, prerequisites, saved drafts and run receipts are stable and
  must not change when the interface changes.
- Execution profiles differ: worker jobs, bounded Python/SQL runs, browser
  previews (HTML/CSS, JavaScript/D3), read-only tutorial chapters and an offline
  DAX desk without a Run action.
- Strict Content Security Policy: scripts and styles from the app origin only; no
  external network requests from the page.
- Keyboard shortcuts in use: Ctrl/Cmd+S saves, Ctrl/Cmd+Enter runs, Escape then
  Tab leaves the editor.

## Brand Commitments

- Name: DS60 Classroom. Mark: the italic "d." monogram.
- Voice: professional and factual; no motivational slogans or growth metaphors
  (docs/content-authoring.md). No em dashes in repository text.
- Lesson prose uses textbook typography with compiled TeX math.

## Evidence on Hand

- The full course catalog, lesson guides, worked examples and reference
  solutions under `courses/`, `python/`, `sql/` and `bridge/`.
- No testimonials, user counts, benchmarks or endorsements exist; do not invent
  them.

## Product Principles

1. The lesson and the learner's work stay side by side; the interface never hides
   the code while the learner reads, or the result after a run.
2. Saved work is sacred: navigation, reloads and layout changes never discard a
   draft or rerun code.
3. Show actual capability: say plainly what runs, what is read-only and what needs
   preparation.
4. Offline and local by default; nothing loads from the network.
5. One classroom for every subject, each recognizable by name and mark, not by
   color alone.

## Accessibility & Inclusion

- Keyboard-operable everywhere, visible focus, a skip link and live status
  regions already exist and must be preserved.
- Text contrast meets WCAG AA (the UI test harness enforces 4.5:1 for subject
  accents and 7:1 for the console) in light and dark appearances.
- Respect reduced-motion preferences.
