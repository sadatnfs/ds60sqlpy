# Service hardening and observability solution reasoning

Attempt `python-svc-02` before opening
[`py_svc_02_hardening_observability_solution.py`](py_svc_02_hardening_observability_solution.py).

Health answers whether the process can answer diagnostics; readiness answers
whether it should receive new work. A failed dependency, unverified artifact,
or draining state makes readiness false while health can remain true for
investigation and graceful shutdown.

Authentication establishes identity; authorization checks that identity's role
for one action. The local static authenticator is an injected test double, not a
production credential system. Tokens never enter logs. Structured events carry
request IDs and bounded fields; metrics use low-cardinality names rather than
user or request IDs as labels.

The token bucket has an injected clock, and the concurrency gate rejects excess
work immediately. Those controls protect one process. Internet-facing systems
also need shared/distributed limits, queue budgets, upstream timeouts, TLS,
secret rotation, network policy, and abuse monitoring.

Artifact bytes are hashed before JSON is trusted. The loader deliberately
rejects pickle and nested arbitrary objects. The incident drill turns a
dependency probe false, observes readiness fail, verifies new work receives
503, and checks logs and metrics retain enough context.

Edge cases include double lease release, clock movement, rate keys with
unbounded cardinality, health checks that perform expensive dependency calls,
logs containing request bodies, metrics labeled by user, authorization policy
drift, artifact replacement after verification, and a readiness dependency
that flaps.

