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

**Solution reasoning**

- **Approach:** Pair kubectl events with lifecycle questions, logs with messages, metrics with trends and traces with request paths.
- **Why it is correct:** Each signal records a different thing, so the question decides which one can answer it.
- **Plausible wrong approach:** Searching logs for a scheduling failure misses that the scheduler reports it as an event.
- **How to verify:** Each of the four signals is matched to its diagnostic question.

## Exercise 2: Define a bounded incident time window.

Without time alignment a healthy later observation can be mistaken for evidence about the original failure.

**Expected:** Relevant timestamps and retained identities are explicit.

**Solution reasoning**

- **Approach:** Set start and end timestamps around the incident and record the Pod names and UIDs involved.
- **Why it is correct:** Events expire and Pods are replaced, so a window tied to retained identities keeps evidence comparable.
- **Plausible wrong approach:** Querying the last hour with no fixed bounds mixes unrelated activity into the result.
- **How to verify:** The window has explicit timestamps and the identities that existed within it.

## Exercise 3: Build a correlated synthetic request packet.

Resource identity and request identity serve different roles. Preserve both when connecting rollout changes to request behavior.

**Expected:** Request ID, service, status, duration and resource revision are related carefully.

**Solution reasoning**

- **Approach:** Link one request ID to its service, status, duration and the revision of the serving workload.
- **Why it is correct:** A shared ID lets log lines, spans and metrics describe the same request instead of nearby ones.
- **Plausible wrong approach:** Joining records by timestamp alone can pair a slow request with a different request's error.
- **How to verify:** Every field in the packet is linked to the request ID and revision.

## Exercise 4: Diagnose a latency metric without assuming app CPU is the cause.

A total duration measures the whole path. Use more specific evidence before changing resource limits.

**Expected:** Break down DNS, connection, queueing and handler phases.

**Solution reasoning**

- **Approach:** Split the measured latency into DNS, connection, queueing and handler time before choosing a cause.
- **Why it is correct:** A high total can come from any phase, and CPU only explains the handler part.
- **Plausible wrong approach:** Raising CPU limits because latency rose may change nothing if the delay is in DNS or queueing.
- **How to verify:** The answer breaks latency into phases with evidence for each.

## Exercise 5: Explain high-cardinality label risk.

Use bounded dimensions for aggregation and appropriately controlled logs or traces for individual requests.

**Expected:** Unbounded unique label values expand metric state and cost.

**Solution reasoning**

- **Approach:** Show that each unique label value creates a new time series in the metrics store.
- **Why it is correct:** Labels such as request ID or user ID have no bound, so series count, memory and cost grow without limit.
- **Plausible wrong approach:** Adding a per-request label to make metrics searchable turns them into an unbounded store.
- **How to verify:** The answer ties unbounded label values to growing metric state and cost.

## Exercise 6: Plan privacy-aware observability for a teaching service.

Diagnostics should make failures explainable without collecting unrelated personal or secret data.

**Expected:** No credentials or private payloads, bounded retention and useful correlation fields.

**Solution reasoning**

- **Approach:** Exclude credentials and private payloads, bound retention and keep fields such as request ID and revision.
- **Why it is correct:** Correlation needs identifiers, not content, so useful debugging does not require sensitive data.
- **Plausible wrong approach:** Logging full request bodies for convenience can capture tokens and personal data.
- **How to verify:** The plan lists excluded data, a retention limit and the correlation fields kept.
