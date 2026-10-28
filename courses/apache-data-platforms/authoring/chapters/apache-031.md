## A connection reference separates code from deployment values

A connection identifier names configuration that a task can request at runtime.
It can hold endpoint, type, login, credential or extra settings, depending on the
integration. Keeping the identifier in a DAG avoids embedding deployment-specific
values directly into business logic. It does not itself make those values safe
to print or grant the task permission to use every external system.

Airflow can resolve connections from environment variables, metadata storage or
a configured secrets backend. Providers supply integration-specific hooks and
operators. Installing a provider and defining a connection are separate actions:
a connection record cannot create a missing Python package, and an installed
provider cannot invent valid credentials or network access.

The workshop defines a local synthetic connection through its container environment.
It contains a declared fixture name and nonsecret local metadata, with no cloud
credential or external service. The TaskFlow task resolves the actual connection
through the Airflow SDK at execution time, checks its allowed fields and stores
only a redacted bounded observation.

## Worked case A: resolve a known local connection in a task

The connection-check action triggers the fixed connection workflow and waits for
its actual task success. The task requests classroom_fixture, validates the
expected connection type and dataset marker, and records that the reference was
resolved. It does not print the complete connection object or its URI, because
real deployments can place passwords in those representations.

Resolution occurs inside task execution rather than at module import time.
DAG parsing should be quick and repeatable; retrieving a remote secret or opening
a database during parsing adds availability and performance dependencies to the
scheduler's discovery path. The task's runtime failure can then be attributed
to the relevant operation instead of preventing the whole DAG file from loading.

An environment-defined connection may not appear in the metadata UI in the same
way as a database-defined record. That difference does not prove the task cannot
resolve it. Inspect the configured backend and execution environment, while
keeping secret values out of diagnostic logs. A read-only presence check and a
real connection attempt establish different levels of evidence.

## Worked case B: reject a missing connection explicitly

The same bounded task requests an intentionally absent connection identifier.
The SDK must report the expected missing-connection category, which the example
records without revealing unrelated configuration. The task then verifies the
known fixture reference still resolves, ensuring the negative check did not
mutate deployment settings or create an empty fallback.

Silently returning default production credentials or a guessed endpoint would be
unsafe and difficult to debug. A missing configuration value should produce a
clear actionable error tied to its identifier. A network timeout, invalid password
and missing provider are different failure categories and should not all be
reported as connection not found.

Optional integration providers are prepared when building a reviewed environment,
not installed from inside a task because an import failed. Their versions can
constrain Airflow and dependency packages. The hash-locked environment records the selected
provider distributions as preparation evidence, while its actual connection example
uses only the explicitly prepared SDK path.

## Mistakes, diagnosis and interview discussion

Separate configuration lookup, package availability, DNS, transport, authentication,
authorization and query semantics. Masking a printed password does not justify
logging an entire credential object. Restrict tasks to the connection references
they need and keep engine sockets, host cloud credentials and unrelated learner
state out of the workshop container.

**Interview discussion: why not put the database URL directly in every DAG?**
A stable connection reference allows deployment-specific resolution and credential
management without editing business logic, and avoids duplicating sensitive values.
It still needs provider compatibility and access controls. These two actual SDK
lookups establish the intended resolution and rejection behavior without claiming
a synthetic local reference proves a remote production database connection.

The [complete Airflow workshop](../../projects/airflow/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.
