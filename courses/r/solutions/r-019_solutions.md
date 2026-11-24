# r-019: reference reasoning

Use the [complete reference](r-019_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The ID remains character, and the empty missing marker is a deliberate part of this synthetic CSV contract.

The JSON contract contains a scalar ID and an array of values. The RDS round trip additionally retains factor levels, including the unused level.

## Explained practice

### Exercise 1

Explain why row.names=FALSE matters in a CSV export.

It prevents an unintended extra column.

**Approach:** Write the starter frame with `row.names = FALSE`, read it back and compare the column names with the original.

**Why it holds here:** The frame's row names are the defaults 1 and 2, which carry no business meaning. With row.names = FALSE the file holds only id and amount, so the restored names match exactly.

**Tempting mistake:** Accepting the default export. The file gains an unnamed first column, read.csv names it X, and the restored frame has three columns, so positional code reads the row index as the ID.

**Verify:** `names(restored)` returns "id", "amount" after the FALSE export, while the default export shows "X", "id", "amount".

### Exercise 2

Preserve an ID with leading zeros.

The restored ID stays"001" rather than numeric 1.

**Approach:** Declare the ID column as character on read with `colClasses = c("character", "numeric")`.

**Why it holds here:** "001" and "002" are identifiers, not quantities, so their characters must survive unchanged. Declaring the class means read.csv never guesses, and the leading zeros stay in place for joins and display.

**Tempting mistake:** Reading with defaults and repairing afterward with `sprintf("%03d", id)`. That assumes every ID is exactly three digits wide, which nothing in the contract promises, and it cannot restore an ID such as "0001".

**Verify:** `restored$id` returns "001" and "002", and `identical(restored, original)` returns TRUE.

### Exercise 3

Round-trip one trusted R object with attributes.

saveRDS/readRDS preserve the intended local R structure.

**Approach:** Save the object with `saveRDS(x, path)`, read it with `readRDS(path)` and compare with `identical()`, using RDS only for trusted files produced by R.

**Why it holds here:** The reference object is a numeric vector with names A and B, and Example 2 uses a factor with an unused level C. RDS serializes the complete object, so names, class and levels all come back.

**Tempting mistake:** Writing the factor to CSV. Only the labels A and B are written, read.csv returns plain character, and both the factor class and level C are lost without any message.

**Verify:** `identical(readRDS(path), x)` returns TRUE, and for the factor `levels(readRDS(path))` shows "A", "B", "C".

### Exercise 4

Diagnose default type inference as a schema guarantee.

Specify and validate required column types and missing markers.

**Approach:** State the required classes and missing markers in the read call, then validate the restored names, classes and NA counts before using the data.

**Why it holds here:** From these two rows read.csv would infer integer for both columns, because the amount 2 has no decimal point. The original amount is double, so identical() fails even though the printed values look the same.

**Tempting mistake:** Treating the inferred types as the schema. A later file with 2.5 turns amount into double, and one with n/a turns it into character, so each new file can silently change the program's behavior.

**Verify:** `class(read.csv(path, na.strings = "")$amount)` returns "integer", while the typed read returns "numeric".

### Exercise 5

State the JSON shape of a one-element measurement vector.

Choose array versus scalar explicitly and test that representation.

**Approach:** Decide that values is always an array, wrap it in `I()` before `toJSON(..., auto_unbox = TRUE)`, and read it back with `simplifyVector = FALSE`.

**Why it holds here:** The reference record has a single measurement, 2. I() protects it from unboxing, so the text is an array with one element, the same shape as a record with two measurements, and the restored value is a list.

**Tempting mistake:** Relying on auto_unbox alone. The single value is written as the scalar 2, and a consumer expecting an array fails only on records that happen to have one measurement.

**Verify:** `as.character(encoded)` returns {"values":[2]}, and `is.list(restored$values)` returns TRUE.

### Exercise 6

Explain whether a temporary output survives a later classroom run.

Do not rely on arbitrary temporary files; retain source and supported captured artifacts through the documented UI.

**Approach:** Treat every `tempfile()` path as owned by the current session, remove it with `unlink()` when finished, and keep anything worth saving as source code or as an artifact captured through the documented classroom interface.

**Why it holds here:** tempfile() returns a path inside tempdir(), a directory created for this R session and removed when the session ends. A later classroom run starts a new session with a different directory, and the saved classroom state does not include the run filesystem.

**Tempting mistake:** Copying a path printed by an earlier run into a later script. That file is gone, so the read fails, or it finds an unrelated file if paths happen to be reused.

**Verify:** `file.exists(path)` returns FALSE after `unlink(path)`, and `tempdir()` shows a different directory in a new session.

## What the checks establish

The reference makes 3 `stopifnot()` checks on its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
