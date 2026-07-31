# Bridge Day 1 — Configuration, logging, and typed CLI boundaries

**Level:** Intermediate  
**Prerequisites:** [Python Day 15](../../python/ds-60day/companion-guides/day15_cli_project.md)
and [SQL Day 15](../../sql/postgres-60day/companion-guides/day15_phase1_project.md)

## Why this matters

Database programs fail early when configuration is ambiguous and fail
dangerously when diagnostics reveal credentials. Today you will build one
boundary that turns untrusted command-line strings and environment variables
into a small, validated `Settings` object. Code inside the application can then
rely on that object instead of repeatedly reading global process state.


<!-- BEGIN BRIDGE ENRICHMENT: HOW TO RUN -->
## How to run this lesson

Start at the repository root. The answer-free starter is deliberately safe to
run: it prints orientation text and does not call unfinished functions or
contact PostgreSQL.

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe bridge\lessons\day01_config_logging_cli.py
.\.venv\Scripts\python.exe -m pytest bridge\tests -q
```

```bash
# macOS/Linux
.venv/bin/python bridge/lessons/day01_config_logging_cli.py
.venv/bin/python -m pytest bridge/tests -q
```

Read this guide first, implement one boundary at a time in
`bridge/lessons/day01_config_logging_cli.py`, and use small fakes or recording doubles for the
default evidence path. Any PostgreSQL step is optional, explicitly gated, and restricted to `DS60_DATABASE_URL` plus the disposable `advanced_sql_training` database. Never place a credential in source, notebook output, test fixtures, or logs.
<!-- END BRIDGE ENRICHMENT: HOW TO RUN -->

## Objectives

By the end, you can:

- define a typed configuration object with explicit optional fields;
- apply and test CLI-over-environment precedence;
- reject invalid log levels at the boundary;
- log a useful database label without revealing a password or query parameter;
- make CLI parsing testable without modifying `sys.argv`.

## Vocabulary

| Term | Meaning |
|---|---|
| configuration boundary | The small part of a program that converts external strings into validated internal values |
| environment variable | A named string supplied to a process by its operating system or shell |
| precedence | The documented rule for choosing between multiple configuration sources |
| redaction | Replacing sensitive content with a safe marker |
| immutable | An object whose fields cannot be reassigned after creation |
| exit code | An integer a program returns to its caller; zero conventionally means success |


## Worked example: validate once

This smaller example shows the boundary pattern without solving the database
configuration exercise:

```python
from collections.abc import Mapping


def load_port(environ: Mapping[str, str]) -> int:
    raw = environ.get("APP_PORT", "8000")
    port = int(raw)
    if not 1 <= port <= 65535:
        raise ValueError("APP_PORT must be between 1 and 65535")
    return port
```

Notice that the function accepts a `Mapping`, not `os.environ` directly. A test
can pass a normal dictionary, and all callers receive an `int` or an exception.

For this course, use these settings:

- `DS60_DATABASE_URL`: optional until a live database step;
- `DS60_LOG_LEVEL`: defaults to `INFO`;
- explicit CLI values override their environment equivalents;
- `--dry-run` defaults to false and must never be inferred from a non-empty
  string such as `"false"`.


<!-- BEGIN BRIDGE ENRICHMENT: DEEP DIVE -->
## Mental model: turn strings into trusted state once

Everything outside the program arrives as untrusted text. PowerShell
environment variables, POSIX environment variables, command-line arguments,
and copied connection URLs are all strings, even when they represent a Boolean
or a log level. A **configuration boundary** performs four jobs in a visible
order: collect candidate values, apply precedence, validate and normalize the
chosen values, and return one typed object. The rest of the application should
receive `Settings`; it should not repeatedly consult `os.environ`.

Think about precedence one field at a time. A CLI log level can override the
environment log level while the database URL still comes from the environment
and `dry_run` still uses its default. Treating CLI input as an all-or-nothing
bundle creates surprising missing values. Also distinguish *missing* from
*present but invalid*: no URL is acceptable for this offline starter, while
`DS60_LOG_LEVEL=INF0` is an error that should be reported before any database
work begins.

This tiny example shows the shape without implementing the lesson functions:

```python
from collections.abc import Mapping


def choose_timeout(environ: Mapping[str, str], cli_value: str | None) -> int:
    raw = cli_value if cli_value is not None else environ.get("APP_TIMEOUT", "30")
    timeout = int(raw)
    if timeout < 1:
        raise ValueError("timeout must be positive")
    return timeout


assert choose_timeout({"APP_TIMEOUT": "15"}, None) == 15
assert choose_timeout({"APP_TIMEOUT": "15"}, "5") == 5
```

Secrets require a second boundary. The program may need a complete database URL
to connect, but logs need only a safe label. Redaction should therefore be an
allowlist of components that may leave the process, not a list of substrings
that happen to look secret. Query parameters can contain tokens, fragments can
contain copied diagnostics, and malformed input can still contain a password.
A safe failure marker is more useful than echoing unparseable text.

Finally, parser construction and parser use are separate. `build_parser()`
describes accepted CLI syntax. `main(argv)` parses a supplied sequence and is
therefore testable without mutating `sys.argv`. The real process may pass
`None`; a unit test can pass `["--log-level", "debug"]`. That dependency
injection is the same idea used later for clocks, sleepers, database factories,
and model adapters.
<!-- END BRIDGE ENRICHMENT: DEEP DIVE -->

## Exercises

### Practice contract

- **Focus:** Build one typed configuration boundary that combines environment and CLI input without leaking connection credentials.
- **Assumptions:** CLI values override environment values; a missing database URL remains `None`; log levels are normalized to the five declared values.
- **Primary failure mode:** Configuration objects and exception text can expose passwords just as easily as an explicit print statement.
- **Evidence loop:** predict the boundary, implement the smallest change,
  verify success and failure with a deterministic fake, then explain which
  behavior still requires an explicitly enabled PostgreSQL integration test.

1. **Implementation:** Implement `load_settings()` with CLI-over-environment precedence,
   uppercase log-level normalization, and `None` for a missing URL.
   - **Progressive hint:** Resolve each source once, then validate the final selected value at
     the boundary.
   - **Verify:** Assert that CLI `debug` overrides environment `WARNING`, an absent URL remains `None`, `INF0` raises `ValueError`, and the supplied environment mapping is unchanged.
2. **Security:** Implement `redact_database_url()` so diagnostics retain scheme, user, host,
   port, and database but remove password, query, and fragment.
   - **Progressive hint:** Parsing components is safer than replacing substrings in an opaque
     secret.
   - **Verify:** Use a URL containing sentinel password, query token, and fragment; assert all three sentinels are absent while scheme, username, host, port, and database remain visible.
3. **Implementation:** Implement `build_parser()` with `--database-url`, `--log-level`, and
   `--dry-run` without reading global process state during parser construction.
   - **Progressive hint:** Parser construction and argument parsing are separate
     responsibilities.
   - **Verify:** Assert `parse_args([])` leaves URL and log-level overrides unset with `dry_run=False`; then parse all three flags and compare the exact namespace without reading `sys.argv`.
4. **Integration:** Implement `main(argv)` so it parses the supplied sequence, loads settings,
   configures logging, and emits only a safe summary.
   - **Progressive hint:** A testable CLI accepts an argument sequence instead of rewriting
     `sys.argv`.
   - **Verify:** Call `main()` with an injected argument list and captured logs; assert exit status `0`, the selected level, one redacted database label, and no full URL or password.
5. **Testing:** Create a table-driven test matrix for defaults, CLI precedence, mixed-case
   levels, invalid levels, malformed URLs, credentials, and a missing URL.
   - **Progressive hint:** Include both successful values and exact failure types; assert
     secrets are absent from all diagnostics.
   - **Verify:** Parameterize defaults, each CLI override, mixed-case valid levels, `INF0`, missing URL, malformed URL, and sentinel credentials; compare exact `Settings` or exception types.
6. **Prediction:** Predict the result when the environment says `WARNING`, the CLI supplies
   `debug`, `dry_run=True`, and no database URL exists; then verify it.
   - **Progressive hint:** Apply precedence independently per setting rather than treating one
     source as an all-or-nothing bundle.
   - **Verify:** Write `Settings(database_url=None, log_level='DEBUG', dry_run=True)` before running the case, then assert the returned dataclass equals that prediction.
7. **Debugging:** Repair a redactor that catches parse errors but returns `f'invalid:
   {database_url}'` and explain why the exception path is still a leak.
   - **Progressive hint:** Failure messages are an output boundary and need the same secrecy
     rule as normal logs.
   - **Verify:** Feed malformed text containing `secret-marker`; assert the repaired branch returns a fixed marker such as `<invalid-database-url>` and never includes `secret-marker`.
8. **Design:** Add configuration provenance such as `cli`, `environment`, or `default` without
   storing or logging the selected secret value twice.
   - **Progressive hint:** Metadata about a source can be safe even when the source value is
     not.
   - **Verify:** Show provenance labels `cli`, `environment`, and `default` beside resolved fields while the complete database URL exists in only one field and never appears in the safe summary.
9. **Security testing:** Use a recording logger or `caplog` to prove that startup, success, and
   validation-failure paths contain no password, query token, or full URL.
   - **Progressive hint:** Test the emitted boundary, not only the return value of the redaction
     helper.
   - **Verify:** Capture startup, success, and validation-failure logs with password/query sentinels; assert every sentinel and the full URL are absent and the safe host/database label remains.
10. **Portability:** Write equivalent Windows PowerShell and POSIX invocations that set
   environment values outside Python and pass CLI overrides through `argv`; identify what
   remains platform-neutral.
   - **Progressive hint:** Environment-setting syntax differs, but `argparse`, `Mapping`, and
     the Python entry point do not.
   - **Verify:** Record one PowerShell `$env:DS60_LOG_LEVEL=...` run and one POSIX `export ...` run; assert the same `Settings` values result when identical CLI overrides are supplied.

### Before opening the solution

- State the input/output and ownership boundary in one sentence.
- Show one normal case, one edge case, and one failure case.
- Inspect recorded calls rather than relying on plausible output.
- Confirm no credential, payload, or high-cardinality identifier was emitted.


## Self-check

- Does `load_settings({"DS60_LOG_LEVEL": "warning"})` produce `WARNING`?
- Can a CLI value override the environment without mutating the mapping?
- Does any diagnostic output contain a password or `sslmode` query parameter?
- Does an invalid log level fail before any database connection is attempted?
- Can your tests run without setting real environment variables?

Expected behavior: every accepted setting has a precise internal type, invalid
levels raise a useful error, and redacted output contains no secret substring.

## Common pitfalls

- **Using `bool(raw_string)`:** `bool("false")` is `True`. Let the CLI action
  create a Boolean.
- **Logging `settings`:** dataclass representations include every field unless
  you deliberately exclude or redact it.
- **Silently accepting typos:** treating `INF0` as `INFO` hides operator error.
- **Reading `os.environ` everywhere:** global reads create order-dependent tests
  and unclear precedence.
- **Treating an absent URL as a startup error:** offline exercises do not need a
  database; validate that requirement only at the live-DB boundary.


<!-- BEGIN BRIDGE ENRICHMENT: ASK CODEX -->
## Ask Codex about this lesson

Use the checked-in `guide-ds60sqlpy-learning` skill as a tutor, not as an
answer generator. The direct catalog prerequisites are `python-15`, `sql-15`. The
prompt below deliberately names exact paths so a new Codex task can orient
itself without guessing.

```text
Tutor me through stable lesson ID bridge-01: Config Logging CLI.
Direct catalog prerequisites: python-15, sql-15. Assume I completed exactly those
prerequisites, then begin with one short Retrieval question that connects each
prerequisite to this lesson.

Use repository skill guide-ds60sqlpy-learning.
Companion guide: bridge/companion-guides/day01_config_logging_cli.md
Learner artifact: bridge/lessons/day01_config_logging_cli.py

Do not open, quote, summarize, or copy anything under solutions/ until I
explicitly say I have finished my attempt and ask to compare.

Use these coaching phases in order:
1. Predict — ask what I expect before I run or change code.
2. Attempt — let me implement or explain one numbered exercise at a time.
3. Hint — give the smallest useful conceptual hint, never a finished answer.
4. Evidence — ask for the exact return value, exception type, recorded calls,
   query plus bound parameters, or written decision required by that exercise.
5. Retrieval — close with two no-notes questions and one transfer problem.

Keep the default path offline and fake-first. If the lesson has an optional
PostgreSQL step, require my explicit opt-in, DS60_DATABASE_URL, and the
disposable advanced_sql_training database; never ask me to paste the URL.

Done when every numbered exercise has its own evidence, normal/edge/failure
behavior is explained in my words, the relevant offline tests pass, and I can
solve the final transfer problem without opening solutions/.
```
<!-- END BRIDGE ENRICHMENT: ASK CODEX -->

## Next step

Continue to [Day 2](day02_protocols_context_decorators.md), where Protocols and
context managers isolate concrete database resources. After attempting the
exercises, compare reasoning in
[the Day 1 solution notes](../solutions/day01_solutions.md).
