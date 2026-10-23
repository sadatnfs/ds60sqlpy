# JavaScript and TypeScript authoring

All 42 stable lesson bundles have portable specifications. `specs.py` contains 001-009, `intermediate.py` 010-018, `typed.py` 019-024, `typed_advanced.py` 025-028, `browser.py` 029-031, `advanced.py` 032-037 and `applications.py` 038-042. `render.py` keeps guides, answer-free learner sources, executable references and explanatory solutions aligned. `browser_fixtures.py` creates only the checked-in starter and separate completed browser trees, never learner copies.

Run `python courses/javascript-typescript/authoring/build.py` from the repository root. It preserves stable plan IDs and runtime contracts. Raw Python strings preserve JavaScript/TypeScript backslash escapes; code containing nested child programs needs particular care. Parse references and worked programs, compile TypeScript with the pinned strict NodeNext flags, then execute in the prepared runtime. Browser behavior requires a real browser session.

The fixture READMEs use the prepared Docker image with --pull never, read-only mounts of new learner copies and separate loopback origins. No authoring script installs packages, downloads models or changes a runtime image. Implementation status and runtime receipts remain in `docs/implementation/javascript-content-status.md`.
