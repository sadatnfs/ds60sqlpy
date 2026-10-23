# The journey and teacher experience

Status: interactive design prototype. Open `/journey-preview` in the learning app. The preview reads the five validated plans and provides real prediction feedback, incremental hints, and local draft recovery. Runtime execution, mastery grading, and job orchestration remain future implementation.

## Learner journey

The starting screen asks what the learner wants to build and shows five subject paths with beginner, intermediate, and advanced outcomes. Each track exposes its actual planned lessons, estimated lesson time, prerequisites, concrete lab, and verification method. Stage labels describe increasing independence, not a promise that every learner needs the same number of days.

Entry should be selective. C++ and Kubernetes teach their own first steps. Scala offers a language-first route, with Python prerequisites attached to PySpark exercises. Mathematical Python tracks offer a short diagnostic and relevant foundation lessons rather than requiring every previous production or geospatial module. A recommendation explains its prerequisite relationship and allows the learner to review or self-assess an equivalent skill.

In a future published journey, the home screen will offer Continue, Review, and Explore. Continue resumes the exact exercise and draft; Review presents a changed retrieval problem; Explore shows prerequisites and profile readiness. Optional study-time planning uses actual selected lessons and completed prerequisites. Never equate elapsed time, revealed answers, or clicked checkboxes with understanding.

## Lesson workspace

Desktop uses a path rail, a teaching area, and evidence/context panels. Mobile collapses into a single readable column with ordinary navigation. Avoid hiding instructions behind the editor. The learner should always know the purpose, current step, next action, and whether work has saved.

The teaching sequence is Understand, Predict, Experiment, Inspect, Explain, and Review. A small worked example and a question precede the coding surface. Prediction feedback explains a misconception after a committed answer. Experiment offers a prepared fixture, starter code, and progressive hints. Inspect distinguishes expected output from actual runtime results and links each verifier check to the relevant concept. Explain uses a visible rubric. Review changes the context so recalling an answer is insufficient.

The preview implements the navigable sequence and pilot reasoning questions. Its code pane contains starter or reference code, with no Run button. Expected observations are labelled, and a correct prediction is labelled a reasoning result. A local explanation draft and selected step survive a reload where browser storage is available. Preview storage is separate from real course progress, and can be reset without changing `.learning`. When storage is unavailable, the interface must say that the draft is unsaved.

The eventual coding workspace needs line numbers, language-aware highlighting, indent/comment shortcuts, keyboard-accessible resizing, diagnostic links, undo, autosave status, a reset-to-starter action with draft protection, and separate stdout, stderr, artifacts, and checks. Long jobs show queue position, phase, elapsed time, cancellation, and actual bounded logs. Profile preparation belongs before execution; a disabled action explains what is missing.

## Feedback without misleading signals

Use separate labels for planned content, runtime readiness, machine verification, learner explanation, and self-reported completion. Green should not mean both "I read this" and "all tests passed." A failed build, missing image, numeric mismatch, and weak explanation need different next steps. Preserve learner code after failure. Show uncertainty explicitly when a machine cannot judge an explanation.

Do not add an AI tutor as a prerequisite. The existing MCP path can later expose course context, planned next steps, hints, and bounded job status using the same typed backend contracts. Execution and state changes remain explicit, scoped actions. Model access, privacy, and optional network costs require a separate design; the offline teacher remains useful by itself.

## Visual system and accessibility

Use semantic tokens for canvas, surface, text, muted text, borders, focus, action, planned, warning, and success. The prototype uses a warm neutral canvas and restrained forest-green accents, clear typography, and no network fonts or decorative image dependencies. Reuse components for path cards, stage selectors, teaching steps, evidence panels, notices, and hint disclosures. Adapt to narrow screens, reduced motion, and browser zoom.

Prefer native controls. Every form field has a label, every status change is announced without stealing focus, and keyboard focus stays visible. Use buttons with `aria-pressed` for simple mutually exclusive filters. If implementing true tabs, follow the ARIA tab pattern, including arrow keys, Home/End, focus management, and labelled panels; do not add tab roles without the behavior. [W3C tab pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)

Target WCAG 2.2 AA, including contrast, keyboard access, meaningful names, zoom/reflow, and no color-only feedback. Design for at least 44px practical touch targets, while recording the applicable WCAG criterion separately. Automated checks cannot prove screen-reader usability. Review task completion with keyboard and a screen reader, especially after changing the active lesson or revealing a hint. W3C's guidance distinguishes focus from selection and describes predictable keyboard behavior. [W3C keyboard interface guidance](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)

## User studies before large-scale authoring

Ask a newcomer to choose a path, understand a prerequisite, predict a result, use one hint, explain a failed check, resume after reload, and identify what has actually been verified. Observe without prompting. Record confusion and time to a useful first result, then improve one vertical slice before copying its pattern into hundreds of lessons. Include learners using Windows/WSL2, smaller laptops, keyboard navigation, and no prior Python or Docker experience.
