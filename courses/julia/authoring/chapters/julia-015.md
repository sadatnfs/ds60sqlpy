## A table needs a schema and a grain

A DataFrame organizes named columns into rows. Its grain states what one row represents. Column names and element types are useful schema information, but a table also needs semantic contracts such as unique request IDs, units and missingness rules. DataFrames does not infer those scientific meanings automatically.

Selection chooses columns or creates derived ones. A row-wise transformation applies a function to corresponding values from each row, while a column transformation receives a whole column. `ByRow` makes that distinction explicit. Grouping creates subsets for an aggregation rule; it does not itself decide whether groups should receive equal weights in a later scientific summary.

Indexing conventions affect copying. A selected column accessed with `!` can share its storage, while ordinary copied-column selection can provide a separate vector. Learn the documented contract and test caller-visible mutation rather than assuming that every table expression creates a snapshot.

## Worked case A: select and transform named columns

The first example retains a request ID and derives a scaled score. It explicitly requests copied columns for the selected output. A separate alias/copy trace shows why mutating a directly shared score column changes the source table. The resulting names and values are checked exactly.

{{WORKED_A}}

## Worked case B: summarize with missingness counts

The grouped example has two groups and one missing score. Each output group reports total rows, observed scores and the observed-value mean. Sorting group keys makes presentation deterministic. A mean alone would hide the difference between one observed score and two observed scores.

{{WORKED_B}}

## Whole-column and row-wise functions

A vector-valued function and a scalar row function have different shape contracts. Broadcasting a function over a column is not the same as passing the whole column to an aggregation. Inspect small outputs and names before assigning a derived field to a larger pipeline.

Keep original columns when they are needed for lineage or diagnosis. A chain of transformations should make it possible to reconstruct rejected rows and the meaning of each derived value. Reusing a familiar column name for a different unit or population creates a semantic error even if the code is valid.

## Diagnose a grouped result

Check input counts, group keys, missingness and the aggregation denominator. An all-missing group needs an explicit result policy. If later code averages group means, decide whether it should weight groups equally or by their relevant observation counts. Both can be meaningful but answer different questions.

A table transformation is not proof that data have the intended grain. Validate identifiers and join assumptions before aggregating. The next unit demonstrates how a many-to-many join can inflate totals while producing a well-formed DataFrame.

The examples use the prepared DataFrames package and small literal tables. No external file or service is read. They establish the stated indexing and transformation contracts, not a general claim that a particular chain is statistically valid or optimized for a large dataset.
