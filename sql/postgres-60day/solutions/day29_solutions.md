# Day 29 — Solutions: Pattern Matching

PostgreSQL regex operators are `~` (case-sensitive) and `~*`
(case-insensitive). Full-text search tokenizes and normalizes words rather than
matching arbitrary substrings.

## Exercise 1 — Emails beginning with `customer1` plus two digits

Assumption: the seeded `@example.com` domain is part of the required format.
Anchors ensure the entire email matches, and the dot in the domain is escaped.

```sql
SET search_path TO training, public;

SELECT customer_id,
       full_name,
       email
FROM customers
WHERE email ~* '^customer1[0-9]{2}@example\.com$'
ORDER BY customer_id;
```

Expected shape: customers whose numeric suffix is exactly three digits and
starts with `1`, such as `customer100@example.com`. It does not match
`customer10` or `customer1000`.

If the domain should be unrestricted, replace the ending with `@.+$`; that is a
different and much looser requirement.

## Exercise 2 — Full-text search requiring both “home” and “product”

```sql
SET search_path TO training, public;

SELECT product_id,
       name,
       category
FROM products
WHERE to_tsvector(
        'english',
        name || ' ' || category
      ) @@ to_tsquery('english', 'home & product')
ORDER BY product_id;
```

Expected shape: products whose combined name and category contain both search
lexemes. In the seeded catalog, `Product ...` names in the `Home` category
qualify.

## Pitfalls

- `%` and `_` are wildcards for `LIKE`, not for PostgreSQL regex.
- `|` means OR and `&` means AND in `to_tsquery`; the exercise requires `&`.
- Concatenation with a nullable field produces `NULL`. The setup columns used
  here are non-null, but production code can use
  `concat_ws(' ', name, category)`.
- Applying `to_tsvector` at query time is fine for this small course table. A
  larger system normally uses a generated `tsvector` column plus a GIN index.
