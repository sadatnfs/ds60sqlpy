# web-035: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

PHP's array is an ordered map: it associates keys with values and preserves an iteration order. It can represent a list or a keyed record, but these are different data contracts. A list of study rows should not accidentally become an object-shaped JSON value because filtered numeric keys were left nonconsecutive. Key coercion can also matter, so avoid treating arbitrary external strings as interchangeable with integer indices.

Transformations are easier to reason about when they do not mutate the original data unexpectedly. Map computes a derived value for each record; filter keeps records satisfying a predicate. Validate expected fields before arithmetic. A missing key is different from a known null field and should be handled according to the record contract.

Use explicit string keys for records, such as subject and minutes. `array_filter` preserves keys, so `array_values` is useful when the intended result is a fresh list. `array_map` applies a function to values. A foreach by reference can leave a lingering reference to the last item; avoid it unless mutation is necessary and understood.

## Exercise 1: Explain how a list differs from a keyed record.

A list models ordered values; a record's named keys identify fields.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a second validated study row.

Every row has the declared subject and integer-minutes fields.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Filter and summarize study records without changing the originals.

The derived list contains only qualifying rows and retains consecutive indices.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose JSON output changing from an array to an object shape.

Inspect numeric key gaps after filtering and reindex when the contract is a list.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test an empty result and a missing required field.

Empty lists are valid where declared; malformed records are rejected explicitly.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the risk of a lingering foreach reference.

A reference variable can still alias the last element and cause later assignments to mutate it.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.
