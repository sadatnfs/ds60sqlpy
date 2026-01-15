# Day 60 — Final Capstone (Part 3) — Packaging, Performance, and Handoff (Companion Guide)

Objectives
- Package SQL artifacts, document runbooks, and performance profiles
- Ensure reproducibility, access controls, and monitoring hooks
- Present results and limitations; plan next steps

Packaging
- Organize scripts by stage: staging/, conformance/, serving/, views/, mvs/
- Provide Makefile or task runner with phony targets: setup, load, build_dims, build_facts, build_kpis
- Requirements and environment: Postgres version, extensions (tablefunc, pg_trgm), settings used

Performance and reliability
- Include EXPLAIN (ANALYZE, BUFFERS) for key queries; before/after improvements
- Outline vacuum/autovacuum settings and index maintenance schedule
- Permissions: GRANT on views to BI role; RLS where applicable

Handoff
- README with architecture diagram, data lineage, and glossary
- Known limitations (e.g., returns handling), risks, and backlog
- Monitoring plan: dashboards for top queries, bloat, long transactions

Deliverables
- A self‑contained repository folder with scripts, docs, and sample outputs

Stretch goals
- Dockerized Postgres + seed data for demo
- CI job to lint SQL, run validations, and build MVs
