# Day 56 — Project 4: BI (Part 2) — Row‑Level Security, Access, and Parameters (Companion Guide)

Objectives
- Implement row‑level security (RLS) policies for multi‑tenant or region‑restricted views
- Parameterize reporting via session variables or binding tables
- Audit access and ensure PII protections

RLS basics
- ALTER TABLE ... ENABLE ROW LEVEL SECURITY; CREATE POLICY ... USING (...)
- Use current_setting('app.user_region') to parameterize allowed regions

Parameterized reporting
- Create a small params table keyed by session/app id; join to filter date ranges, segments
- Alternatively, bind variables from the application layer (preferred)

PII and auditing
- Mask sensitive fields in views (hash/email prefix); grant SELECT only on views
- Log connections and queries where appropriate; avoid logging PII values

Pitfalls
- Complex policies that hurt performance; keep predicates sargable and indexed
- Leaking data through aggregates with small group sizes; enforce k‑anonymity thresholds in views

Deliverables
- Example RLS policy and a restricted BI view

Stretch goals
- Proxy roles and SECURITY INVOKER/DEFINER choices
- Row count suppression for small cohorts
