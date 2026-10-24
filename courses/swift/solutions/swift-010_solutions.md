# swift-010: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-010_solution.swift](swift-010_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Preserve absence and zero:** Optional lookup prevents missing information from being confused with a stored value. Pear is present with zero and apple is absent.

**Deduplicate and order deliberately:** Set semantics establish uniqueness while sorting separately establishes order. Duplicate red is not inserted and sorted output is deterministic.

## Reason through the six tasks

1. **Predict and explain.** Explain the optional result of each dictionary lookup.

2. **Guided modification.** Count repeated tags using the default-value subscript.

3. **Independent construction.** Build a unique sorted list of accepted inventory names.

4. **Diagnose a defect.** Diagnose persisting hashValue as a cross-run identifier.

5. **Boundary evidence.** Test missing, present-zero and duplicate keys.

6. **Transfer and justify.** Design a custom Hashable key using only stable identity fields.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A Dictionary associates unique keys with values; a Set stores unique members. Both use Hashable to narrow equality lookup. Equal values must hash consistently. A hash value is not a persistent identifier and should not be saved as an enduring key, since hashing can vary across process runs.

Dictionary lookup returns an optional, preserving the distinction between a missing key and a present zero. Output order is not a business sorting policy. Sort keys explicitly for stable presentation. When designing a custom key, use stable identity fields and avoid changing a key after it has been inserted into hashed storage.

`[String: Int]` declares a dictionary. `counts[key, default: 0] += 1` inserts a default only for that mutation. Set.insert returns whether an element was newly inserted. sorted establishes presentation order.

Hash collisions do not mean values are equal; equality resolves them. Dictionary order should not be treated as a report contract. A default subscript can insert values during mutation, so inspect side effects.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
