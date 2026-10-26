# dax-046: explained reference and practice reasoning

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

The complete [reference source](dax-046_reference.dax) and [named model](../models/retail/model.json) belong together. The reference-results sidecar binds both exact files by SHA-256. Those hashes identify bytes; they do not certify DAX execution.

## Worked-case reconciliation

### Case A: Default and explicit rates

All-row revenue 187; fee-rate domain 0..1; default rate 0.1.

| DefaultFee | ExplicitTwentyPercent |
| --- | --- |
| 168.3 | 149.6 |

A default argument is part of the function contract. Changing it can alter every call that omits the parameter, even if the call source itself stays unchanged.

- The omitted rate uses 0.1, giving 187*(1-0.1)=168.3.
- An explicit 0.2 overrides that default.
- 187*(1-0.2)=149.6.

### Case B: A valid zero and an invalid rate

Same function; compare boundary rate 1 with out-of-domain rate 1.2.

| FullFee | InvalidRate |
| --- | --- |
| 0 | BLANK |

A caller should retain a validation signal if BLANK could be mistaken for no activity. A more elaborate error policy belongs in the function's documented contract.

- Rate 1 is inside the declared domain and leaves zero amount.
- Rate 1.2 violates the rule.
- The invalid-domain branch returns BLANK, not a fabricated negative net amount.

## Explained practice answers

### Exercise 1

Predict Course.NetAfterFee(50,0).

The result is 50.

### Exercise 2

Change the default rate to 0.15 in a hypothetical version.

The 187 default call would become 158.95; the explicit 0.2 call would remain 149.6.

### Exercise 3

Write a function contract with units and domain.

Amount is a numeric value in one declared currency; feeRate is a dimensionless fraction in 0..1; output uses the same currency and invalid rates return BLANK.

### Exercise 4

Diagnose treating a measure reference as a function that accepts a rate argument.

Use a defined UDF for explicit parameters, or model a disconnected parameter selection for a measure; do not invent measure-call syntax.

### Exercise 5

Explain why function text alone does not prove an external model supports UDFs.

Verify the documented product release and database compatibility level before external use; this offline file is not a compiler receipt.

### Exercise 6

Transfer the rule to reusable metric normalization.

Document units, accepted domains, missingness and evaluation-mode assumptions, then test boundary calls and the caller's context separately.

## Review the boundary

A sound answer can use a different readable expression if its population, context and units agree. Compare counterexamples as well as ordinary rows. Where an engine, model role or newer feature is assumed, record that assumption separately from the offline calculation. Never reuse a supplied table as evidence that an edited formula ran.
