# Day 52 — Project 3: Data Warehouse (Part 1) — Dimensional Modeling (Companion Guide)

Objectives
- Design a star schema for analytics: fact tables and conforming dimensions
- Define grain, surrogate keys, and slowly changing needs
- Plan staging → conformance → serving layers

Modeling steps
- Identify business processes (orders, events) and define fact grain (e.g., one row per order_item)
- Dimensions: customers, products, dates, geography; surrogate keys (bigint identity)
- Conformance: consistent codes, canonical types (timestamptz UTC)

Pipelines
- Staging tables mirror sources; light typing only
- Conformance applies business rules, deduping, and SCD logic for dims
- Serving exposes facts/dims with foreign keys and quality checks

Pitfalls
- Mixed grains; lock grain early
- Natural key drift; use robust key mapping and audit tables

Deliverables
- ERD of star schema; checklist of columns and dtypes

Stretch goals
- Bridge tables for many‑to‑many (product tags), role‑playing dims (order_date vs ship_date)
