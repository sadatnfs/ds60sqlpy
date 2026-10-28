## A collection has a contract beyond its contents

A tuple is an immutable ordered collection whose element types can differ. A named tuple adds field names, making a small record easier to interpret. A dictionary maps keys to values, while a set records membership. These structures answer different questions and should not be selected only because they can all hold several values.

A one-element tuple needs a trailing comma to distinguish it from parentheses around an expression. Named tuples expose fields by name as well as position. Their field names and order are part of their type, which can support clear small record interfaces. They do not automatically make nested mutable values immutable.

Dictionary iteration order should not be used as an implicit scientific ordering rule. Sort keys or construct an explicit ordering when a report, comparison or serialization needs one. Missing keys also require a policy: lookup can fail, a default can be supplied, or a value can be inserted deliberately.

## Worked case A: a record with explicit fields

The first example groups a request ID, a score and an eligibility flag in a named tuple. It checks named access and destructures an ordinary tuple. A small returned record can be clearer than a positional vector whose columns must be remembered by the caller.

{{WORKED_A}}

## Worked case B: count categories and inspect membership

The dictionary example counts repeated categories with an explicit zero default. It then sorts the keys before presentation. A set removes duplicates for a membership question, which is different from counting their frequency. The program retains both views so deduplication cannot silently change the counting task.

{{WORKED_B}}

## Keys and equality

Dictionaries use an equality/hash contract that treats certain special values differently from ordinary numerical `==`. The earlier equality lesson introduced `isequal`. A NaN key can therefore be retrieved consistently, while signed zeros can remain distinct keys. This behavior is useful only when it matches the meaning assigned to those keys.

A mutable object used as a key can be difficult to reason about if its equality or hash-relevant state changes after insertion. Prefer stable identifiers for records and keep measurements as values. A row's current position is not a stable identifier when the dataset can be reordered.

## Diagnose a collection choice

If counts change after a conversion to a set, ask whether multiplicity was meaningful. If a report changes ordering between environments, inspect whether it relied on dictionary traversal. If a missing key is treated as zero, confirm that absent and observed-zero are interchangeable for that metric. They often are not.

A named tuple is well suited to a small fixed record, while a DataFrame later supplies a columnar table interface. Neither removes the need for a declared schema, units and missingness policy. Use the representation that makes the intended operations and invariants clear.

The examples check tuple syntax, record access, category counts, stable presentation and special-key behavior. They do not establish a universal speed ranking among structures. Later type and performance lessons explain how concrete element types and access patterns interact with compilation and allocation.
