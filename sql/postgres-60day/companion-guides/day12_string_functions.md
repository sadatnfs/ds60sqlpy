# Day 12 — String Functions and Text Processing (Companion Guide)

Learning objectives
- Clean and standardize text: TRIM, UPPER/LOWER, REPLACE, REGEXP_REPLACE
- Parse text: SPLIT_PART, SUBSTRING, POSITION, regular expressions
- Compare case-insensitively: ILIKE, citext, trigram similarity (pg_trgm)

Core concepts and deep dive
- Normalization: trim whitespace, unify case, collapse repeated spaces with regex.
- Parsing: SPLIT_PART(email,'@',2) to get domain; SUBSTRING with regex for flexible extraction.
- Regular expressions: ~ (match), ~* (case-insensitive), !~ (not match); capture groups in SUBSTRING.
- Performance: Function on column may prevent index use; consider functional indexes or store normalized columns.

Examples
- Standardize emails: lower(trim(email)).
- Extract order prefix from SKU: SUBSTRING(sku FROM '^([A-Z]+)-').
- Regex validate phone numbers and flag invalids.

Practice exercises
1) Build a normalized_customer_email column and check duplicates.
2) Extract TLD from email domain and analyze distribution.
3) Use pg_trgm to find near-duplicate product names.

Further reading
- String functions: https://www.postgresql.org/docs/current/functions-string.html
- Regex: https://www.postgresql.org/docs/current/functions-matching.html
- pg_trgm: https://www.postgresql.org/docs/current/pgtrgm.html
