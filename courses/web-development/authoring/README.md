# Reproducible web curriculum authoring

`chapters.json` owns the 60 stable chapter specifications: prose, vocabulary,
worked snippets, exercise prompts and explanations, direct prerequisites and
references. `templates/` owns the complete answer-free HTML/PHP starters and
separate executable references. Templates are ordinary formatted source files,
not encoded strings hidden inside a generator. The optional HTTP fixture is
maintained directly under `../fixtures/php-http-lab/`.

From the repository root:

```sh
python courses/web-development/authoring/build.py
python courses/web-development/authoring/build.py --check
```

The build writes guides, published starters, references, explanatory solutions,
`track.json`, `lessons.json` and `fixtures/reference-inventory.json`. It uses
UTF-8 and LF newlines, performs no network or engine operations and never
writes learner state. Check mode is read-only and compares exact bytes.

When editing executable code, edit its template and regenerate. Apply the
repository formatting tool to **both** template and published source files.
Both paths have the same extension and formatting contract, so generation
checks remain exact after formatting. Do not invent whitespace-insensitive
source comparisons, relax a test or label a stale reference as executed.
Embedded worked snippets in prose remain intentionally authored teaching text.

```sh
./scripts/format-repo --language web --language php
python courses/web-development/authoring/build.py --check
./scripts/lint-repo
python scripts/check_modules.py
python scripts/check_content_rendering.py
python -m pytest -n 4 --dist loadgroup tests/test_web_development.py
```

Use `./scripts/format-repo --list` to inspect the current toolchain names and
coverage before adding a new artifact type. The root release process also
regenerates shared readers and validates links. Do not hand-edit generated
reader pages.

## Evidence contract

Each reference marker is `<lesson-id> reference checks passed`. It follows
explicit checks of the supplied fixture, not a guarantee of all behavior.
The inventory contains expected observations and no fabricated runtime result.
PHP references need actual execution in the prepared `php-cli` worker. The
SQLite examples use `sqlite::memory:` and cannot prove the classroom's
PostgreSQL behavior or persistence. Browser references need actual HTML preview
execution plus interaction, narrow-width, zoom and keyboard observations.

Run optional browser acceptance only against disposable learning state. A
saved browser observation must remain distinct from trusted backend execution,
and opening history must not replace a newer draft. The HTTP fixture has its
own local acceptance sequence and limitations. Never publish session tokens,
private browser state or machine-specific logs as curriculum evidence.

## Scope decisions

HTML and CSS share a document workflow, so they are taught together in one
subject. The artifact language is HTML even when a chapter concentrates on
embedded CSS. PHP remains a distinct worker and language. HTTP server design,
file uploads, email and production deployment are deliberately not hidden
behind a CLI Run button. The project capstone connects these layers through
explicit integration and retains references to deeper JavaScript/D3, SQL and
Docker routes.

## Actual browser acceptance

After starting a classroom with disposable learning state and preparing the repository browser-test environment, run:

```sh
python courses/web-development/authoring/check_browser.py --url http://127.0.0.1:PORT --confirm-disposable --report work/web-browser-report.json
```

Replace PORT with that disposable server's actual loopback port. The script writes test drafts and observations, so do not point it at a learner's saved classroom. It checks all 30 references, real interactions, narrow layout, HTML/PHP pad separation, reload behavior, native script/lifecycle semantics and the retained preview isolation. It does not build or start a server.
