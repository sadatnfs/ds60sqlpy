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

