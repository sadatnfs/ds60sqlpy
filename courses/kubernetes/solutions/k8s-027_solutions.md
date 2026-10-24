# k8s-027: Explanatory solutions

These answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.

## Mechanism

Observability connects internal state to the questions an operator needs to answer. Metrics summarize numeric behavior, logs record events and traces connect work across components. None is useful without a defined unit, time window and relation to the service contract. A dashboard can be visually healthy while omitting the failing path.

A service-level indicator should describe user-relevant behavior, such as successful eligible requests divided by all eligible requests. A service-level objective adds a target over a defined window. A five-request teaching sample can illustrate the calculation but cannot establish a production reliability objective.

The chapter uses an authored request ledger and optional host-provided namespace metrics. It does not install a monitoring stack or assume metrics-server exists. Missing metrics capability is recorded as unavailable, not converted to zero CPU or zero errors.

## Exercise 1: Define an SLI

The metric definition determines what is measured. A successful status with a wrong payload may still violate the application contract, so the indicator should match the intended user outcome.

**Expected:** A reproducible numerator/denominator with five synthetic observations.

## Exercise 2: Compute error and success fractions

Counts reveal the small evidence base. The result illustrates arithmetic and cannot establish a production SLO or recurrence from five synthetic requests.

**Expected:** Error.2, success.8 under the declared status rule.

## Exercise 3: Compute the stated quantiles

Another interpolation convention can yield a different value. Report the convention and filtering rather than treating one library default as a universal p95 definition.

**Expected:** p50=30ms, p95=100ms.

## Exercise 4: Inspect a counter reset

The reset changes the interpretation of a simple difference. Recovering a rate needs enough timing/reset data or a monitoring method designed for counters. Do not invent events that were not observed.

**Expected:** Do not report negative117 requests; record reset and available interval evidence.

## Exercise 5: Handle absent metrics

The absence of a data source is itself an operational fact. Installing a stack or broadening credentials is outside this lesson's automatic workflow; the host must provide and qualify it deliberately.

**Expected:** Metrics capability unavailable, not zero resource use.

## Exercise 6: Write a focused incident observation

The next check should discriminate a plausible mechanism such as backend readiness, application errors or resource pressure. Preserve missingness and uncertainty instead of turning a dashboard pattern into a definitive root cause.

**Expected:** A bounded evidence record with units, window, UIDs and a reversible diagnostic.

## Boundary and troubleshooting review

A missing metrics API is a capability issue, not proof of zero usage. A single slow request suggests a question but does not establish the system-wide cause. An alert should name the violated contract and a discriminating next check.

Record units, window, sample size, filters and missingness. A screenshot alone cannot reproduce the calculation or prove application correctness. The offline script checks the synthetic ledger; actual collection requires the qualified host/client capability.
