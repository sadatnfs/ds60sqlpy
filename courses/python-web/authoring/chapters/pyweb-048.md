## Starting point and result

A Django model describes intended data structure in Python, while migrations record how the database schema evolves. This chapter creates a genuine temporary application package, generates its initial migration, applies it and repeats the migration command without losing an existing row.

## Mechanism: migration state is versioned schema history

Django's application registry loads model definitions. Makemigrations compares model state with migration state and writes operations describing the change. Migrate applies the outstanding operations and records which migrations have completed. These are separate steps: editing a model does not automatically alter a deployed database.

The fixture defines a Note with a unique title. The uniqueness rule becomes a database constraint through the generated migration. Application validation can improve user feedback, but only the database can resolve competing writes reliably at the final storage boundary.

The temporary package and database are owned by this finite program. It writes only inside its temporary directory and removes that directory after closing connections. A real project commits reviewed migration files to source control and applies them through a controlled deployment step, not through an arbitrary request handler.

## Worked case: generate, apply and replay an initial migration

The program creates the small package, configures Django to install it and runs makemigrations. It asserts that the initial migration file exists, applies migrations and inserts a row. A second migrate invocation leaves that row intact and produces no outstanding plan for the already applied migration.

This is actual migration execution, not a hand-created table pretending to exercise migrations. Other compact ORM chapters use schema_editor deliberately to focus on queries; this chapter tests the migration machinery itself.

The repeated command demonstrates idempotent migration planning for this unchanged schema. It does not prove that every future migration is reversible or safe under concurrent application traffic. Dropping a column or changing a large table needs a separate data-preservation and deployment plan.

## Worked case: let the database enforce uniqueness

A second row with the same title is attempted inside transaction.atomic. The database raises IntegrityError, and the transaction rolls back. The final count remains one. Catching the exception outside the atomic block ensures the failed transaction is unwound before later queries inspect the result.

This case explains why a form's uniqueness check is not enough under concurrency. Two requests can both observe that a title is available before either commits. The constraint provides the final decision, and the application must translate the expected conflict without leaving its transaction unusable.

Data migrations require equal care. A transformation should define how existing rows are mapped, how failures are resumed and whether the reverse direction is meaningful. A successful schema-only fixture does not certify an unrelated data migration.

## Failure diagnosis and discussion

**Why does the model include a field that SQL says is missing?** Model state and applied migration state may differ. Inspect the migration plan and target database before changing application code.

**Should developers regenerate a migration already deployed elsewhere?** Usually not. Changing its history can make environments disagree about what a recorded migration means. Add a new reviewed migration for the new state.

If a duplicate-write test poisons later queries, inspect where the IntegrityError is caught relative to atomic. If migration replay loses a row, inspect destructive operations rather than assuming migrate is harmless. Continue with QuerySets to learn when database reads actually execute.
