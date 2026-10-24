# C subject guidance

Read the root AGENTS.md, content contract and add-learning-path skill before
editing. This subject owns courses/c. Stable IDs are c-001 through c-042.
Language c uses the c17 Linux Docker profile and one staged main.c. Preserve
separate learner source, reference, explanation and saved-state namespaces.

Durable content lives in authoring/foundations.py, composition.py and systems.py.
authoring/render.py derives guides, starters, checked references, track.json and
lessons.json. Regenerate with authoring/build.py and clang-format 21.1.8 available.
The optional C_LESSON_FORMATTER variable selects an explicit formatter command;
never embed a developer machine path in maintained source.

Each lesson has six genuinely distinct tasks, expected observations, executable
checks and explanatory answers. The first two are worked examples. Keep starters
answer-free and tutor prompts lesson-specific. No em dashes in authored prose.

Never execute undefined behavior to demonstrate why it is invalid. Explain the
bad expression as text and run a defined alternative or safe regression. Check
allocation-size arithmetic before allocation, preserve output on rejected
operations, and make ownership and release explicit. Do not use asserts as a
production input-validation substitute. References use an always-on CHECK helper, independent of NDEBUG, so required
operations and checks cannot disappear in a release-style build.

Separate ISO C17, POSIX and compiler-specific capabilities. Pthreads, pipes and
descriptors are Linux-container capabilities; native Windows is not a backend
target. Sanitizers and multi-file Make projects are explicit prepared contributor
workflows, not capabilities implied by the one-file pad. Never add arbitrary
flags, host paths, package downloads or external services to a lesson manifest.

The fixture under fixtures/stats-project is directly authored and has a public
header, checked arithmetic implementation, executable, tests and Makefile. Keep
its build products ignored and validate in a disposable build directory. Do not
delete unrelated resources or learner progress during qualification.

Compile changed references with strict warnings, execute their assertions and use
sanitizers for memory-sensitive changes when available. Report local compiler,
actual Linux-worker, sanitizer and browser evidence separately. A passing run is
not a proof that every possible C input or platform is safe.
