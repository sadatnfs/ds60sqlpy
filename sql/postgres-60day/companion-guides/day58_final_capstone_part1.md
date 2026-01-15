# Day 58 — Final Capstone (Part 1) — Ingestion, Cleansing, and Validation (Companion Guide)

Objectives
- Ingest messy staged data; normalize case/whitespace/date formats
- Validate emails/countries; upsert valid rows; report data quality
- Build mapping tables for normalization and reusable validation functions

Flow (matches script)
1) Stage raw rows into a temp staging table (stg_customers_raw)
2) Clean:
   - full_name: trim; collapse whitespace
   - email: lower, trim; regex validation
   - country: upper, trim; map via country_map
   - segment: nullif(trim(segment), '')
   - created_at: parse multiple formats with CASE/regex + to_timestamp
   - attributes: to JSONB, fallback to '{}'
3) Validate flags: email_valid, country_valid
4) Upsert: INSERT ... SELECT valid rows; ON CONFLICT DO NOTHING (or DO UPDATE by design)
5) DQ summary: counts of invalid email/country/name; store/report

Pitfalls
- Overly strict regexes that reject valid emails; choose pragmatic patterns
- Server‑side COPY permission issues; prefer \copy or inserts in curriculum
- Time zone normalization; parse to timestamptz

Deliverables
- Cleaned records inserted; DQ summary table/view with counts

Stretch goals
- Extend parser to more date formats and phone normalization
- Stored procedure to wrap end‑to‑end ingest with return of DQ metrics
