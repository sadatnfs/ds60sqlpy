# Day 57 — Security, Privacy, and Ethics (Companion Guide)

## Learning objectives
- Handle secrets and PII safely; understand data minimization
- Apply basic privacy techniques (pseudonymization, k-anonymity concepts)
- Recognize and mitigate bias; document model cards

## Why this matters
Responsible AI requires protecting users, complying with regulations, and mitigating harms.

## Core concepts and examples
- Secrets: use env vars or secret managers (not in code)
- PII: classify, encrypt at rest/in transit, access control, retention
- Privacy: aggregation, differential privacy (concept), noise addition
- Fairness: group metrics, disparate impact, balanced datasets

## Common pitfalls
- Exporting logs with PII to unsecured storage
- Using demographic attributes as features without justification
- Ignoring consent, purpose limitation, and transparency

## Practice exercises
1) Create a data classification matrix for a project
2) Compute group precision/recall across sensitive groups
3) Draft a model card with intended use and limitations

## Further reading
- Model Cards: https://arxiv.org/abs/1810.03993
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
