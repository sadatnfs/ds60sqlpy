# r-039: reference reasoning

Run the [complete reference](r-039_reference.R) under the [run rules](../STUDY-GUIDE.md#run-a-chapter).

## Why the implementation has this shape

The interaction is zero for A and follows x for B, allowing a different slope in the two groups under this encoding.

twice_x is exactly determined by x. More column names do not create more independent information.

## Explained practice

### Exercise 1

List the columns of ~ x + group for a two-level factor.

Intercept, x and groupB under the declared levels/contrasts.

**Approach:** Build `model.matrix(~ x + group, data)` and read its column names.

**Why it holds here:** The intercept stands for group A because A is the first declared level, x gets one column, and B gets one treatment contrast column, groupB, which is 1 for rows 3 and 4.

**Tempting mistake:** Expecting both groupA and groupB next to the intercept. With an intercept that design would be rank deficient. If the levels were declared as B then A, the single column would be groupA, so the level order decides the reference.

**Verify:** `identical(colnames(additive), c("(Intercept)", "x", "groupB"))` returns TRUE.

### Exercise 2

Add x:group through the * expansion.

The design also includes x:groupB.

**Approach:** Write `~ x * group`, which expands to x + group + x:group, and check that the main effects stay in the design.

**Why it holds here:** The added x:groupB column is the product of x and groupB, so it is 0, 0, 0, 1: only the B row with x = 1 carries it. The coefficient is the difference between B's slope and A's.

**Tempting mistake:** Writing `~ x:group` alone. Without the x and group main effects, R codes the term as x:groupA and x:groupB with one shared intercept, which forces both groups to have the same value at x = 0.

**Verify:** `colnames(interaction)` returns the four names ending in x:groupB, and `interaction[, "x:groupB"]` returns 0, 0, 0, 1.

### Exercise 3

Inspect and validate a design before fitting.

Document the numeric meaning of every requested coefficient.

**Approach:** Before fitting, check the column names, the dimensions and that the rank equals the number of columns, and write down what each coefficient means.

**Why it holds here:** Here the design is 4 by 4 with rank 4, so every coefficient is identified, and the names say which comparison each one makes. With exactly as many rows as columns, though, no error can be estimated.

**Tempting mistake:** Fitting lm first and reading the coefficient table. lm does not stop on a rank deficient design; it reports NA for the aliased coefficient, which is easy to skim past.

**Verify:** `qr(interaction)$rank == ncol(interaction)` returns TRUE, and `dim(interaction)` returns 4 4.

### Exercise 4

Diagnose simultaneous x and 2*x predictors.

Separate coefficients are not identifiable from this design.

**Approach:** Detect the dependency with the rank and keep only one of the two columns.

**Why it holds here:** `I(2 * x)` is exactly twice x in every row, so the design has three columns and rank two. Coefficients of 1 on x and 0 on the copy produce the same fitted values as 0 on x and 0.5 on the copy, so separate effects cannot be identified.

**Tempting mistake:** Reading the NA that lm reports for `I(2 * x)` as evidence that the doubled predictor has no effect. The NA means the data cannot separate the two columns, not that either effect is zero.

**Verify:** `qr(redundant)$rank < ncol(redundant)` returns TRUE, since the rank is 2 and there are 3 columns.

### Exercise 5

Handle a factor level absent from training data.

Do not silently invent a learned effect for an unseen category.

**Approach:** Decide in advance what happens to a category absent from training: reject the row, or route it to a stated fallback and report how many rows took that path.

**Why it holds here:** The model only has A and B. A row with group C has no column, and `factor("C", levels = c("A", "B"))` is NA; predict on an lm fit stops with a new level error.

**Tempting mistake:** Replacing the NA with A so that prediction runs. C then silently receives A's intercept and slope, an effect the data never estimated.

**Verify:** `"C" %in% levels(data$group)` returns FALSE, and `factor("C", levels = c("A", "B"))` returns NA.

### Exercise 6

Separate algebraic fit from model validity.

Use diagnostics and held-out evaluation after defining the statistical question.

**Approach:** State the statistical question first, then judge the model with residual diagnostics and held out data, not with the fact that the design is solvable.

**Why it holds here:** The interaction design has full rank with four observations, so a fit reproduces all four values with zero residuals. That is a property of the algebra, and it leaves no degrees of freedom to check anything.

**Tempting mistake:** Taking the perfect fit as support for the model. Any four values at these x and group settings would be fit perfectly.

**Verify:** `nrow(interaction) - qr(interaction)$rank` returns 0, which shows there is no residual information for checking the model.

## What the checks establish

The assertions confirm that the additive design has columns `(Intercept)`, `x` and `groupB`, that the interaction design adds `x:groupB` and has full rank, that a design with a redundant column loses rank, and that no unobserved level C appears. They do not show that any coefficient is meaningful; full rank only means each column can be estimated separately.

The reference makes 5 `stopifnot()` checks; see [what a passing run proves](../STUDY-GUIDE.md#what-a-passing-run-proves).
