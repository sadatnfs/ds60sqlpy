# r-053: reference reasoning

Use the [complete reference](r-053_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference tests both mapping and constant-setting behavior rather than checking only that a ggplot object exists. The summary layer has independent data and explicitly controlled inheritance, making its numerical role inspectable.

Only two plots are printed. The built-data checks establish row/group/coordinate properties, while the actual classroom renderer must still be inspected for visual quality and delivery. No browser success is inferred from a bare Rscript pass.

## Explained practice

### Exercise 1

Map group to colour and shape for the four-row fixture.

The built point layer contains four observations and two encoded group identities.

**Expected evidence:** Four marks and two categories.

### Exercise 2

Set a constant point colour outside aes and compare it with a group mapping.

The constant setting gives one colour to every row, while a group mapping uses a scale.

**Expected evidence:** One fixed colour versus two mapped colours.

### Exercise 3

Add a group-mean layer using its own data.

The layer has two rows with response means 2 and 4, separate from the four raw observations.

**Expected evidence:** Correct layer-specific row counts and coordinates.

### Exercise 4

Diagnose aes(colour="group") when the intended mapping is the group column.

The quoted string is one mapped category, not the data column. Use aes(colour=group) for variable mapping.

**Expected evidence:** Literal-versus-variable distinction stated.

### Exercise 5

Print a plot object from a script or function.

The explicit call emits the graphic through the active device rather than merely storing an object.

**Expected evidence:** A rendered figure request occurs.

### Exercise 6

Explain what ggplot_build checks cannot establish about the delivered image.

Correct marks and groups do not prove readable labels, sufficient contrast or absence of clipping in the browser.

**Expected evidence:** Data and visual evidence separated.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
