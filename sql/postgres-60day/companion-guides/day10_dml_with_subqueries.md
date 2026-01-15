# Day 10 — DML with Subqueries: INSERT/UPDATE/DELETE/UPSERT (Companion Guide)

Learning objectives
- INSERT ... SELECT to populate tables from queries
- UPDATE ... FROM and DELETE using subqueries
- Use ON CONFLICT for idempotent upserts

Core concepts and deep dive
- INSERT INTO table(cols) SELECT ... FROM ... WHERE ...; carry all required columns, handle default values.
- UPDATE t SET col=expr FROM other WHERE t.id=other.id; mind ambiguity with JOINs.
- DELETE FROM t USING other WHERE t.id=other.id; or use WHERE EXISTS (...) pattern.
- Upsert: INSERT ... ON CONFLICT (key) DO UPDATE SET ...; choose conflict target (PK/unique) and update columns carefully.

Examples
- Deduplicate staging to canonical: INSERT ... SELECT DISTINCT ... ON CONFLICT DO NOTHING/UPDATE.
- Slowly-changing-attribute style updates: UPDATE customers SET segment=new.segment FROM new WHERE customers.id=new.id.

Pitfalls
- Multi-row subqueries in scalar contexts; ensure uniqueness or add LIMIT 1.
- Upserts racing under concurrency; consider locking or version columns.

Practice exercises
1) Insert top 1000 high-value customers into a marketing list table.
2) Upsert product prices from a pricing feed; record updated_at.

Further reading
- INSERT: https://www.postgresql.org/docs/current/sql-insert.html
- UPDATE: https://www.postgresql.org/docs/current/sql-update.html
- UPSERT: https://www.postgresql.org/docs/current/sql-insert.html#SQL-ON-CONFLICT
