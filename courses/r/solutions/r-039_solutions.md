# r-039: reference reasoning

Use the [complete reference](r-039_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The interaction is zero for A and follows x for B, allowing a different slope in the two groups under this encoding.

twice_x is exactly determined by x. More column names do not create more independent information.

## Explained practice

### Exercise 1

List the columns of ~ x + group for a two-level factor.

Intercept, x and groupB under the declared levels/contrasts.

**Expected evidence:** Intercept, x and groupB under the declared levels/contrasts.

### Exercise 2

Add x:group through the * expansion.

The design also includes x:groupB.

**Expected evidence:** The design also includes x:groupB.

### Exercise 3

Inspect and validate a design before fitting.

Document the numeric meaning of every requested coefficient.

**Expected evidence:** Document the numeric meaning of every requested coefficient.

### Exercise 4

Diagnose simultaneous x and 2*x predictors.

Separate coefficients are not identifiable from this design.

**Expected evidence:** Separate coefficients are not identifiable from this design.

### Exercise 5

Handle a factor level absent from training data.

Do not silently invent a learned effect for an unseen category.

**Expected evidence:** Do not silently invent a learned effect for an unseen category.

### Exercise 6

Separate algebraic fit from model validity.

Use diagnostics and held-out evaluation after defining the statistical question.

**Expected evidence:** Use diagnostics and held-out evaluation after defining the statistical question.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.
