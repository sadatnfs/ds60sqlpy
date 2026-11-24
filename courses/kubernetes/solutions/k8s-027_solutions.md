# k8s-027: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Observability connects internal state to the questions an operator needs to answer. Metrics summarize numeric behavior, logs record events and traces connect work across components. None is useful without a defined unit, time window and relation to the service contract. A dashboard can be visually healthy while omitting the failing path.

A service-level indicator should describe user-relevant behavior, such as successful eligible requests divided by all eligible requests. A service-level objective adds a target over a defined window. A five-request teaching sample can illustrate the calculation but cannot establish a production reliability objective.

The chapter uses an authored request ledger and optional host-provided namespace metrics. It does not install a monitoring stack or assume metrics-server exists. Missing metrics capability is recorded as unavailable, not converted to zero CPU or zero errors.

## Exercise 1: Define an SLI

The metric definition determines what is measured. A successful status with a wrong payload may still violate the application contract, so the indicator should match the intended user outcome.

**Expected:** A reproducible numerator/denominator with five synthetic observations.

**Solution reasoning**

- **Approach:** Write the SLI definition: which requests count, what counts as success, the window and the unit.
- **Why it is correct:** A definition precise enough to recount the five rows gives the same numerator and denominator to anyone who applies it.
- **Plausible wrong approach:** Saying the service was mostly fine gives no rule another person could apply to the ledger.
- **How to verify:** Recounting the five rows yields the same two numbers.

## Exercise 2: Compute error and success fractions

Counts reveal the small evidence base. The result illustrates arithmetic and cannot establish a production SLO or recurrence from five synthetic requests.

**Expected:** Error fraction 0.2 and success fraction 0.8 under the declared status rule.

**Solution reasoning**

- **Approach:** Count one 500 and four 200 among five eligible requests and divide each by five.
- **Why it is correct:** Under a rule that 5xx is an error, one of five is 0.2 errors and four of five is 0.8 success.
- **Plausible wrong approach:** Dividing by the four successful requests gives an error ratio of 0.25 and a denominator that excludes failures.
- **How to verify:** The two fractions are 0.2 and 0.8, and they sum to one.

## Exercise 3: Compute the stated quantiles

Another interpolation convention can yield a different value. Report the convention and filtering rather than treating one library default as a universal p95 definition.

**Expected:** p50=30ms, p95=100ms.

**Solution reasoning**

- **Approach:** Sort the five latencies and take rank ceil(q times n) for each quantile.
- **Why it is correct:** With n of 5, p50 uses rank 3 and p95 uses rank 5, so p95 is the largest of the five samples.
- **Plausible wrong approach:** Interpolating between ranks gives values that never appeared in the data and differ from the stated method.
- **How to verify:** p50 is the third sorted value and p95 the fifth, matching 30 ms and 100 ms.

## Exercise 4: Inspect a counter reset

The reset changes the interpretation of a simple difference. Recovering a rate needs enough timing/reset data or a monitoring method designed for counters. Do not invent events that were not observed.

**Expected:** Do not report negative 117 requests; record reset and available interval evidence.

**Solution reasoning**

- **Approach:** Note that 3 is lower than 120 and check for a process restart between the readings.
- **Why it is correct:** Counters only increase within one process, so a drop after a restart is a reset, not negative traffic.
- **Plausible wrong approach:** Subtracting to report minus 117 requests treats a reset as real traffic.
- **How to verify:** The record names the reset and uses only the evidence available for each interval.

## Exercise 5: Handle absent metrics

The absence of a data source is itself an operational fact. Installing a stack or broadening credentials is outside this lesson's automatic workflow; the host must provide and qualify it deliberately.

**Expected:** Metrics capability unavailable, not zero resource use.

**Solution reasoning**

- **Approach:** Record the metrics API error text next to the successful client result.
- **Why it is correct:** A missing metrics API means usage was not measured, which is different from a measured zero.
- **Plausible wrong approach:** Writing CPU 0 for the namespace converts an unavailable reading into a false measurement.
- **How to verify:** The record contains the error or condition text and a separate passing client check.

## Exercise 6: Write a focused incident observation

The next check should discriminate a plausible mechanism such as backend readiness, application errors or resource pressure. Preserve missingness and uncertainty instead of turning a dashboard pattern into a definitive root cause.

**Expected:** A bounded evidence record with units, window, UIDs and a reversible diagnostic.

**Solution reasoning**

- **Approach:** Pair one controller fact with one application metric, add a hypothesis and one reversible next check.
- **Why it is correct:** Together they connect what Kubernetes reported with what clients experienced, within a stated window and with object UIDs.
- **Plausible wrong approach:** Proposing a rollback as the next step makes the diagnosis irreversible before the hypothesis is tested.
- **How to verify:** Units, window, UIDs and a reversible next check are all present.

## Boundary and troubleshooting review

A missing metrics API is a capability issue, not proof of zero usage. A single slow request suggests a question but does not establish the system-wide cause. An alert should name the violated contract and a discriminating next check.

Record units, window, sample size, filters and missingness. A screenshot alone cannot reproduce the calculation or prove application correctness. The offline script checks the synthetic ledger; actual collection requires the qualified host/client capability.
