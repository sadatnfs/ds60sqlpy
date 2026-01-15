# Day 53 — Project 3: Data Warehouse (Part 2) — Slowly Changing Dimensions (SCD) (Companion Guide)

Objectives
- Implement SCD Type 1 and Type 2 for key dimensions (customers/products)
- Use MERGE‑like upsert patterns to manage changes
- Maintain validity ranges and current‑row flags

Patterns
- SCD1 (overwrite): UPDATE existing row; INSERT new if not exists; no history
- SCD2 (history): end‑date prior row, insert new row with start_date, end_date=NULL, is_current=true

SQL sketch (Postgres 15 MERGE or emulation)
- MERGE INTO dim_customer d USING staging s ON (d.natural_key=s.natural_key)
  WHEN MATCHED AND hash(d.attribs) <> hash(s.attribs) THEN
    UPDATE SET end_date = s.effective_ts, is_current=false
    INSERT (..., start_date=s.effective_ts, end_date=NULL, is_current=true)
  WHEN NOT MATCHED THEN INSERT (..., start_date=s.effective_ts, end_date=NULL, is_current=true)

Queries
- As‑of joins: join fact to dim on key and fact_date BETWEEN start_date AND COALESCE(end_date, 'infinity')
- Current row filter: is_current=true

Pitfalls
- Duplicate natural keys in staging; dedup deterministically first
- Clock skew on effective_ts; prefer source change timestamp or batch time

Deliverables
- SCD1/2 upsert scripts and test cases

Stretch goals
- SCD Type 3 (limited history columns) and hybrid patterns
- Hash diffing for change detection with fewer column compares
