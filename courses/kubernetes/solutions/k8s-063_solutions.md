# k8s-063: explanatory solutions

Compare after your own attempt or an explicit reveal. These explanations describe the synthetic topology and stated API contracts. They are not fabricated runtime receipts.

## Mechanism review

Observability uses system outputs to reason about internal behavior. Events describe notable Kubernetes lifecycle observations. Logs record application or component messages. Metrics summarize numeric measurements over time. Traces connect spans of a request across components. Each signal has different retention, sampling and interpretation limits.

A metric’s labels define its dimensions. High-cardinality labels such as every raw user ID or request token can create operational cost and privacy risk. Aggregation can hide a failing subgroup, while excessive detail can overwhelm the system. Choose dimensions that support the diagnostic question.

A trace ID can connect a browser request to proxy and application work when propagation is implemented. It is not a secret or authorization token, and it should not be confused with a Kubernetes resource UID. Time synchronization and sampling affect how confidently signals can be correlated.

Begin with a named symptom and time window. Read only relevant namespace objects, bounded logs and the minimal metric dimensions needed. A Pod event about scheduling does not prove a later HTTP request’s outcome. A request latency spike can involve DNS, connection setup, queueing or handler work.

The fixture supplies synthetic event and request records to practice correlation. Actual metrics stacks and distributed tracing require separately prepared components. The lesson does not install observability operators or collect all-cluster data automatically.

## Exercise 1: Match each signal to a diagnostic question.

No signal is universally sufficient. Choose the smallest set that distinguishes the competing explanations.

**Expected:** Events for lifecycle, logs for messages, metrics for trends, traces for request paths.

## Exercise 2: Define a bounded incident time window.

Without time alignment a healthy later observation can be mistaken for evidence about the original failure.

**Expected:** Relevant timestamps and retained identities are explicit.

## Exercise 3: Build a correlated synthetic request packet.

Resource identity and request identity serve different roles. Preserve both when connecting rollout changes to request behavior.

**Expected:** Request ID, service, status, duration and resource revision are related carefully.

## Exercise 4: Diagnose a latency metric without assuming app CPU is the cause.

A total duration measures the whole path. Use more specific evidence before changing resource limits.

**Expected:** Break down DNS, connection, queueing and handler phases.

## Exercise 5: Explain high-cardinality label risk.

Use bounded dimensions for aggregation and appropriately controlled logs or traces for individual requests.

**Expected:** Unbounded unique label values expand metric state and cost.

## Exercise 6: Plan privacy-aware observability for a teaching service.

Diagnostics should make failures explainable without collecting unrelated personal or secret data.

**Expected:** No credentials or private payloads, bounded retention and useful correlation fields.
