# Day 08 — Scalar and Inline Subqueries (Companion Guide)

Learning objectives
- Use scalar subqueries in SELECT/WHERE for per-row lookups
- Use IN/ANY/ALL with subqueries and understand semantics
- Replace subqueries with joins where appropriate for performance

Core concepts and deep dive
- Scalar subquery returns a single value; errors on >1 row. Use LIMIT 1 with ORDER BY to guarantee determinism.
- IN subquery builds a set; ANY/ALL compare a value against a subquery-produced set with an operator.
- Correlated vs uncorrelated inline subqueries: prefer uncorrelated when possible.

Examples
- SELECT customer_id, (SELECT COUNT(*) FROM orders o WHERE o.customer_id=c.customer_id) AS order_cnt FROM customers c.
- WHERE product_id IN (SELECT product_id FROM promotions WHERE now() BETWEEN starts_at AND ends_at).

Pitfalls
- Scalar subqueries in SELECT executed per row; may be slow. Consider pre-aggregating and joining.
- IN with large sets can be slow; join instead or use EXISTS.

Practice exercises
1) Add last_order_date per customer via scalar subquery; then rewrite as a LEFT JOIN.
2) Use ANY to filter orders whose total exceeds ANY top 10% order totals.

Further reading
- Subqueries: https://www.postgresql.org/docs/current/sql-select.html#SQL-SELECT-SUBQUERIES
