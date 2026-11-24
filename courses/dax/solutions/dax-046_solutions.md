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

**Why it fits this model:** A rate of 0 is inside the 0 to 1 domain, so the function returns amount x (1 - 0).

**Tempting mistake:** Expecting 0 to count as omitted and trigger the 0.1 default, which gives 45. The default applies only when the argument is missing.

**How to confirm:** Course.NetAfterFee(50, 0) returns 50.

### Exercise 2

Change the default rate to 0.15 in a hypothetical version.

The 187 default call would become 158.95; the explicit 0.2 call would remain 149.6.

**Why it fits this model:** Calls that omit the rate use the default, so only the first column moves: 187 x 0.85. The explicit 0.2 call still computes 187 x 0.8.

**Tempting mistake:** Expecting both columns to change because both call the same function. An explicit argument always overrides the default.

**How to confirm:** DefaultFee becomes 158.95 and ExplicitTwentyPercent stays 149.6.

### Exercise 3

Write a function contract with units and domain.

Amount is a numeric value in one declared currency; feeRate is a dimensionless fraction in 0..1; output uses the same currency and invalid rates return BLANK.

**Why it fits this model:** The contract names the amount's currency (USD for NetRevenue), the rate as a fraction from 0 to 1, the output in the same currency, and BLANK for invalid rates.

**Tempting mistake:** A caller passing 10 for 10 percent gets BLANK, because 10 is outside the domain. Without the contract, that looks like a bug.

**How to confirm:** Course.NetAfterFee(187, 0.1) returns 168.3 and Course.NetAfterFee(187, 10) returns BLANK, both as documented.

### Exercise 4

Diagnose treating a measure reference as a function that accepts a rate argument.

Use a defined UDF for explicit parameters, or model a disconnected parameter selection for a measure; do not invent measure-call syntax.

**Why it fits this model:** Measures take no arguments. A rate that varies by caller is either a UDF parameter or a selection from a disconnected parameter table read with SELECTEDVALUE.

**Tempting mistake:** Writing `[NetRevenue](0.2)` as if a measure accepted a rate. It is not valid DAX.

**How to confirm:** Course.NetAfterFee([NetRevenue], 0.2) returns 149.6; a parameter table with 0.2 selected should give the same.

### Exercise 5

Explain why function text alone does not prove an external model supports UDFs.

Verify the documented product release and database compatibility level before external use; this offline file is not a compiler receipt.

**Why it fits this model:** Whether UDFs are available depends on the product release, the feature's status and the model's compatibility level. Valid function text does not show that support.

**Tempting mistake:** Copying the FUNCTION definition into an older model and assuming that, since it ran in this course, it will deploy.

**How to confirm:** Check the target release and compatibility level in the documentation, then run case A in that model and expect 168.3 and 149.6.

### Exercise 6

Transfer the rule to reusable metric normalization.

Document units, accepted domains, missingness and evaluation-mode assumptions, then test boundary calls and the caller's context separately.

**Why it fits this model:** A normalization function, such as revenue per unit, should take both values as parameters: 187 / 17 = 11 USD per unit overall.

**Tempting mistake:** A function that applies ALL(Product) inside its body. Every caller then gets the overall figure, 11, even under Blue, where 163 / 12 is about 13.58.

**How to confirm:** Call it under Blue and expect about 13.58; any population change belongs in the caller's filters, where it is visible.

## Review the boundary

Another readable expression is sound when its population, context and units match; record any assumed engine separately.
