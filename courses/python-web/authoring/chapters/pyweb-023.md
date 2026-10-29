## Starting point and result

A web application needs operational commands as well as request handlers. Schema initialization, migrations and maintenance should have explicit entrypoints and observable results. This chapter exercises a real Flask CLI command and a real Alembic schema operation against an owned temporary SQLite database.

## Mechanism: commands and migrations have different responsibilities

The `initialize` CLI command creates the initial table if absent. Flask's CLI runner invokes the actual registered command and captures its outcome. Running it twice verifies this specific initialization's idempotent behavior.

A migration changes an existing schema while preserving the intended data contract. The program creates an Alembic MigrationContext and Operations object on a real connection, then adds a nonnullable boolean column with a server default. Existing rows can receive the default without being dropped or reconstructed by unrelated application code.

This is an operation-level probe. A complete Alembic project also maintains revision files, a version table, environment configuration and an ordered revision graph. The owned application workshop supplies that larger lifecycle. Executing one add-column operation does not establish that revision history, upgrade coordination or rollback has been qualified.

## Worked case: repeat a named initialization command

The test runner invokes `initialize` twice and requires both invocations to succeed. It then inserts an existing row through a parameterized statement. The setup is explicit and local; it does not depend on a previous chapter having created a database.

Idempotence should be evaluated for the command's actual effect. A create-if-absent statement does not guarantee that an already existing table has the expected complete schema. A production startup should verify compatibility rather than assuming that an object with the right name has the right columns and constraints.

## Worked case: evolve the schema without losing the row

The migration operation adds `active` with a true default. A subsequent query sees the original title and active value one, and the schema inspector sees the expected three columns. The assertions therefore cover both data preservation and the resulting shape.

Adding a column is not always operationally cheap on every database/version or with every default. Large tables, locks, backfills and rolling deployments need a planned compatibility strategy. SQLite behavior here must not be silently generalized to a live PostgreSQL deployment. The workshop's actual database operations have separate acceptance.

## Failure diagnosis

A command that works manually but fails under the deployment runner may depend on the wrong configuration, working directory or database credentials. A migration that succeeds on an empty test database can still fail against realistic existing values. Include representative old rows and relevant constraints in migration tests.

Avoid running destructive schema resets as a routine error-recovery step. They can hide a migration defect by deleting the evidence and the learner's data. Versioned evolution, explicit ownership and retained backups are more useful than assuming every database is disposable.

## Interview discussion

**Is `create_all` or create-if-absent a migration system?** It can create missing structures in a bounded scenario, but it does not by itself describe every transition between historical schema versions or manage a reviewed revision graph.

**Can a migration have a successful SQL exit and still be unsafe for a rolling deployment?** Yes. Old and new application processes may coexist. Their read/write assumptions must remain compatible during the transition, including any backfill period.

## Next step

Define how the application depends on an upstream HTTP service. Tests should reproduce success, timeout and failure translation without accidentally contacting an uncontrolled external system.
