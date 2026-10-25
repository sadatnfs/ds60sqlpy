# llm-applied-022: Structured tools for extraction, aggregation and data-science work

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-021`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Tools connect language proposals to explicit analytical operations. This chapter follows a request through validation, data admission, computation and explanation, showing how typed interfaces and stable arithmetic support a data scientist without turning a model's wording into execution authority.

## Purpose and mental model

An LLM can help propose data-science operations, but the application should execute only typed, bounded operations whose semantics are understood. A tool call is a request object, not a shell command. The dispatcher validates its schema, operation name, column choices, row limit and value types before computing. A model-generated SQL string is especially risky when treated as an unrestricted query; this lesson instead exposes a narrow grouped-mean operation over an in-memory fixture. The same principle can wrap reviewed parameterized SQL in a real system.

Separate extraction, computation and explanation. An extraction proposal becomes accepted data only after validation. A deterministic tool computes counts and means. The answerer then explains the returned artifact without inventing a different number or causal interpretation. A mean difference does not establish a treatment effect without a valid design. Missing values, booleans, nonfinite numbers and unsupported columns are explicit failures under this lesson contract. The code performs no network request, database mutation or arbitrary evaluation.

## Treat a tool call as a proposal with a defined meaning

An analyst asks the Methods Desk to compare average outcomes by group. The model can help identify a suitable operation and fill a structured request, but the application must decide whether that request is allowed and whether its inputs satisfy the operation's assumptions. The model's output is data presented to that decision, not an arbitrary program to execute.

The fixture exposes one operation: group_mean over named group and value fields. Extra keys and unsupported operations are rejected. This small interface makes the computation easy to inspect and gives the learner a concrete baseline before considering a larger tool catalog. A real database-backed operation would additionally need authenticated data access, a reviewed query shape and a snapshot or consistency policy.

The operation catalog should correspond to useful analytical tasks. A count, a grouped mean, a validated join or a predeclared confidence-interval calculation can each have a clear input and output contract. Exposing unrestricted text execution because it is flexible moves many unresolved decisions into the model proposal. The narrower interface lets the application preserve units, grain and resource bounds explicitly.

## Trace the data as carefully as the requested operation

The accepted request does not establish that the rows are appropriate. The application must know which observations the principal may use, which reporting period they belong to and what one row represents. The fixture uses one uniquely identified observation per row and rejects duplicate IDs. A join that duplicates a row would otherwise change the weight it receives in the mean.

For group A with values 1 and 3 and group B with value 10, the tool returns counts and means: A has count 2 and mean 2; B has count 1 and mean 10. The difference of means is eight. Retaining counts makes the result interpretable and allows the overall observation mean to be reconstructed as \(\frac{14}{3}\). Averaging the two group means instead yields six and defines a different weighting rule.

Missingness is another part of the contract. Replacing a missing measurement with zero or dropping it silently changes the denominator and possibly the population. The fixture rejects missing values under its strict policy. Another operation could support missingness explicitly, but should then report which observations contributed and which policy was applied.

## Validate the numerical output, not only the primitive types

Finite numeric inputs can still lead to an unstable implementation. Two values of 1e308 have a finite mean of 1e308, but a naive intermediate sum can overflow. The qualified tool uses scaled summation and checks its result. This is an example of why typed input admission and computational correctness are independent obligations.

Different tasks require different numerical representations. Integer cents can preserve exact monetary totals under an appropriate domain contract; floating-point means introduce rounding. A statistical procedure may need conditioning checks or a meaningful tolerance. The tool's output should state the method and units rather than presenting every numeric value as exact in the same sense.

The current example is deterministic over its accepted in-memory rows. A remote query can observe changing data between two calls, so repeating the same request text does not necessarily reproduce the same result. A larger analytical artifact should retain a data snapshot or equivalent source identity, the operation/code version and the relevant policy. Those identities let the analyst distinguish changed input from changed implementation.

## Keep execution and explanation as separate stages

After the dispatcher returns a structured result, the language model can explain it. That second stage must preserve the values, units and scope of the artifact. A response saying group A's mean is 20 when the tool returned 2 is an output-validation failure, even if the prose is otherwise clear. A response calling the difference a causal effect adds a claim the grouped mean did not establish.

A structured report can refer directly to result fields and render reviewed phrases around them. More flexible prose can be checked through a separate claim-extraction and validation process. Either way, the calculation artifact remains the numerical source. Asking the generator to recompute the number from memory creates another opportunity for divergence.

The analyst's requested interpretation may require additional work. A mean difference can reflect selection, confounding, measurement or random variation. A tool that calculates it correctly does not establish random assignment, independence or a suitable uncertainty model. The assistant should identify the missing design evidence and, when appropriate, propose a separate reviewed analysis rather than claim that the arithmetic already answered the causal question.

## Bound the operation through its lifecycle

The fixture's row limit controls one dimension of work. A serving tool also needs a duration limit, cancellation behavior and explicit handling of partial failure. A retry policy should distinguish whether the previous operation merely failed to return a result or may already have produced a side effect. The pure grouped-mean example has no external mutation; operations that write data need a separately defined authorization and recovery contract.

Tool results and errors are also untrusted inputs to a later model stage. An error message should not be allowed to redefine the operation catalog or request broader access merely because it appears in a tool-output field. The application retains control of which next actions are admissible, while the model can propose a useful explanation or recovery step within that boundary.

The next chapter combines these lifecycle concerns with freshness, caching and observability. Together they make a domain assistant reviewable as a system: a question leads to admitted evidence and data, a bounded computation produces an artifact, and the final answer is checked against what actually happened.

## Design decisions and when to use this method

Use typed tools when a subject assistant needs exact arithmetic, validated database reads, plots or data transformations. Keep the operation catalog small and explicit. Validate inputs before execution and outputs before explanation. For expensive tools, add real time, cancellation and resource bounds in the execution layer rather than relying only on a prompt asking the model to be concise.

Do not expose eval, arbitrary filesystem paths or unrestricted SQL as a convenience shortcut. A model proposal can be malformed or influenced by retrieved text. A real database tool should use parameter binding, least-privilege access and an explicit target. Preserve the analysis code and input identity so a user can reproduce a result without trusting the generated prose. Statistical interpretation still depends on sampling, measurement and design assumptions beyond the tool's arithmetic correctness.

Expose a small operation whose input schema, output grain and computational meaning are reviewable. A proposal model can choose that operation and explain its result, while the application validates and executes it. Keep operation admission distinct from permission to access the underlying data.

The numeric implementation now uses scaled summation so two large finite values can have a correct finite mean without an overflowing intermediate sum. That strengthens arithmetic under the same declared finite-number policy. It does not turn floating-point means into exact rational arithmetic or establish causal interpretation.

## Vocabulary and concepts

**Tool proposal:** A structured request awaiting trusted validation.

**Dispatcher:** Code mapping admitted operation names to fixed implementations.

**Deterministic analysis artifact:** A reproducible result calculated from accepted data.

**Interpretation boundary:** The distinction between a computed statistic and a broader claim.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-022/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-022.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The tool request has exactly operation, group_by and value fields. Allowed values are group_mean, group and value. Input rows have id, group, value with unique IDs and at most 20 records. Reject bool even though it is an int subclass. Group values with a dictionary, then emit sorted rows containing group, count, mean. Keep the tool result separate from any prose proposal and verify quoted numbers against it.

## Trace a typed tool from proposal to descriptive result

The accepted request is exactly operation=group_mean, group_by=group, value=value. An extra query field or operation=run_sql is rejected rather than interpreted. The dispatcher therefore selects a fixed implementation; it does not execute model-generated source code. The literal rows are already in memory, so this example makes no claim about authenticating a database connection or binding SQL parameters in a live engine.

The input grain is one identified observation per row. The output grain is one row per group, carrying count and mean. For A values 1, 3, the sum is four, count two and mean two. B has value ten, count one and mean ten. The descriptive difference B minus A is eight. The output preserves the different sample counts instead of presenting both means as equally supported by data.

Aggregation can change meaning. The overall observation mean is(1+3+10)/3=\(\frac{14}{3}\). Averaging the two group means gives(2+10)/2=6 and weights groups equally rather than observations. Carrying counts makes the distinction reconstructible. The request schema does not authorize a later explanation to substitute either aggregate silently.

Finite input checks alone do not prevent intermediate overflow. With values[1e308, 1e308], ordinary floating summation can become infinity before division by two, although the mathematical mean is 1e308. The repaired calculation uses s=max(abs(values)), computes a mean of scaled values v/s, then multiplies by s. Every scaled magnitude is at most one, so the bounded group cannot overflow that summation. A zero scale returns zero directly. The result is also checked for finiteness.

For the two large equal values, scaled values are[1, 1], their mean is one and the output is 1e308. For equal opposite values, the scaled terms cancel to zero. This is an arithmetic stability improvement, not a guarantee of exactness for every representable combination; rounding and underflow remain part of floating-point computation. Use an explicitly different numeric representation if the task requires exact monetary units or exact decimal rounding rules.

Missing values and booleans are rejected under this strict policy. Dropping None would change count and potentially bias the result; accepting True as one would conflate logical and measured data. A different missingness policy may be appropriate for another task, but it should have its own output count, denominator and explanation. Duplicate IDs are also a data-quality failure because repeated observations would change weights.

The explanation check in the fixture compares the computed mean two with a proposed value twenty. It demonstrates an independent numeric anchor, but it is not a parser that validates every arbitrary sentence. A real report interface can carry structured claims referring to result cells and render them through reviewed templates, or use a separately evaluated extraction/validation stage for free-form prose.

Finally, group membership is not a treatment-assignment design. The difference eight does not by itself estimate the causal effect of changing an observation from A to B. Sampling, measurement, confounding and assignment assumptions remain outside the grouped-mean arithmetic. The assistant can state which additional evidence is needed, but fluent explanation cannot supply it.

### Interview reasoning with explanatory answers

**Why keep counts beside means?** They identify denominators and allow correct recombination. They also expose a one-record group that a mean alone could conceal.

**Why validate outputs after validated inputs?** Correct primitive types and finite inputs do not exclude numerical overflow or implementation errors. The computed artifact has its own contract.

**Does a narrow tool replace data access policy?** No. It restricts allowed operations. The application must separately determine which rows the principal may use and how results may be disclosed.

## Worked example / walkthrough

### Example A: Execute a bounded grouped mean

The output grain is one row per group. Counts remain beside means so a one-record group does not look as well supported as a larger group.

```python
import math
from collections import defaultdict
def dispatch(request,rows):
    if not isinstance(request,dict) or set(request)!={'operation','group_by','value'}: raise ValueError('exact tool fields required')
    if request!={'operation':'group_mean','group_by':'group','value':'value'}: raise ValueError('operation or columns not allowed')
    if not 1<=len(rows)<=20: raise ValueError('row budget1..20 required')
    if len({row['id'] for row in rows})!=len(rows): raise ValueError('duplicate row ID')
    groups=defaultdict(list)
    for row in rows:
        if set(row)!={'id','group','value'} or not isinstance(row['id'],str) or not isinstance(row['group'],str): raise ValueError('row schema')
        value=row['value']
        if type(value) not in (int,float): raise TypeError('numeric value required')
        if not math.isfinite(value): raise ValueError('finite value required')
        groups[row['group']].append(value)
    result=[]
    for key,values in sorted(groups.items()):
        scale=max(abs(value) for value in values)
        mean=0.0 if scale==0 else scale*(math.fsum(value/scale for value in values)/len(values))
        if not math.isfinite(mean): raise ValueError('finite group mean required')
        result.append({'group':key,'count':len(values),'mean':mean})
    return result
rows=[{'id':'a1','group':'A','value':1.},{'id':'a2','group':'A','value':3.},{'id':'b1','group':'B','value':10.}]
request={'operation':'group_mean','group_by':'group','value':'value'}
result=dispatch(request,rows)
assert result==[{'group':'A','count':2,'mean':2.},{'group':'B','count':1,'mean':10.}]
```

**Expected:** A count 2 mean 2; B count 1 mean 10.

### Example B: Reject an arbitrary operation

The dispatcher never interprets arbitrary text as code or SQL. A production SQL adapter would need a separate reviewed query template and target boundary.

```python
for proposal in [{'operation':'run_sql','group_by':'group','value':'value'},{**request,'query':'DROP TABLE anything'}]:
    try: dispatch(proposal,rows)
    except ValueError: pass
    else: raise AssertionError('unbounded operation accepted')
```

**Expected:** ValueError before any computation.

### Example C: Reject invalid numeric values

Silently dropping or coercing these values would change the denominator or meaning. A different missingness policy must be explicitly designed and reported.

```python
for bad in [True,float('nan'),None]:
    changed=[dict(r) for r in rows]; changed[0]['value']=bad
    try: dispatch(request,changed)
    except (TypeError,ValueError): pass
    else: raise AssertionError('invalid numeric value accepted')
huge=[{'id':'h1','group':'A','value':1e308},{'id':'h2','group':'A','value':1e308}]
assert dispatch(request,huge)==[{'group':'A','count':2,'mean':1e308}]
huge[1]['value']=-1e308
assert dispatch(request,huge)[0]['mean']==0.0
```

**Expected:** invalid rows are rejected; equal 1e308 values have finite mean 1e308 and opposite values have mean 0.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: A count 2 mean 2; B count 1 mean 10. descriptive statistic available; causal claim not established. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Execute a bounded grouped mean.** Use rowsA 1, A3, B10 and the admittedgroup_mean request.
   **Expected:** A count 2 mean 2; B count 1 mean 10.
   **Verify:** Save the assertion results for exercise 1, including A count 2 mean 2; B count 1 mean 10.

2. **Reject an arbitrary operation.** Submitoperationrun_sql or an extra query field.
   **Expected:** ValueError before any computation.
   **Verify:** Save the assertion results for exercise 2, including ValueError before any computation.

3. **Reject invalid numeric values.** Replace one value with True, NaN or None, then check large finite values and cancellation under the same numeric policy.
   **Expected:** invalid rows are rejected; equal 1e308 values have finite mean 1e308 and opposite values have mean 0.
   **Verify:** Save the assertion results for exercise 3, including invalid rows are rejected; equal 1e308 values have finite mean 1e308 and opposite values have mean 0.

4. **Enforce identity and work limits.** Duplicatea 1, then supply 21 unique rows.
   **Expected:** duplicate identity and row-limit violations rejected.
   **Verify:** Save the assertion results for exercise 4, including duplicate identity and row-limit violations rejected.

5. **Verify an explanation against the artifact.** Check a proposed sentence saying groupAmean 2 against the result; reject a proposed mean 20.
   **Expected:** 2accepted; 20mismatch.
   **Verify:** Save the assertion results for exercise 5, including 2accepted; 20mismatch.

6. **Refuse an unsupported causal interpretation.** Attach a descriptive result to a claim that group caused the difference without assignment-design evidence.
   **Expected:** descriptive statistic available; causal claim not established.
   **Verify:** Save the assertion results for exercise 6, including descriptive statistic available; causal claim not established.

## Common pitfalls and diagnosis

If a mean is nonfinite despite finite rows, inspect intermediate arithmetic and the output guard. If an aggregate changes after joining data, inspect observation IDs and multiplicity before the tool. If a report uses a mean of group means, verify that equal-group weighting was actually intended.

If a model proposes extra columns or arbitrary SQL, reject the unsupported request shape rather than attempting to interpret it. If the explanation invents a number or causal effect, compare it with the structured artifact and design evidence. Record admission, calculation and interpretation failures separately so each can be repaired at the correct boundary.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Tool proposal, Dispatcher, Deterministic analysis artifact using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-021` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Python numeric types](https://docs.python.org/3.12/library/stdtypes.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-022, Structured tools for extraction, aggregation and data-science work.
Read courses/llm-applied/guides/llm-applied-022.md and courses/llm-applied/lessons/llm-applied-022.py. Direct prerequisites: `llm-applied-021`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```
