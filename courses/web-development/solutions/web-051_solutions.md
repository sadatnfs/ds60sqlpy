# web-051: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

PDO is a database access interface with drivers for particular engines. The classroom prepares PDO SQLite so examples can use an in-memory database without credentials or network access. PostgreSQL and SQLite differ in types, SQL features and concurrency, so a SQLite pass does not prove PostgreSQL behavior. Revisit the SQL route for relational design and engine-specific queries.

A prepared statement separates the fixed query structure from parameter values. A value containing a quote or SQL-looking text remains a value when bound correctly. Parameters cannot stand in for arbitrary identifiers, keywords or sort directions. Dynamic column selection needs an explicit allowlist that maps a choice to trusted SQL structure. Escaping HTML output is a separate boundary after fetching data.

Create a PDO connection with exception error mode, create a tiny schema and prepare an INSERT. Execute it with a parameter map, then prepare a SELECT using a value predicate. Keep the database handle local to this run. The example's table is disposable in-memory state, not the learner's persistent classroom database.

## Exercise 1: Explain what a prepared value parameter can and cannot replace.

It represents data values, not arbitrary table names, column names or SQL keywords.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Insert a title containing an apostrophe.

The stored value round-trips exactly through a bound parameter.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a local PDO note store with prepared insert and lookup.

The expected record is retrieved and SQL-looking text remains data.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose concatenating an untrusted sort key into SQL.

Map the choice through an explicit trusted allowlist rather than treating it as a bindable value.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test an empty result and an attack-shaped title.

No-match behavior is explicit and the table remains intact after storing the title.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain which checks must be repeated when moving to PostgreSQL.

Driver behavior, schema types, SQL syntax, transactions and concurrency need engine-specific integration evidence.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
