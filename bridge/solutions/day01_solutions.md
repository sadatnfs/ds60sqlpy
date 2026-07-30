# Bridge Day 1 — Solution notes

Use these notes after attempting the
[learner file](../lessons/day01_config_logging_cli.py). The executable reference
is [day01_solution.py](day01_solution.py).

## Design

The reference turns external strings into one frozen `Settings` object. It
accepts an environment `Mapping` and explicit keyword values, so precedence is
visible and tests need not patch process-global state. `parse_log_level()` owns
normalization and validation.

The command-line parser is created by a function, and `main()` accepts an
argument sequence. That makes the same boundary usable from a real process and
a test.

## Why redaction is separate

The full database URL is needed for connection but must not flow into logs.
`redact_database_url()` uses URL components and removes the password, query, and
fragment. Malformed and non-URL forms get a generic marker rather than a best
effort echo. `settings_summary()` is an explicit allowlist of safe fields.

## Tradeoffs

- A frozen dataclass is simple and dependency-free. A larger application might
  use a configuration library for nested settings and richer error reporting.
- The URL redactor targets the documented URL form. Libpq keyword/value DSNs
  receive a generic marker; correctly parsing and safely re-rendering them
  belongs in a driver-aware utility.
- Missing `DS60_DATABASE_URL` is allowed because the course runs offline. A
  live adapter should reject `None` at the point it opens a connection.
- `logging.basicConfig()` is adequate for one CLI. A library should not
  configure global logging on import.

## Edge cases worth testing

- whitespace and mixed-case log levels;
- URL-encoded usernames and IPv6 hosts;
- malformed ports;
- passwords and query parameters containing recognizable secret text;
- no database URL;
- CLI values overriding environment values.

The important invariant is not the exact redacted string. It is that no secret
substring can appear and malformed input is never reflected into output.

## Exercise solutions

These walkthroughs align one-for-one with the learner and guide. The executable
reference is `bridge/solutions/day01_solution.py`; use it only after an honest attempt.

**Shared failure rule:** Configuration objects and exception text can expose passwords just as easily as an explicit print statement.

### Exercise 1 — Implementation

**Prompt:** Implement `load_settings()` with CLI-over-environment precedence, uppercase
log-level normalization, and `None` for a missing URL.

**Approach:** Select the explicit argument when it is not `None`, otherwise read the matching
environment key. Pass the chosen level through one normalizer and construct the frozen
`Settings`; do not invent a placeholder URL.

**Why this boundary matters:** Resolve each source once, then validate the final selected value
at the boundary.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 2 — Security

**Prompt:** Implement `redact_database_url()` so diagnostics retain scheme, user, host, port,
and database but remove password, query, and fragment.

**Approach:** Use `urlsplit`, rebuild only approved components, replace any password with `***`,
and omit query and fragment entirely. Malformed or non-URL input returns a fixed marker that
contains none of the original text.

**Why this boundary matters:** Parsing components is safer than replacing substrings in an
opaque secret.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 3 — Implementation

**Prompt:** Implement `build_parser()` with `--database-url`, `--log-level`, and `--dry-run`
without reading global process state during parser construction.

**Approach:** Create an `ArgumentParser`, register three options, and return it. Keep defaults
neutral so `load_settings()` can apply environment fallback after parsing.

**Why this boundary matters:** Parser construction and argument parsing are separate
responsibilities.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 4 — Integration

**Prompt:** Implement `main(argv)` so it parses the supplied sequence, loads settings,
configures logging, and emits only a safe summary.

**Approach:** Call `parse_args(argv)`, pass parsed values into `load_settings`, configure the
selected level, and log a summary produced from redacted fields. Return a status code and never
log `Settings` directly.

**Why this boundary matters:** A testable CLI accepts an argument sequence instead of rewriting
`sys.argv`.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 5 — Testing

**Prompt:** Create a table-driven test matrix for defaults, CLI precedence, mixed-case levels,
invalid levels, malformed URLs, credentials, and a missing URL.

**Approach:** Parameterize environment/CLI combinations and expected `Settings` or `ValueError`.
For URL cases, assert the permitted label and separately assert that password, query, fragment,
and malformed input never appear.

**Why this boundary matters:** Include both successful values and exact failure types; assert
secrets are absent from all diagnostics.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 6 — Prediction

**Prompt:** Predict the result when the environment says `WARNING`, the CLI supplies `debug`,
`dry_run=True`, and no database URL exists; then verify it.

**Approach:** The result is `database_url=None`, `log_level='DEBUG'`, and `dry_run=True`: the
explicit level overrides only its environment counterpart, while the absent URL stays absent.

**Why this boundary matters:** Apply precedence independently per setting rather than treating
one source as an all-or-nothing bundle.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 7 — Debugging

**Prompt:** Repair a redactor that catches parse errors but returns `f'invalid: {database_url}'`
and explain why the exception path is still a leak.

**Approach:** Replace the echoing branch with a constant such as `<invalid-database-url>`. A
parser failure does not make the original string safe; it may still contain a credential or
token.

**Why this boundary matters:** Failure messages are an output boundary and need the same secrecy
rule as normal logs.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 8 — Design

**Prompt:** Add configuration provenance such as `cli`, `environment`, or `default` without
storing or logging the selected secret value twice.

**Approach:** Track a small enum or literal beside each resolved setting, and expose provenance
only through the safe summary. Keep the URL in one field and redact at presentation time rather
than copying it into provenance records.

**Why this boundary matters:** Metadata about a source can be safe even when the source value is
not.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 9 — Security testing

**Prompt:** Use a recording logger or `caplog` to prove that startup, success, and
validation-failure paths contain no password, query token, or full URL.

**Approach:** Run the CLI with sentinel secret fragments, capture every log record, join
messages and exception text, and assert each sentinel is absent. Also assert a useful safe
database label is present on success.

**Why this boundary matters:** Test the emitted boundary, not only the return value of the
redaction helper.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.

### Exercise 10 — Portability

**Prompt:** Write equivalent Windows PowerShell and POSIX invocations that set environment
values outside Python and pass CLI overrides through `argv`; identify what remains
platform-neutral.

**Approach:** Use `$env:NAME = ...` in PowerShell and `export NAME=...` in a POSIX shell, then
invoke the same `python -m ... --log-level ...` arguments. The parser and precedence tests stay
platform-neutral because they use injected mappings and sequences.

**Why this boundary matters:** Environment-setting syntax differs, but `argparse`, `Mapping`,
and the Python entry point do not.

**Evidence:** Capture exact calls, returned values, exception types, and
cleanup order. Re-run the case and require the same fake-backed result;
keep live PostgreSQL evidence separately labeled and opt-in.
