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

## Run the starter

```powershell
# Windows PowerShell, from the repository root
.\.venv\Scripts\python.exe bridge\lessons\day01_config_logging_cli.py
```

```bash
# macOS/Linux, from the repository root
.venv/bin/python bridge/lessons/day01_config_logging_cli.py
```

The starter deliberately does not call unfinished functions.

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
2. **Security:** Implement `redact_database_url()` so diagnostics retain scheme, user, host,
   port, and database but remove password, query, and fragment.
   - **Progressive hint:** Parsing components is safer than replacing substrings in an opaque
     secret.
3. **Implementation:** Implement `build_parser()` with `--database-url`, `--log-level`, and
   `--dry-run` without reading global process state during parser construction.
   - **Progressive hint:** Parser construction and argument parsing are separate
     responsibilities.
4. **Integration:** Implement `main(argv)` so it parses the supplied sequence, loads settings,
   configures logging, and emits only a safe summary.
   - **Progressive hint:** A testable CLI accepts an argument sequence instead of rewriting
     `sys.argv`.
5. **Testing:** Create a table-driven test matrix for defaults, CLI precedence, mixed-case
   levels, invalid levels, malformed URLs, credentials, and a missing URL.
   - **Progressive hint:** Include both successful values and exact failure types; assert
     secrets are absent from all diagnostics.
6. **Prediction:** Predict the result when the environment says `WARNING`, the CLI supplies
   `debug`, `dry_run=True`, and no database URL exists; then verify it.
   - **Progressive hint:** Apply precedence independently per setting rather than treating one
     source as an all-or-nothing bundle.
7. **Debugging:** Repair a redactor that catches parse errors but returns `f'invalid:
   {database_url}'` and explain why the exception path is still a leak.
   - **Progressive hint:** Failure messages are an output boundary and need the same secrecy
     rule as normal logs.
8. **Design:** Add configuration provenance such as `cli`, `environment`, or `default` without
   storing or logging the selected secret value twice.
   - **Progressive hint:** Metadata about a source can be safe even when the source value is
     not.
9. **Security testing:** Use a recording logger or `caplog` to prove that startup, success, and
   validation-failure paths contain no password, query token, or full URL.
   - **Progressive hint:** Test the emitted boundary, not only the return value of the redaction
     helper.
10. **Portability:** Write equivalent Windows PowerShell and POSIX invocations that set
   environment values outside Python and pass CLI overrides through `argv`; identify what
   remains platform-neutral.
   - **Progressive hint:** Environment-setting syntax differs, but `argparse`, `Mapping`, and
     the Python entry point do not.

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

## Next step

Continue to [Day 2](day02_protocols_context_decorators.md), where Protocols and
context managers isolate concrete database resources. After attempting the
exercises, compare reasoning in
[the Day 1 solution notes](../solutions/day01_solutions.md).
