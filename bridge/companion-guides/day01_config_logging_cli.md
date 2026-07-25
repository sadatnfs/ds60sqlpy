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

1. Implement `load_settings()`. Normalize log levels to uppercase, accept only
   the five declared values, and keep a missing database URL as `None`.
2. Implement `redact_database_url()`. Preserve only enough information to
   identify the scheme, user, host, port, and database. Remove the password,
   query string, and fragment. Return a safe generic marker for malformed or
   non-URL input.
3. Implement `build_parser()` with `--database-url`, `--log-level`, and
   `--dry-run`.
4. Add a `main(argv)` that parses the supplied sequence, loads settings, and
   logs a safe summary. Do not log the `Settings` object directly.
5. Test environment defaults, CLI precedence, mixed-case levels, invalid
   levels, a password-containing URL, a malformed URL, and a missing URL.

### Progressive hints

1. Start with a frozen `dataclass`.
2. Keep normalization in a small helper so invalid input has one error path.
3. `urllib.parse.urlsplit()` understands URL components; parsing alone is not
   validation.
4. Pass `argv` to `ArgumentParser.parse_args()` instead of changing `sys.argv`.

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

