# Reproducible Rust authoring

Run `python courses/rust/authoring/build.py` from the repository root. Only the Python standard library is needed for generation. The original specifications are foundations.py, composition.py and advanced.py. render.py writes the route, manifest, guides, unfinished learners and separate references/explanations as UTF-8 with LF.

Specification order defines stable rust-001 through rust-048 IDs. Do not reorder or renumber published lessons. Each stage contains sixteen chapters. Additive work needs a reviewed stable-ID strategy. The generator touches only this subject and never generates shared HTML.

Verify reproducibility by hashing the generated artifacts, rerunning build.py and comparing hashes. Project fixtures are directly authored source, not generator output. Reference compilation must use the pinned Rust/Arrow worker; a host compiler without the prepared Arrow library cannot qualify those chapters.

Every reference checks both worked scenarios with always-active assertions. Independent and transfer tasks can admit several designs, so explanations focus on invariants and diagnostic reasoning. Do not present printed markers as automatic mastery verification. Use real malformed, null, boundary and ownership cases rather than weakening an assertion to get a pass.
