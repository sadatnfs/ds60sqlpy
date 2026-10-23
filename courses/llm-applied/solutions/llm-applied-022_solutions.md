# llm-applied-022: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

An LLM can help propose data-science operations, but the application should execute only typed, bounded operations whose semantics are understood. A tool call is a request object, not a shell command. The dispatcher validates its schema, operation name, column choices, row limit and value types before computing. A model-generated SQL string is especially risky when treated as an unrestricted query; this lesson instead exposes a narrow grouped-mean operation over an in-memory fixture. The same principle can wrap reviewed parameterized SQL in a real system.

Separate extraction, computation and explanation. An extraction proposal becomes accepted data only after validation. A deterministic tool computes counts and means. The answerer then explains the returned artifact without inventing a different number or causal interpretation. A mean difference does not establish a treatment effect without a valid design. Missing values, booleans, nonfinite numbers and unsupported columns are explicit failures under this lesson contract. The code performs no network request, database mutation or arbitrary evaluation.

**Tool proposal:** A structured request awaiting trusted validation.

**Dispatcher:** Code mapping admitted operation names to fixed implementations.

**Deterministic analysis artifact:** A reproducible result calculated from accepted data.

**Interpretation boundary:** The distinction between a computed statistic and a broader claim.

## Reading the implementation

The tool request has exactlyoperation, group_by andvalue fields. Allowed values aregroup_mean, group andvalue. Input rows haveid, group, value with unique IDs and at most20 records. Rejectbool even though it is anint subclass. Group values with a dictionary, then emit sorted rows containinggroup, count, mean. Keep the tool result separate from any prose proposal and verify quoted numbers against it.

## Trace a typed tool from proposal to descriptive result

The accepted request is exactly operation=group_mean, group_by=group, value=value. An extra query field or operation=run_sql is rejected rather than interpreted. The dispatcher therefore selects a fixed implementation; it does not execute model-generated source code. The literal rows are already in memory, so this example makes no claim about authenticating a database connection or binding SQL parameters in a live engine.

The input grain is one identified observation per row. The output grain is one row per group, carrying count and mean. For A values1, 3, the sum is four, count two and mean two. B has value ten, count one and mean ten. The descriptive difference B minus A is eight. The output preserves the different sample counts instead of presenting both means as equally supported by data.

Aggregation can change meaning. The overall observation mean is(1+3+10)/3=14/3. Averaging the two group means gives(2+10)/2=6 and weights groups equally rather than observations. Carrying counts makes the distinction reconstructible. The request schema does not authorize a later explanation to substitute either aggregate silently.

Finite input checks alone do not prevent intermediate overflow. With values[1e308, 1e308], ordinary floating summation can become infinity before division by two, although the mathematical mean is1e308. The repaired calculation uses s=max(abs(values)), computes a mean of scaled values v/s, then multiplies by s. Every scaled magnitude is at most one, so the bounded group cannot overflow that summation. A zero scale returns zero directly. The result is also checked for finiteness.

For the two large equal values, scaled values are[1, 1], their mean is one and the output is1e308. For equal opposite values, the scaled terms cancel to zero. This is an arithmetic stability improvement, not a guarantee of exactness for every representable combination; rounding and underflow remain part of floating-point computation. Use an explicitly different numeric representation if the task requires exact monetary units or exact decimal rounding rules.

Missing values and booleans are rejected under this strict policy. Dropping None would change count and potentially bias the result; accepting True as one would conflate logical and measured data. A different missingness policy may be appropriate for another task, but it should have its own output count, denominator and explanation. Duplicate IDs are also a data-quality failure because repeated observations would change weights.

The explanation check in the fixture compares the computed mean two with a proposed value twenty. It demonstrates an independent numeric anchor, but it is not a parser that validates every arbitrary sentence. A real report interface can carry structured claims referring to result cells and render them through reviewed templates, or use a separately evaluated extraction/validation stage for free-form prose.

Finally, group membership is not a treatment-assignment design. The difference eight does not by itself estimate the causal effect of changing an observation from A to B. Sampling, measurement, confounding and assignment assumptions remain outside the grouped-mean arithmetic. The assistant can state which additional evidence is needed, but fluent explanation cannot supply it.

### Interview reasoning with explanatory answers

**Why keep counts beside means?** They identify denominators and allow correct recombination. They also expose a one-record group that a mean alone could conceal.

**Why validate outputs after validated inputs?** Correct primitive types and finite inputs do not exclude numerical overflow or implementation errors. The computed artifact has its own contract.

**Does a narrow tool replace data access policy?** No. It restricts allowed operations. The application must separately determine which rows the principal may use and how results may be disclosed.

## Exercise 1: Execute a bounded grouped mean

The question is: Use rowsA1, A3, B10 and the admittedgroup_mean request.

The output grain is one row pergroup. Counts remain beside means so a one-record group does not look as well supported as a larger group.

```python
rows=[{'id':'a1','group':'A','value':1.},{'id':'a2','group':'A','value':3.},{'id':'b1','group':'B','value':10.}]
request={'operation':'group_mean','group_by':'group','value':'value'}
result=dispatch(request,rows)
assert result==[{'group':'A','count':2,'mean':2.},{'group':'B','count':1,'mean':10.}]
```

**Expected:** A count 2 mean2; B count 1 mean10.

**Verify:** Compare the computed values or written argument with A count 2 mean2; B count 1 mean10.

## Exercise 2: Reject an arbitrary operation

The question is: Submitoperationrun_sql or an extraquery field.

The dispatcher never interprets arbitrary text as code or SQL. A production SQL adapter would need a separate reviewed query template and target boundary.

```python
for proposal in [{'operation':'run_sql','group_by':'group','value':'value'},{**request,'query':'DROP TABLE anything'}]:
    try: dispatch(proposal,rows)
    except ValueError: pass
    else: raise AssertionError('unbounded operation accepted')
```

**Expected:** ValueError before any computation.

**Verify:** Compare the computed values or written argument with ValueError before any computation.

## Exercise 3: Reject invalid numeric values

The question is: Replace one value with True, NaN or None, then check large finite values and cancellation under the same numeric policy.

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

**Expected:** invalid rows are rejected; equal1e308 values have finite mean1e308 and opposite values have mean0.

**Verify:** Compare the computed values or written argument with invalid rows are rejected; equal1e308 values have finite mean1e308 and opposite values have mean0.

## Exercise 4: Enforce identity and work limits

The question is: Duplicatea1, then supply21 unique rows.

Repeated records can bias aggregates, and unbounded inputs can exceed a tool budget. Both checks occur before the grouped calculation.

```python
too_many=[{'id':str(i),'group':'A','value':1.} for i in range(21)]
for bad_rows in [rows+[dict(rows[0])],too_many]:
    try: dispatch(request,bad_rows)
    except ValueError: pass
    else: raise AssertionError('identity or budget ignored')
```

**Expected:** duplicate identity and row-limit violations rejected.

**Verify:** Compare the computed values or written argument with duplicate identity and row-limit violations rejected.

## Exercise 5: Verify an explanation against the artifact

The question is: Check a proposed sentence saying groupAmean2 against the result; reject a proposedmean20.

The explanation stage should consume the computed artifact as its numerical source. A fluent but different number is an output-validation failure.

```python
lookup={r['group']:r for r in result}
assert lookup['A']['mean']==2 and lookup['A']['mean']!=20
```

**Expected:** 2accepted; 20mismatch.

**Verify:** Compare the computed values or written argument with 2accepted; 20mismatch.

## Exercise 6: Refuse an unsupported causal interpretation

The question is: Attach a descriptive result to a claim that group caused the difference without assignment-design evidence.

An LLM can help explain what additional design evidence is needed, but it cannot convert an observational group difference into a causal effect by wording alone.

```python
report={'group_means':result,'random_assignment_verified':False,'causal_effect_established':False}
assert report['group_means'] and not report['causal_effect_established']
```

**Expected:** descriptive statisticavailable; causal claimnot established.

**Verify:** Compare the computed values or written argument with descriptive statisticavailable; causal claimnot established.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.
