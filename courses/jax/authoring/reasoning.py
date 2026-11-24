"""Explained-reference reasoning for each JAX unit, keyed by unit number.

Each entry states the solution approach, why it holds for that unit's fixture,
one plausible wrong approach per exercise with the reason it fails, and how to
verify the reference. Write every sentence about the unit's own code and values.
"""

from model import Reasoning

REASONING: dict[int, Reasoning] = {
    1: Reasoning(
        approach=(
            "Every exercise reuses two small functions. `predict` multiplies the scalar weight "
            "by the input vector `x = [1, 2, 3]`, and `mse` validates that inputs and targets are "
            "nonempty vectors of equal shape before averaging the squared residuals. Work each "
            "task by hand first: write the predictions, subtract the targets, square, sum, and "
            "divide by three. Only then compare the hand value with the JAX result."
        ),
        correctness=(
            "The targets are exactly `2 * x`, so the residual at weight `w` is `(w - 2) * x`. "
            "The loss is therefore `(w - 2) ** 2 * (1 + 4 + 9) / 3 = 14 * (w - 2) ** 2 / 3`. "
            "That closed form gives 56/3 at weight 0, 14/3 at weight 1 and 0 at weight 2, which "
            "is why the asserted values are exact rather than approximate."
        ),
        pitfalls=(
            "Computing `mse(1., x, y)` as the mean of the errors instead of the squared errors "
            "gives -2 rather than 14/3, because the residuals [-1, -2, -3] are all negative and "
            "never cancel into a squared quantity.",
            "Searching for the weight with a gradient step is unnecessary and hides the point: "
            "dividing any target by its input gives 2 for every observation, so the fit is "
            "algebraic and a single `mse(2., x, y)` call proves it.",
            "Dividing the single squared residual of 1 by the count of changed targets, one, "
            "reports a loss of 1. The mean still runs over all three observations, so the "
            "correct value is 1/3.",
            "Letting `jnp.mean` run on two empty arrays returns NaN with a runtime warning, "
            "which looks like a number in logs. The guard `inputs.size == 0` raises ValueError "
            "before any reduction runs.",
            "Comparing `jnp.sum` with `mse` directly fails because 56 is three times 56/3. The "
            "equality only holds after multiplying the mean by the observation count of three.",
            "Reporting the predictions [8, 10] as evidence that weight 2 generalizes confuses "
            "arithmetic with evaluation. The inputs 4 and 5 were written by the author, so "
            "they test the multiplication, not data the rule has never seen.",
        ),
        verification=(
            "Run `courses/jax/solutions/jax-001_solution.py` in the `jax-cpu` profile; the last "
            "line reads `jax-001: 8 asserted cases passed`. Independently, evaluate the closed "
            "form `14 * (w - 2) ** 2 / 3` at w = 0, 1 and 2 on paper and confirm 56/3, 14/3 and "
            "0. Then pass `y[:, None]` to `mse` and confirm the ValueError, which shows the shape "
            "guard rather than broadcasting decided the result."
        ),
    ),
    2: Reasoning(
        approach=(
            "The fixture `table = jnp.arange(6.).reshape(2, 3)` holds rows [0, 1, 2] and "
            "[3, 4, 5]. Before each task, write the shape of every operand and line the "
            "shapes up from the right: (2, 3) against (3,) broadcasts along rows, while (2, 3) "
            "against (2, 1) broadcasts along columns. Updates use `.at[...]`, which returns a "
            "new array and leaves the original untouched."
        ),
        correctness=(
            "Row means are 1 and 4, so subtracting a (2, 1) mean column gives [-1, 0, 1] in both "
            "rows and each centered row sums to zero. Offsets of shape (3,) add 10, 20 and 30 to "
            "the three columns; offsets reshaped to (2, 1) add 10 to every entry of row 0 and 20 "
            "to every entry of row 1. These sums can be read straight off the six fixture values."
        ),
        pitfalls=(
            "Dropping `keepdims=True` leaves the row means with shape (2,). Subtracting that from "
            "a (2, 3) table raises a broadcast error here, and on a (2, 2) table it would "
            "silently subtract column-wise, which is the bug a nonsquare fixture exposes.",
            "Writing the offsets as a column `[[10.], [20.], [30.]]` gives shape (3, 1), which "
            "does not broadcast against (2, 3). The feature axis is the last axis, so a flat "
            "length-3 vector is the correct alignment.",
            "Adding `jnp.array([10., 20.])` without `[:, None]` fails because a trailing length "
            "of 2 cannot align with 3 columns. The new axis is what moves the offsets onto the "
            "row dimension.",
            "Using `old.at[0].set(5.0)` replaces the 1 with 5 and returns [5, 2], not [6, 2]. "
            "The task asks for an increment, so `.add` is required; `set` silently discards the "
            "existing value.",
            "Calling `values.at[3].set(1.0)` on a length-3 vector does not raise in JAX; "
            "out-of-bounds updates are dropped by default. Relying on that would hide the bad "
            "index, which is why `replace_at` checks the bound on the host first.",
            "Reusing the (2, 3) fixture to test the axis rule cannot catch code that hard-codes "
            "three columns. The (3, 2) array changes both lengths, so a wrong axis choice "
            "produces a shape error or nonzero row sums.",
        ),
        verification=(
            "Run the reference and confirm `jax-002: 8 asserted cases passed`. For a manual "
            "check, print `table.mean(axis=1, keepdims=True).shape` and expect (2, 1), then print "
            "`centered.sum(axis=1)` and expect zeros. After the accumulate task, print `old` "
            "again and confirm it is still [1, 2], which shows the update returned a new array "
            "instead of mutating the input."
        ),
    ),
    3: Reasoning(
        approach=(
            "The header turns on 64-bit mode before any array exists, so every dtype in this "
            "lesson is requested explicitly and then asserted. Each task isolates one numerical "
            "fact: the dtype that was kept, the epsilon of each float format, an absolute-only "
            "tolerance near zero, an exact integer count, the shift identity of log-sum-exp and a "
            "finite-value precondition."
        ),
        correctness=(
            "Epsilon for float32 is exactly `2.0**-23` and for float64 exactly `2.0**-52`, so "
            "equality rather than closeness is appropriate. The scores 0 and log 3 exponentiate "
            "to 1 and 3, whose sum is 4, giving `logsumexp = log 4`. Adding 1000 to both scores "
            "multiplies each exponential by the same factor, which adds exactly 1000 to the log "
            "of the sum."
        ),
        pitfalls=(
            "Checking only `jnp.array([1.0]).dtype` shows float64 under the X64 header and "
            "float32 without it, so it tests the global setting rather than the requested dtype. "
            "Passing `dtype=` explicitly is what makes both assertions meaningful.",
            "Treating epsilon as the absolute error of any float32 result is wrong: near 1000 "
            "the spacing of float32 values is `2**-14`, 512 times larger than `2**-23`, because "
            "spacing scales with the binary exponent.",
            "Using the default relative tolerance to compare 1e-12 with 0.0 fails because "
            "`rtol * |0|` is zero. Without an explicit `atol`, any nonzero residual near zero "
            "is rejected no matter how small.",
            "Summing the counts after casting them to float32 still returns 10.0 here, but it "
            "turns an exact integer total into an approximate one and changes the scalar dtype, "
            "so the `int` comparison no longer documents exactness.",
            "Computing `jnp.log(jnp.sum(jnp.exp(scores + 1000.0)))` directly overflows, because "
            "`exp(1000)` exceeds the float64 range and returns inf. The library subtracts the "
            "maximum first, which keeps every exponential at most one.",
            "Comparing NaN and inf with a wide tolerance does not make them valid. "
            "`assert_allclose` treats matching NaNs as equal by default, so the `isfinite` check "
            "must run before any tolerance is applied.",
        ),
        verification=(
            "Run the reference and expect `jax-003: 8 asserted cases passed`. Then print "
            "`jnp.finfo(jnp.float32).eps` and `jnp.finfo(jnp.float64).eps` and compare them "
            "with `2.0**-23` and `2.0**-52`. Evaluate the unstable `log(sum(exp(scores + "
            "1000)))` once to see inf, and contrast it with the `logsumexp` difference of 1000 "
            "to confirm why the stable form is used."
        ),
    ),
    4: Reasoning(
        approach=(
            "State is the pair `(total, count)` and `transition` returns a new pair instead of "
            "editing anything in place. Each task asks which pair results from a given sequence "
            "of observations, so trace the pair by hand: start at (0, 0), add the value to the "
            "total and one to the count, and divide only when the count is positive."
        ),
        correctness=(
            "From (0, 0), the values 1, 3 and 8 produce (1, 1), (4, 2) and (12, 3), so the mean "
            "is 4. Feeding 20 into the saved (12, 3) gives (32, 4) and a mean of 8. The groups "
            "(6, 2), (9, 3) and (5, 1) combine to (20, 6), a mean of 10/3, because totals and "
            "counts add independently of grouping."
        ),
        pitfalls=(
            "Passing the first result into the second call, `transition(transition(initial, "
            "5.0), 5.0)`, gives (10, 2) and makes the two runs differ. Replay means the same "
            "input state and value, which both produce (5, 1).",
            "Keeping only a running mean and updating it as `(mean + value) / 2` starts at 1, "
            "moves to 2 after the 3 and ends at 5 after the 8, not 4. Without the count, the "
            "latest value is overweighted.",
            "Returning `total / max(count, 1)` reports a mean of 0 for the empty state. Zero "
            "observations do not have a mean of zero, so `mean_of` raises ValueError instead.",
            "Continuing from the printed mean 4 alone cannot weight the new value of 20; "
            "`(4 + 20) / 2 = 12` is wrong. The saved total 12 and count 3 are what give the "
            "correct mean of 8.",
            "Concluding that floating sums are always order-independent overreaches. These values "
            "are small integers that float64 represents exactly; long sums of mixed magnitudes "
            "can round differently when reordered.",
            "Averaging the three group means 3, 3 and 5 gives 11/3, not 10/3. That treats each "
            "group as one observation, while the group with three items should count three "
            "times as much.",
        ),
        verification=(
            "Run the reference and expect `jax-004: 8 asserted cases passed`. For an independent "
            "check, compute `sum([1, 3, 8]) / 3` and `sum([1, 3, 8, 20]) / 4` in plain Python and "
            "compare them with `mean_of` on the traced states. Calling `mean_of(initial)` must "
            "raise ValueError, and swapping the order of the three values must leave (12, 3) "
            "unchanged."
        ),
    ),
    5: Reasoning(
        approach=(
            "Treat every random draw as a pure function of a key. `draw_step` splits its key "
            "into a key to carry forward and a key to consume, draws four normals with the "
            "consumed key, and returns both. Each task then asks a question about key identity, "
            "which `same_key` answers by comparing the raw `key_data` arrays rather than sampled "
            "values."
        ),
        correctness=(
            "The same root and the same `fold_in` identifier always produce the same key, so "
            "identifier 42 replays and identifier 43 differs. `split` into four yields four keys "
            "with distinct data. The sequence function starts from `key(19)` and applies the same "
            "three transitions both times, so its final keys and stacked (3, 4) draws must match."
        ),
        pitfalls=(
            "Checking `isinstance(key, float)` or printing the key tells little about its "
            "representation. The typed key has shape () and its contents are integer words "
            "reached through `jax.random.key_data`.",
            "Comparing four uniform draws for distinctness tests sampled values, which could "
            "collide by chance. The task checks stream allocation, so the reference compares the "
            "bytes of each key's data.",
            "Deriving a record key with `jax.random.key(3 + 42)` mixes the root seed and record "
            "identifier into one integer, so root 4 with record 41 would collide. `fold_in` "
            "keeps the two inputs separate.",
            "Testing that draws from records 42 and 43 differ in their first value is weak: two "
            "floats could coincide. Comparing key data states the property that actually "
            "separates the two streams.",
            "Writing `draw_step(key)` without rebinding `key` in the loop reuses the same key "
            "three times, producing three identical rows. The returned next key must replace "
            "the old one at every step.",
            "Reading two equal Bernoulli masks as bad luck misses the cause: the same key always "
            "gives the same eight values. After `split`, `k1` and `k2` differ even if some mask "
            "entries still match.",
        ),
        verification=(
            "Run the reference and expect `jax-005: 8 asserted cases passed`. As an extra check, "
            "draw `jax.random.uniform(jax.random.key(11), (3,))` twice in one script and confirm "
            "equality, then draw from `jax.random.split(jax.random.key(11))[0]` and confirm the "
            "values change. Inspect the `(3, 4)` shape of the stacked sequence draws before "
            "comparing their values."
        ),
    ),
    6: Reasoning(
        approach=(
            "Treat `params` as a ledger of named arrays: a (2, 2) weight and a (2,) bias. Each "
            "task either reads that ledger with `jax.tree.map` and `jax.tree.leaves`, or pairs it "
            "with a second tree of the same structure. `checked_update` refuses to pair trees "
            "until both the structure and every leaf shape agree, and only then applies "
            "`p - rate * g` leaf by leaf."
        ),
        correctness=(
            "The weight holds four entries and the bias two, so the scalar count is six. With "
            "gradient 2 everywhere on the weight and rate 0.5, each weight entry drops by 1, "
            "turning [[1, 2], [3, 4]] into [[0, 1], [2, 3]]. The bias [1, -1] minus 0.5 times "
            "[3, -4] is [-0.5, 1]. Adding the scalar counter to the tuple makes seven zeroed "
            "entries."
        ),
        pitfalls=(
            "Mapping `len` over the leaves reports 2 for both arrays, because the weight has two "
            "rows and the bias two entries. Only `.shape` distinguishes the (2, 2) matrix from "
            "the (2,) vector.",
            "Counting `len(jax.tree.leaves(params))` gives 2, the number of arrays, not 6. The "
            "question asks for stored scalars, so each leaf's `.size` must be summed.",
            "Rebuilding the dictionary as `dict(zip(params.keys(), leaves))` swaps the arrays: "
            "JAX flattens dictionaries in sorted key order, bias before weight, while "
            "`params.keys()` follows insertion order, weight first.",
            "Zipping leaves without the structure check pairs the bias (2,) with the only "
            "gradient leaf, the (2, 2) weight gradient. Broadcasting then returns a (2, 2) bias "
            "with no error, which is why the tree structure is compared first.",
            "Adding the step instead of subtracting it gives weight [[2, 3], [4, 5]] and bias "
            "[2.5, -3]. The values look plausible, so only the asserted numbers catch the sign "
            "error.",
            "Calling `jnp.zeros_like(state)` on the whole tuple tries to turn a dictionary and a "
            "scalar into one array and fails. `jax.tree.map` applies `zeros_like` to each of the "
            "three leaves separately.",
        ),
        verification=(
            "Run the reference and look for `jax-006: 8 asserted cases passed`. Print "
            "`jax.tree.leaves(params)` and note that the bias appears first, which explains the "
            "key-order trap. Then call `checked_update` with a gradient whose bias has shape "
            "(3,) and confirm the leaf-shape ValueError, proving both guards run before any "
            "arithmetic."
        ),
    ),
    7: Reasoning(
        approach=(
            "Write the loss in closed form before calling `jax.grad`. With `x = [1, 2, 3]` and "
            "`y = 2 * x`, the residual is `(w - 2) * x`, so `L(w) = 14 * (w - 2) ** 2 / 3` and "
            "`L'(w) = 28 * (w - 2) / 3`. Every task compares autodiff with this formula, with a "
            "central difference, or with a hand derivative for an extra parameter."
        ),
        correctness=(
            "At w = 1 the formula gives -28/3, and at w = 2 both value and slope are zero. "
            "Summing instead of averaging multiplies the gradient by three, giving -56 at zero. "
            "For the affine model at zero, the residuals are -y = [-2, -4, -6]; the bias "
            "derivative is `2 * mean(-y) = -8` and the weight derivative is "
            "`2 * mean(-y * x) = -56/3`."
        ),
        pitfalls=(
            "Dropping the factor 2 from the derivative of the square gives -14/3 at weight one. "
            "Autodiff applies the full chain rule, so the hand formula must keep "
            "`2 * (w * x - y) * x`.",
            "A forward difference `(loss(w + h) - loss(w)) / h` carries an error near "
            "`h * L'' / 2`, about 4.7e-5 for `L'' = 28/3`, which fails the 1e-8 bound. The "
            "central difference cancels that term for this quadratic.",
            "Expecting the summed loss to share the mean loss gradient of -56/3 ignores the "
            "missing division by three. The two objectives have the same minimizer but "
            "different slopes.",
            "Locating the optimum by noticing that `loss(1.5)` and `loss(2.5)` both equal 7/6 "
            "suggests symmetry around 2 but does not show a zero slope. `value_and_grad` at "
            "2.0 checks the value and the derivative directly.",
            "Leaving out the factor 2 for the bias gives -4, the plain mean residual. The bias "
            "enters every prediction with coefficient one, so its derivative is twice the mean "
            "residual, -8.",
            "Swapping `jax.grad` for `jax.jacobian` makes the error disappear but returns three "
            "per-observation slopes [-4, -16, -36]. No objective was chosen; the mean of that "
            "vector, -56/3, is the gradient of the mean loss.",
        ),
        verification=(
            "Run the reference and confirm `jax-007: 8 asserted cases passed`. Then evaluate "
            "`28 * (w - 2) / 3` at w = 0, 0.7 and 1 by hand and compare with `jax.grad(loss)`. "
            "Apply one SGD step with rate 0.1 from zero to reach 28/15, and check that "
            "`loss(28 / 15)` equals 56/675, which ties the gradient to a decrease in the loss."
        ),
    ),
    8: Reasoning(
        approach=(
            "Fix the point `(2, 0)` and write the 3 by 2 Jacobian of "
            "`(a * a, a * b, sin(b))` by hand: rows [4, 0], [0, 2] and [0, 1]. A JVP multiplies "
            "that matrix by an input-space direction and returns three numbers. A VJP multiplies "
            "its transpose by an output-space cotangent and returns two numbers. Each task "
            "chooses a direction or cotangent and predicts the result from the matrix."
        ),
        correctness=(
            "Direction [1, 0] selects the first column [4, 0, 0]. Cotangent [0, 1, 0] selects "
            "the second row [0, 2]. With v = [3, 4], Jv = [12, 8, 4] and u . Jv = 12 + 16 + 12 "
            "= 40; with u = [1, 2, 3], the pullback is [4, 7] and v . [4, 7] = 12 + 28 = 40. At "
            "(1, 1) the rows become [2, 0], [1, 1] and [0, cos 1]."
        ),
        pitfalls=(
            "Expecting the JVP along [1, 0] to return the first row [4, 0] confuses the two "
            "products. A JVP output lives in the three-dimensional output space, so it is the "
            "first column [4, 0, 0].",
            "Passing the input-shaped vector [0, 1] to `back` is rejected, because the "
            "cotangent must match the output shape (3,). The pullback consumes output "
            "sensitivities and returns input sensitivities.",
            "Comparing `Jv` with `J^T u` directly compares a length-3 vector with a length-2 "
            "vector. Duality is a statement about two scalars, `u . Jv` and `v . J^T u`, both 40.",
            "A one-sided difference along [3, 4] with h = 1e-5 has an error of about "
            "`h / 2` times the second directional derivative, 18 for the first output, giving "
            "roughly 9e-5. That breaks the 1e-8 bound; the central form passes.",
            "Reusing the stored `jacobian` constant at [1, 1] gives the wrong answer, since that "
            "matrix was computed for (2, 0). Both the bilinear entries and `cos(b)` change with "
            "the point.",
            "Differentiating the unweighted `jnp.sum(function(z))` gives J^T [1, 1, 1] = [4, 3], "
            "not [4, 7]. The weights [1, 2, 3] are the cotangent, and dropping them changes the "
            "objective.",
        ),
        verification=(
            "Run the reference and confirm `jax-008: 8 asserted cases passed`. Then compute "
            "`jax.jacfwd(function)(point)` and compare it entry by entry with the hand matrix. "
            "Multiply that matrix by [3, 4] and its transpose by [1, 2, 3] with plain NumPy, "
            "and confirm you get [12, 8, 4] and [4, 7] independently of the JVP and VJP calls."
        ),
    ),
    9: Reasoning(
        approach=(
            "Differentiate `a * a + a * b + 2 * b * b` by hand first: the gradient is "
            "`(2a + b, a + 4b)` and the Hessian is [[2, 1], [1, 4]] everywhere. The tasks then "
            "check the first derivative at (1, 2), compare two ways of building the Hessian, "
            "form a Hessian-vector product without the matrix, and contrast this constant "
            "curvature with the point-dependent curvature of `z ** 4`."
        ),
        correctness=(
            "At (1, 2) the gradient is (2 + 2, 1 + 8) = (4, 9). For v = [2, -1], Hv = (4 - 1, "
            "2 - 4) = (3, -2), and `v . Hv = 6 + 2 = 8`. A degree-two polynomial has a constant "
            "Hessian, so (-3, 7) returns the same matrix. For `z ** 4` the second derivative is "
            "`12 * z ** 2`, which is 0 at zero and 48 at two."
        ),
        pitfalls=(
            "Forgetting that the cross term `a * b` feeds both partial derivatives gives (2, 8) "
            "instead of (4, 9). Each coordinate's derivative picks up the other coordinate from "
            "that product.",
            "Calling `jax.jacrev(quadratic)(point)` returns the gradient [4, 9] with shape (2,), "
            "not the Hessian. The second derivative needs `jacrev` applied to `jax.grad`, which "
            "produces the (2, 2) result.",
            "Central-differencing the scalar loss along v gives the directional derivative "
            "`grad . v = 8 - 9 = -1`, a single number. The matrix-free product perturbs the "
            "gradient function, which returns the vector [3, -2].",
            "Reading the mixed-sign vector Hv = [3, -2] as evidence of negative curvature is a "
            "misreading. Curvature along v is the scalar `v . Hv = 8`, which is positive.",
            "Building the evaluation point as `jnp.array([-3, 7])` creates an integer array, "
            "and JAX refuses to differentiate integer inputs. The float literals make the "
            "Hessian call valid.",
            "Storing the curvature of `z ** 4` measured at zero, which is 0, and reusing it at "
            "z = 2 predicts no bending where the true value is 48. Nonquadratic curvature must "
            "be recomputed at each point.",
        ),
        verification=(
            "Run the reference and confirm `jax-009: 8 asserted cases passed`. Print "
            "`jax.hessian(quadratic)(point)` and compare it with [[2, 1], [1, 4]]. Then compute "
            "`jax.jvp(jax.grad(quadratic), (point,), (v,))[1]` as a second matrix-free route "
            "and expect [3, -2], matching both the finite difference and `expected_hessian @ v`."
        ),
    ),
    10: Reasoning(
        approach=(
            "Separate what JIT changes from what it must preserve. Values must match the eager "
            "function, but tracing happens once per abstract signature, so each task looks at "
            "one consequence: equal outputs, a new trace for a new shape, a Python branch that "
            "cannot see a traced value, a static loop count, a composition with `grad`, and "
            "the staged jaxpr."
        ),
        correctness=(
            "The polynomial `z * z + z + 1` gives 3, 7 and 13 on [1, 2, 3] in either mode. The "
            "traced function sees shapes (2,) and (3,), so it traces twice. `n` is static, so "
            "`n = 0` unrolls to no additions and returns `0. * value`. The gradient of "
            "`sum(z * z)` is `2 * z`, giving [2, 4] at [1, 2]."
        ),
        pitfalls=(
            "Timing the first JIT call to compare with eager execution answers a different "
            "question. That call includes tracing and compilation, and the task only asks "
            "whether the values [3, 7, 13] agree.",
            "Calling the compiled function twice with length-2 inputs records only one trace, "
            "because the second call reuses the cached specialization. The shapes must differ "
            "to show a new trace.",
            "Marking `z` static with `static_argnums=0` does not repair the branch. JAX arrays "
            "are not hashable, so the call fails, and static numerical values would retrace for "
            "every new number anyway.",
            "Starting the carry at the Python float `0.` instead of `0. * value` returns a bare "
            "scalar when `n = 0` and the input is a vector. Multiplying by `value` keeps the "
            "input's shape and dtype.",
            "Reading the gradient as `z` itself, [1, 2], forgets the factor 2 from the square. "
            "The derivative of the sum of squares is `2 * z`, so the compiled and eager "
            "gradients are both [2, 4].",
            "Asserting an exact equation count, such as two, ties the test to one JAX version's "
            "lowering. The reference only asserts at least one equation and exactly one output "
            "variable.",
        ),
        verification=(
            "Run the reference and confirm `jax-010: 8 asserted cases passed`. Print "
            "`jax.make_jaxpr(lambda z: z * z + 1)(2.0)` to see the multiply and add equations "
            "yourself. Add a third call to `compiled` with length 2 and confirm the trace list "
            "stays at two entries, which shows the cache, not the formula, controls retracing."
        ),
    ),
    11: Reasoning(
        approach=(
            "Unroll `h_new = 0.5 * h + v` by hand before trusting the primitives. Three steps "
            "give `h3 = h0 / 8 + v0 / 4 + v1 / 2 + v2`, which predicts both gradient tasks at "
            "once. The remaining tasks probe the contract of each loop primitive: `scan` with "
            "zero steps, `fori_loop` with a fixed index range, `while_loop` under forward-mode "
            "differentiation, and a carry that is a vector rather than a scalar."
        ),
        correctness=(
            "The unrolled formula has coefficient 1/8 on `h0` and coefficients [1/4, 1/2, 1] "
            "on the inputs. An empty scan returns its initial carry 5 and a history of shape "
            "(0,). Indices 0 to 3 sum to 6. Starting at one, doubling reaches 2, 4, 8 and 16, so "
            "the output is 16 and the tangent is 2 ** 4 = 16. Inputs [2, 4] then [1, 2] give "
            "[2, 4] and then `0.5 * [2, 4] + [1, 2] = [2, 4]`."
        ),
        pitfalls=(
            "Counting only the transitions after the first input and answering 1/4 misreads the "
            "recurrence. Each of the three steps halves the carry, including the first, so the "
            "initial state contributes 0.5 ** 3.",
            "Reporting [1, 1/2, 1/4] reverses the order. The last value is added after every "
            "halving, so it reaches the output untouched, while the first value is halved by "
            "the two later steps.",
            "Expecting an empty scan to raise, or to return zero, treats it like a reduction "
            "with a missing identity. `scan` simply never calls `step`, so the carry passes "
            "through as 5.",
            "Treating the `fori_loop` upper bound as inclusive adds index 4 and reports 10. The "
            "bounds follow Python `range(0, 4)`, which stops before the upper value.",
            "Using `jax.grad` on `double_until` fails, because reverse mode cannot "
            "differentiate a `while_loop` whose trip count is decided at run time. Forward mode "
            "through `jax.jvp` works and gives 16.",
            "Starting the batched run from the scalar `0.` breaks the carry contract: after one "
            "step the carry would become shape (2,), and `scan` requires the carry returned by "
            "`step` to match the carry it received.",
        ),
        verification=(
            "Run the reference and confirm `jax-011: 8 asserted cases passed`. Write a plain "
            "Python loop over [2, 2, 2] from zero and compare its 3.5 with "
            "`recurrence(0., values)[0]`. Then try `jax.grad(double_until)(1.)` once to see the "
            "reverse-mode error, which explains why the lesson uses `jax.jvp` for the "
            "dynamic stopping rule."
        ),
    ),
    12: Reasoning(
        approach=(
            "Name the mapped axis before writing `in_axes`. Prediction batches map the feature "
            "rows and share one weight, so `in_axes=(None, 0)`. The model comparison maps the "
            "weight rows and shares one feature vector, so `in_axes=(0, None)`. For gradients, "
            "the per-example derivative of the squared error is `2 * (w . x - t) * x`, which "
            "at zero weight is `-2 * t * x`."
        ),
        correctness=(
            "With w = [2, -1], the rows [1, 2] and [3, 4] give 2 - 2 = 0 and 6 - 4 = 2. At zero "
            "weight the per-example gradients are -2 * 1 * [1, 2] = [-2, -4] and -2 * 2 * "
            "[3, 4] = [-12, -16], whose mean is [-7, -10] and sum [-14, -20]. The three models "
            "applied to [2, 3] give 2, 3 and 2 + 3 = 5."
        ),
        pitfalls=(
            "Mapping both arguments with `in_axes=0` pairs weight entry 2 with row [1, 2] and "
            "entry -1 with row [3, 4]. Each call then sees a scalar weight against a length-2 "
            "row, which `vdot` rejects.",
            "Assuming the mean of per-example gradients always equals the gradient of the batch "
            "objective ignores weighting. With unequal observation weights the plain mean of "
            "the per-example rows no longer matches.",
            "Reusing [-7, -10] for the summed objective halves the step an optimizer would "
            "take. Summing two equally weighted examples doubles the gradient to [-14, -20].",
            "Keeping `in_axes=(None, 0)` for the model comparison hands the whole (3, 2) weight "
            "matrix to every call and maps over the scalars of [2, 3]. That is a shape error, "
            "not a set of three predictions.",
            "Wrapping only `predict_one` in `jax.jit` and keeping a Python loop gives the "
            "same [0, 2] but never tests whether `jit` composes with `vmap`. The task compiles "
            "the mapped function itself.",
            "Closing over one key, as in `jax.vmap(lambda _: jax.random.normal(key, (2,)))`, "
            "produces three identical rows. Splitting into three keys and mapping over them "
            "gives each row its own stream.",
        ),
        verification=(
            "Run the reference and confirm `jax-012: 8 asserted cases passed`. Print "
            "`jax.vmap(jax.grad(loss_one), in_axes=(None, 0, 0))(jnp.zeros(2), features, "
            "targets)` and expect the rows [-2, -4] and [-12, -16]. Averaging and summing that "
            "(2, 2) array by hand reproduces both batch gradients without calling the batch "
            "losses."
        ),
    ),
    13: Reasoning(
        approach=(
            "Split the work between two functions with different jobs. `admit` runs on the "
            "host with NumPy and rejects malformed inputs before any loss exists: wrong shapes, "
            "a non-Boolean or empty mask, or an active label outside the classes. `token_mean` "
            "is pure JAX: it replaces inactive labels with 0, gathers the log-softmax of each "
            "target, zeroes inactive rows, and divides by the active count."
        ),
        correctness=(
            "Uniform logits over three classes give probability 1/3 for every target, so each "
            "active row costs log 3 and their mean is log 3 regardless of padding. For logits "
            "[log 3, 0] the softmax is [3/4, 1/4], so target 0 costs log(4/3) and target 1 "
            "costs log 4. For [1000, 0, -1000] the target already holds nearly all the mass, "
            "so the loss is close to zero."
        ),
        pitfalls=(
            "Dividing by the number of stored rows instead of `active.sum()` turns the padded "
            "fixture into `3 * log 3 / 6`, half the correct value. Padding would then change "
            "the objective it should not affect.",
            "Skipping `admit` for an all-false mask lets `token_mean` compute 0 / 0, which is "
            "NaN rather than an error. Reporting zero instead would claim perfect prediction "
            "with no evidence.",
            "Checking target identity only on the uniform fixture cannot catch a label swap, "
            "since every class scores log 3 there. The nonuniform row separates log(4/3) from "
            "log 4.",
            "Computing `jnp.log(jnp.exp(z) / jnp.exp(z).sum())` overflows `exp(1000)` to "
            "infinity and returns NaN. `jax.nn.log_softmax` subtracts the row maximum first.",
            "Relying on the gather to fail for the active label -100 does not work, because "
            "JAX does not raise index errors for out-of-range gathers. The host-side bounds "
            "check in `admit` is what rejects it.",
            "Calling `admit` inside the function passed to `jax.jit` fails, because "
            "`np.asarray` cannot convert a tracer to a concrete array. Validation belongs "
            "before the compiled call, as the reference does.",
        ),
        verification=(
            "After the reference prints `jax-013: 8 asserted cases passed`, line up "
            "`token_mean` with `-jax.nn.log_softmax(logits)[jnp.arange(3), targets[:3]].mean()` "
            "on the first three rows to confirm the mask removes only the sentinel. Then pass "
            "integer zeros as the mask and confirm `admit` reports the Boolean requirement."
        ),
    ),
    14: Reasoning(
        approach=(
            "Treat every optimizer as a function from (weight, state, gradient) to (new weight, "
            "new state), and step it by hand. Momentum keeps one velocity, `v = 0.9 * v + g`, "
            "then moves by `rate * v`. Adam keeps a first moment, a second moment and a step "
            "counter, divides each moment by its bias correction, and moves by the corrected "
            "mean over the root of the corrected square."
        ),
        correctness=(
            "SGD gives 1 - 0.2 * 3 = 0.4. Momentum gives velocity 2 and weight -0.2, then "
            "velocity 1.8 + 2 = 3.8 and weight -0.2 - 0.38 = -0.58. Adam's first step stores "
            "m = 0.2 and s = 0.004; corrected they are 2 and 4, so the step is about 0.1. On the "
            "second step m = 0.38 over 0.19 is still 2 and the corrected square is still 4."
        ),
        pitfalls=(
            "Moving by the old velocity before adding the gradient makes the first momentum "
            "step zero. The reference updates the velocity first, which is why the first weight "
            "is already -0.2.",
            "Calling `adam_step` twice with a fresh `zero_state` also lands near -0.2, since a "
            "constant gradient gives the same first step each time. Only the counter, 1 instead "
            "of 2, reveals the lost state.",
            "Dropping the bias correction makes the first Adam step 0.1 * 0.2 / sqrt(0.004), "
            "about 0.32, instead of about 0.1. The early moments are biased toward their zero "
            "start.",
            "Treating a zero gradient as no update ignores the stored first moment. Here "
            "m = 0.18 and the corrected values give a further step of about 0.067, so the "
            "weight keeps decreasing.",
            "Comparing only the weights after `jax.jit(adam_step)` misses a state that could "
            "differ, such as a counter that failed to increment. The reference compares all "
            "three state leaves.",
            "Expecting a negative second moment after gradient -2 forgets that it stores "
            "squares. Only the first moment flips to -0.2; the square stays 0.004, so the "
            "update is +0.1.",
        ),
        verification=(
            "Run the reference and confirm `jax-014: 8 asserted cases passed`. Then print the "
            "three state leaves after each of two Adam steps with gradient 2 and check m = 0.2 "
            "then 0.38, s = 0.004 then 0.007996, and counter 1 then 2. Dividing each by its "
            "bias correction reproduces the corrected values 2 and 4."
        ),
    ),
    15: Reasoning(
        approach=(
            "Keep the network small enough to audit: a (1, 4) input weight, a (4,) hidden "
            "bias, a (4, 1) output weight and a (1,) output bias, thirteen scalars in all. "
            "Training is 120 compiled calls of a plain gradient step with rate 0.05 on five "
            "points of `tanh(2x)`. Each task then checks one property of that pipeline rather "
            "than a tuned accuracy target."
        ),
        correctness=(
            "Replay holds because `initialize` derives both weight draws from one key by a "
            "fixed split. The gradient tree mirrors the parameter tree leaf for leaf. One eager "
            "step and one compiled step consume identical state, batch and rate, so their "
            "leaves agree. Width four gives 4 + 4 + 4 + 1 = 13 parameters and width five gives "
            "16, since each hidden unit brings one input weight, one bias and one output weight."
        ),
        pitfalls=(
            "Replaying with `jax.random.key(31)` but splitting it in another order, or drawing "
            "the output weight first, gives different values under the same seed label. The "
            "whole initialization policy must be replayed.",
            "Asserting that every gradient leaf is nonzero fails here. Inputs and targets are "
            "symmetric about zero and the initial network is odd, so the mean residual and the "
            "output bias gradient are exactly zero at initialization.",
            "Comparing the eager and compiled paths after unequal step counts, or after "
            "training one path, compares two different states. The parity check uses one step "
            "from the same initialization.",
            "Choosing an acceptance threshold after looking at the held-out loss turns the "
            "two points at -0.75 and 0.75 into tuning data. The lesson reports the value and "
            "asserts only that it is finite and nonnegative.",
            "Expecting inference to need a mode switch or key is a habit from dropout models. "
            "This network has no stochastic layer, so two forward calls with the same "
            "parameters must match exactly.",
            "Counting four new parameters per hidden unit, including an extra output bias, "
            "predicts 17 for width five. The output bias belongs to the single output and is "
            "shared, so the count is 16.",
        ),
        verification=(
            "Run the reference and confirm `jax-015: 8 asserted cases passed`. Print "
            "`jax.tree.map(jnp.shape, initialize(jax.random.key(31)))` and sum the sizes to "
            "get 13. Then print the gradient's `b2` leaf at initialization and confirm it is "
            "zero, which shows why the reference checks the total gradient norm instead."
        ),
    ),
    16: Reasoning(
        approach=(
            "Write the dropout contract before any sampling: in training mode a Bernoulli mask "
            "with probability `keep` chooses which entries survive, and survivors are divided "
            "by `keep` so the expected value is unchanged. In evaluation mode the input passes "
            "through untouched. With an input of ones and keep 0.5, every output entry is "
            "therefore either 0 or 2."
        ),
        correctness=(
            "One key always produces one mask, so two calls agree. Keep 1 makes the mask all "
            "true and the scale one. `validate_keep` rejects 0 because the interval is open at "
            "zero. The derivative of `sum(where(mask, x / keep, 0))` is `mask / keep`, which "
            "equals the dropped output of a ones vector. Every entry of the 4096 sample lies in "
            "{0, 2}, so the mean lies in [0, 2]."
        ),
        pitfalls=(
            "Expecting two training calls to differ because dropout is random confuses "
            "sampling with key management. A new mask needs a new key, usually from "
            "`jax.random.split`; the same key replays the same mask.",
            "Applying the mask without dividing by `keep` gives outputs of 0 or 1 and halves "
            "the expected activation. With keep 1 that bug is invisible, which is why the "
            "fixture uses 0.5 elsewhere.",
            "Allowing keep 0 seems to mean drop everything, but the survivor scale `1 / keep` "
            "is infinite. Even though the output would be all zeros, the scale factor poisons "
            "derivatives, so the lesson rejects it.",
            "Treating dropout as the identity when differentiating predicts a gradient of all "
            "ones. The gradient is the sampled mask divided by keep, so dropped entries "
            "contribute zero and survivors contribute two.",
            "Compiling with `jax.jit(dropout)` and no static arguments fails at `if not "
            "training`, since a traced Boolean cannot drive Python control flow. Marking "
            "`training` and `keep` static fixes that.",
            "Asserting that the mean of the 4096 sample equals one treats an expectation as a "
            "guarantee. The sample mean has a standard error of about 1/64, so only the support "
            "bound is safe to assert.",
        ),
        verification=(
            "Run the reference and confirm `jax-016: 8 asserted cases passed`. Print "
            "`dropout(values, key, training=True)` and check that it holds only zeros and twos. "
            "Then replace the key with `jax.random.split(key)[1]` and confirm the mask changes, "
            "while `training=False` still returns the ones vector exactly."
        ),
    ),
    17: Reasoning(
        approach=(
            "List what the transition `next_state` reads: weight, velocity, a random key and "
            "a step counter. A checkpoint that can continue training must store all four. "
            "The key is a typed array, so `save_state` writes its raw words with "
            "`jax.random.key_data` and `load_state` rebuilds it with `wrap_key_data` under the "
            "same `threefry2x32` implementation."
        ),
        correctness=(
            "Two calls of `next_state` from zero give count 2, and the first gradient near "
            "`2 * (0 - 2) = -4` makes the velocity nonzero. Rebuilding from root 52 repeats "
            "every split and draw. A round trip preserves values, scalar shapes and dtypes. "
            "Swapping the key changes the next key data. Two more steps from the original and "
            "the restored state match, ending at count 4."
        ),
        pitfalls=(
            "Saving before any update stores zero velocity and count zero. A loader that "
            "forgot the velocity would still pass, so the lesson prepares two steps first to "
            "exercise retained history.",
            "Saving only the weight and restarting velocity at zero changes the next update, "
            "since momentum carries 90 percent of the old velocity. The continued run would "
            "diverge from the uninterrupted one.",
            "Passing the typed key directly to `np.asarray` does not yield portable numbers. "
            "`jax.random.key_data` exposes the underlying unsigned integer words that `np.savez` "
            "can store without pickling.",
            "Rebuilding the key with a different `impl` reinterprets the stored words under "
            "another generator. The reference pins `threefry2x32` on both sides so the stream "
            "continues unchanged.",
            "Judging that a replaced key is harmless because the next weights look close "
            "ignores the stream. The next key data differs, so every later draw differs too, "
            "and the continuation is a different run.",
            "Writing the checkpoint to a fixed path in the working directory and deleting it "
            "by name risks removing a real file. `TemporaryDirectory` owns its file, and the "
            "check confirms it is gone afterward.",
        ),
        verification=(
            "Run the reference and confirm `jax-017: 8 asserted cases passed`. Open the saved "
            "file with `np.load` and print the dtype of each entry: the key should be unsigned "
            "integer words and the weight float64. Then load it, take two steps, and confirm "
            "the compare helper agrees with two steps from the unsaved state."
        ),
    ),
    18: Reasoning(
        approach=(
            "Reproduce each failure on the smallest input, name the invariant it breaks, and "
            "then repair it without changing the question. Host conversion breaks the rule "
            "that traced values stay inside JAX. Boolean indexing breaks the fixed-shape "
            "rule. Diagnostics must observe runtime values, and a repair for an invalid domain "
            "must leave the valid domain untouched."
        ),
        correctness=(
            "`np.asarray` on a tracer raises `TracerArrayConversionError`. `x[x > 0]` has a "
            "data-dependent length, so JIT raises `NonConcreteBooleanIndexError`. The masked "
            "sum keeps shape (2,) and returns 2. `jax.debug.print` prints total=3 and returns "
            "3. Disabling JIT gives [2, 5] for `x * x + 1`. On [1, 2, 4] the safe log has "
            "derivative 1 / x = [1, 0.5, 0.25]."
        ),
        pitfalls=(
            "Catching a bare `Exception` around the failing call makes the test pass for any "
            "error, including a typo. Naming `TracerArrayConversionError` proves the failure "
            "came from host conversion.",
            "Replacing `x[x > 0]` with `jnp.nonzero(x)` inside JIT hits the same problem, "
            "since its length also depends on data. It only works with a fixed `size` and fill "
            "value, which is another fixed-shape repair.",
            "Using Python `print(total)` inside the jitted function prints a tracer once, "
            "during tracing, and nothing on later calls. `jax.debug.print` is staged into the "
            "computation and reports the value 3.",
            "Accepting a function because it works under `jax.disable_jit()` treats eager "
            "success as the final test. The comparison only localizes the fault; the compiled "
            "path must still be checked.",
            "Writing `jnp.where(x > 0, jnp.log(x), 0)` hides bad values in the output but not "
            "in the gradient: the unused log branch still has an infinite or NaN derivative at "
            "nonpositive entries, which leaks NaN.",
            "Testing the safe log only at zero or negative inputs proves the repair, not the "
            "formula. A mistake such as always using the safe input 1 would also pass there; "
            "positive inputs catch it.",
        ),
        verification=(
            "Run the reference and confirm `jax-018: 8 asserted cases passed`, with the "
            "`total=3` line visible in the output. Then call "
            "`jax.grad(lambda x: jnp.where(x > 0, jnp.log(x), 0.).sum())(jnp.array([0., 1.]))` "
            "and see the NaN, and compare it with the safe extension at the same input."
        ),
    ),
    19: Reasoning(
        approach=(
            "Solve the 2 by 2 system by hand once: A = [[3, 1], [1, 2]] has determinant 5 and "
            "inverse [[2, -1], [-1, 3]] / 5. Every value in the tasks follows from that "
            "inverse, from the closed form `x1 = 2 / (2 + theta)` for the diagonal system, or "
            "from the scalar ridge formula `x'y / (x'x + lambda)`. Validation stays on the host "
            "with a condition-number policy."
        ),
        correctness=(
            "The inverse times [4, 3] gives (8 - 3, -4 + 9) / 5 = [1, 1]. The gradient of the "
            "summed solution is `A^-T [1, 1] = [1, 2] / 5 = [0.2, 0.4]`. The diagonal solution "
            "sums to `2 / (2 + theta) + 2`, whose slope at zero is `-2 / 4 = -0.5`. Ridge "
            "divides 28 by 14 + 14 and gives 1. The compiled solve of [9, 8] returns [2, 3]."
        ),
        pitfalls=(
            "Computing the gradient as `A^-1 [1, 1]` instead of the transposed solve gives the "
            "right numbers here only because A is symmetric. For a nonsymmetric matrix the "
            "pullback must use `A.T`, which the residual check confirms.",
            "Relying on `jnp.linalg.solve` to raise for [[1, 2], [2, 4]] does not work: it "
            "does not raise a Python error and can return infinite or meaningless entries. "
            "Rejection has to come from `admitted_matrix`.",
            "Rejecting matrices by a small determinant depends on scale: multiplying a "
            "well-conditioned matrix by 0.001 shrinks the determinant without making the solve "
            "any harder. The condition number is scale free.",
            "A forward difference at h = 1e-5 has an error near `h / 2` times the second "
            "derivative 0.5, about 2.5e-6, which misses the 1e-8 bound. The central difference "
            "removes that leading term.",
            "Expecting ridge to keep the coefficient 2 because y = 2x fits exactly overlooks "
            "that the penalty charges coefficient size, not residual size. Adding 14 to the "
            "denominator halves the coefficient.",
            "Treating `jax.jit(jnp.linalg.solve)` as a validated solver mistakes speed for "
            "checking. Compilation would solve a nearly singular system just as silently, so "
            "the residual and conditioning checks remain.",
        ),
        verification=(
            "Run the reference and confirm `jax-019: 8 asserted cases passed`. Compute "
            "`np.linalg.cond(np.asarray(matrix))` and note that it is small, then compute it "
            "for [[1, 2], [2, 4]] and see an enormous or infinite value. Multiplying "
            "`matrix @ jnp.array([1., 1.])` back to [4, 3] confirms the first task by residual."
        ),
    ),
    20: Reasoning(
        approach=(
            "Write the simulated value in closed form: ten Euler steps of size 0.1 multiply "
            "the initial value by `(1 - rate / 10) ** 10`. Autodiff differentiates that "
            "product, not the exponential it approximates. The tasks compare the discrete "
            "derivative with the continuous one, refine the step, and probe the edges of the "
            "recurrence at zero rate and at a step too large for decay."
        ),
        correctness=(
            "Differentiating `(1 - k / 10) ** 10` gives `-(1 - k / 10) ** 9`, which is "
            "`-0.9 ** 9` near -0.387 at k = 1, while the continuous slope is `-exp(-1)` near "
            "-0.368. Twenty steps give `-0.95 ** 19` near -0.377, closer to the limit. Rate "
            "zero keeps the multiplier at one. The initial-state slope is `0.9 ** 10`, and one "
            "step at rate 3 multiplies by 1 - 3 = -2."
        ),
        pitfalls=(
            "Expecting `jax.grad(simulate)(1.)` to return `-exp(-1)` assumes autodiff "
            "differentiates the continuous model. It differentiates the ten-step program "
            "exactly, so the answer is `-0.9 ** 9`.",
            "Loosening the tolerance until the discrete and continuous slopes agree hides "
            "discretization error instead of measuring it. The lesson asserts that they "
            "differ and then shows refinement shrinking the gap.",
            "Refining only the simulated value and assuming the derivative improves at the "
            "same rate skips the check that matters here. The derivative errors, about 0.019 "
            "and 0.009, are compared directly.",
            "Reading `rate = 0` as an empty system and expecting zero confuses the decay rate "
            "with the state. The multiplier `1 - 0 * dt` is one, so the initial value 3 is "
            "kept.",
            "Answering `0.9 ** 9` for the initial-value sensitivity reuses the rate formula. "
            "The state is linear in its initial value, so every one of the ten factors "
            "remains and the slope is `0.9 ** 10`.",
            "Accepting -2 because it is finite treats a successful run as a valid simulation. "
            "Euler decay stays positive only while `rate * dt < 1`; at rate 3 with one step the "
            "sign flips even though `exp(-3)` is positive.",
        ),
        verification=(
            "Run the reference and confirm `jax-020: 8 asserted cases passed`. Then evaluate "
            "`-(1 - 1 / n) ** (n - 1)` in plain Python for n = 10, 20 and 100 and compare "
            "each with `jax.grad(lambda k: simulate(k, steps=n))(1.)`. The values should match "
            "and drift toward `-exp(-1)` as n grows."
        ),
    ),
    21: Reasoning(
        approach=(
            "Expand the objective: the mean of `(m + s * z) ** 2` is `m ** 2 + 2 * m * s * "
            "mean(z) + s ** 2 * mean(z ** 2)`. The two-point control [-1, 1] has `mean(z) = 0` "
            "and `mean(z ** 2) = 1`, so it reduces to `m ** 2 + s ** 2` exactly. The 1024 normal "
            "draws only approximate those moments, so tasks on them check method and replay, "
            "not exact values."
        ),
        correctness=(
            "With the control pair, means [0, 1, 2] at scale 3 give 9, 10 and 13. Mean zero and "
            "scale two give 4 with zero slope in the mean. Through `s = exp(u)`, the slope in "
            "u is `2 * s * s = 18` at s = 3. The objective is quadratic in the mean, so a "
            "central difference on fixed noise matches autodiff up to rounding."
        ),
        pitfalls=(
            "Drawing fresh noise for `2 + h` and for `2 - h` makes the difference quotient "
            "measure sampling noise divided by `2 * h`, which is enormous. The same noise "
            "array must feed both evaluations.",
            "Differentiating with respect to the log scale but reporting 6 forgets the chain "
            "rule. The scale derivative 6 is multiplied by `exp(u) = 3`, giving 18.",
            "Expecting `sample_objective(2., 3., noise)` to equal 13 exactly treats the "
            "population value as the sample value. Only the authored control pair has moments "
            "that reproduce `m ** 2 + s ** 2` exactly.",
            "Computing a standard error from the two control points treats an authored design "
            "as a random sample. The variance over count formula belongs to the 1024 "
            "independent draws, with that count kept explicit.",
            "Mapping both arguments with `jax.vmap` would pair each mean with a single control "
            "entry instead of evaluating every mean on both draws. The mean is mapped and the "
            "control pair is closed over and shared.",
            "Replaying with the same key but a different shape or dtype does not reproduce the "
            "draws. The full call, key 61, shape (1024,) and float64, is the replay contract.",
        ),
        verification=(
            "Run the reference and confirm `jax-021: 8 asserted cases passed`. Print "
            "`noise.mean()` and `(noise ** 2).mean()` and check they are near 0 and 1 but not "
            "exact. Then compute `4 + 9 * (noise ** 2).mean() + 12 * noise.mean()` and confirm "
            "it equals `sample_objective(2., 3., noise)` to rounding."
        ),
    ),
    22: Reasoning(
        approach=(
            "Test a custom rule against something it did not define. Softplus has the known "
            "derivative `sigmoid(x)` and second derivative `sigmoid(x) * (1 - sigmoid(x))`. The "
            "custom square has the known derivative `2 * x`. Each task checks the rule against "
            "these independent formulas, against linearity in the tangent, at an extreme input, "
            "and at the boundary of what `custom_vjp` provides."
        ),
        correctness=(
            "At -2, 0 and 2 the gradient equals `jax.nn.sigmoid` of the same points. The rule "
            "multiplies the tangent by `sigmoid(1)`, so tangents 2 and 3 sum to tangent 5. At "
            "1000 `logaddexp(0, 1000)` is 1000 and sigmoid is 1. Four times the square has "
            "slope `4 * 2 * 3 = 24`. At zero, `sigmoid(0) * (1 - sigmoid(0)) = 0.25`."
        ),
        pitfalls=(
            "Writing softplus as `jnp.log(1 + jnp.exp(x))` overflows `exp(1000)` to infinity, "
            "so the value is infinite. `logaddexp` evaluates the same function without forming "
            "the huge exponential.",
            "Returning `sigmoid(value)` as the tangent output without multiplying by "
            "`tangent` makes the JVP ignore its direction. Tangents 2, 3 and 5 would all give "
            "the same number, and linearity fails.",
            "Having `square_backward` return `2 * saved` and ignore the cotangent passes a "
            "plain gradient check but breaks composition: the derivative of `4 * x * x` "
            "would come out as 6 instead of 24.",
            "Testing the custom gradient only at zero, where `sigmoid` is 0.5, would also "
            "accept a rule that always returns 0.5. The three points -2, 0 and 2 separate the "
            "correct rule from constant mistakes.",
            "Expecting the second derivative to fail or be zero assumes a custom JVP blocks "
            "further differentiation. JAX differentiates the rule itself, and `sigmoid` is "
            "smooth, so the answer is 0.25.",
            "Assuming `jax.jvp` works through `custom_square` because the function is a plain "
            "product overlooks the decorator. `custom_vjp` supplies only reverse mode, so the "
            "forward call raises TypeError.",
        ),
        verification=(
            "Once `jax-022: 8 asserted cases passed` appears, check "
            "`jax.grad(stable_softplus)(1.)` against `1 / (1 + math.exp(-1))` from the standard "
            "library. Then temporarily drop the cotangent factor in a copy of "
            "`square_backward` and watch the composition task fail with 6 instead of 24."
        ),
    ),
    23: Reasoning(
        approach=(
            "Write the diagonal system's solution in closed form: x = [2 / (2 + theta), 6 / 3] "
            "= [2 / (2 + theta), 2] for the right side [2, 6]. `custom_linear_solve` "
            "differentiates by solving another linear system with the supplied solver, so every "
            "derivative here is also a division by the diagonal. The tasks check that rule, "
            "compare implementations, and expose what happens when the solver lies."
        ),
        correctness=(
            "The pullback of a ones cotangent divides by the diagonal: [1 / 2, 1 / 3]. At "
            "theta 2 the first entry is 2 / 4 = 0.5 and the second stays 2. At theta 0.5 both "
            "solvers divide [2, 6] by [2.5, 3]. The second derivative of `2 / (2 + theta)` is "
            "`4 / (2 + theta) ** 3`, which is 0.5 at zero. At theta 1 the solution is "
            "[2 / 3, 2] and multiplying by [3, 3] returns [2, 6]."
        ),
        pitfalls=(
            "Answering with the solution [1, 2] mixes up the solved vector with its "
            "sensitivity. The derivative with respect to the right side is the inverse "
            "diagonal applied to ones, [1 / 2, 1 / 3].",
            "Expecting both coordinates to move when theta changes ignores the structure: "
            "theta only enters the first diagonal entry, so the second coordinate stays "
            "6 / 3 = 2.",
            "Treating agreement with `jnp.linalg.solve` at theta 0.5 as proof that any custom "
            "solver converges overreaches. It shows two implementations agree on one tiny, "
            "exactly solvable system.",
            "Accepting the zero-returning solver because its output is finite skips the only "
            "check that matters. Its residual is the whole right side [2, 6], and its "
            "derivatives would be wrong as well.",
            "Declaring `symmetric=True` for a nonsymmetric operator makes JAX reuse the "
            "forward solver for the transposed system and return wrong gradients silently. "
            "It is valid here only because a diagonal matrix is symmetric.",
            "Dropping the exponent factor when differentiating `-2 / (2 + theta) ** 2` gives "
            "`2 / 8 = 0.25`. The power rule brings down the 2, so the second derivative is "
            "`4 / 8 = 0.5`.",
        ),
        verification=(
            "Run the reference and confirm `jax-023: 8 asserted cases passed`. Evaluate "
            "`2 / (2 + t)` and its two derivatives by hand at t = 0 and t = 1 and compare them "
            "with `implicit_solution`, `jax.grad` and the nested grad. Then print the residual "
            "`diagonal * wrong - right` for the bogus solver and see [-2, -6]."
        ),
    ),
    24: Reasoning(
        approach=(
            "Separate what is known from shapes alone from what needs values. For `X.T @ X` "
            "with X of shape (n, d), the output is (d, d) whatever n is, so `jax.eval_shape` "
            "can answer shape questions without arithmetic. Values need execution, and the "
            "staged jaxpr and compiled executable sit between the two."
        ),
        correctness=(
            "A (7, 2) input gives (2, 2) and a (3, 4) input gives (4, 4). The compiled "
            "executable accepts any (3, 2) float64 input, and doubling X multiplies the Gram "
            "matrix by four. The sum of all Gram entries equals the sum of squared row sums, "
            "here 3, 7 and 11, so each entry's derivative is twice its row sum: 6, 14 and 22. "
            "Zero input gives the zero (2, 2) matrix."
        ),
        pitfalls=(
            "Confusing `X.T @ X` with `X @ X.T` predicts a (7, 7) result for seven rows. The "
            "Gram matrix here compares features, so the row count is summed away.",
            "Expecting `jax.eval_shape` to return numbers misreads it. It returns a "
            "`ShapeDtypeStruct` with shape and dtype, which is why the zero-input task needs a "
            "real call to learn values.",
            "Asserting the exact printed jaxpr, such as a particular `dot_general` line, "
            "ties the test to one JAX version. The reference checks one output variable and "
            "a nonempty equation list.",
            "Predicting that doubling the input doubles the output treats the Gram matrix as "
            "linear. Both factors double, so the result is four times the original.",
            "Answering `2 * X` gives the derivative of the trace of the Gram matrix, the sum "
            "of squares. The task sums every entry, including off-diagonal ones, which "
            "couples the features and gives row-sum copies.",
            "Calling the executable compiled for (3, 2) on a (7, 2) array fails, because "
            "`lower(...).compile()` fixes the signature. Shape inference across sizes "
            "belongs to `eval_shape` or a fresh `jax.jit` call.",
        ),
        verification=(
            "Run the reference and confirm `jax-024: 8 asserted cases passed`. Compute "
            "`gram(values)` and compare it with [[35, 44], [44, 56]] worked out by hand from "
            "the three rows. Then print `jax.make_jaxpr(gram)(values)` to see the transpose "
            "and product, and pass a (7, 2) array to `compiled` to see the signature error."
        ),
    ),
    25: Reasoning(
        approach=(
            "Make each timing measure finished work. `completed_times` validates its count, "
            "calls the function, waits with `block_until_ready`, and records the elapsed time "
            "for each repetition. Before any time is reported, the result's shape and values "
            "are checked, and the workload, backend and summary statistic are named "
            "explicitly."
        ),
        correctness=(
            "Zero repetitions raise ValueError, since an empty sample has no median. The "
            "product of a (16, 16) array with its transpose is (16, 16). Eager and compiled "
            "products agree on values. A median of three finite times lies between their "
            "minimum and maximum. The 8 by 8 product matches NumPy. On this lesson's profile "
            "the default backend and the result's device are both CPU."
        ),
        pitfalls=(
            "Stopping the clock as soon as `function(argument)` returns can measure only "
            "dispatch, because JAX runs asynchronously. Waiting with `block_until_ready` makes "
            "each time include the completed computation.",
            "Passing `repeats=3.0` or `True` might seem harmless, but the guard uses "
            "`type(repeats) is not int`, which rejects both. The count must be a genuine "
            "positive integer.",
            "Comparing eager and compiled times before comparing their values could reward a "
            "faster function that computes something else. The value check comes first.",
            "Reporting the mean of three times lets one slow first call, which can include "
            "tracing and compilation, dominate the summary. The median is the declared "
            "statistic, and it describes only these runs.",
            "Placing the 8 by 8 time next to the 16 by 16 time as one series mixes two "
            "workloads. The smaller shape does less arithmetic and gets its own compiled "
            "specialization.",
            "Quoting these CPU times as evidence about accelerators extrapolates beyond the "
            "measurement. The backend check records where the work ran; it says nothing "
            "about GPU or TPU speed.",
        ),
        verification=(
            "Run the reference and confirm `jax-025: 8 asserted cases passed`. Print the three "
            "times from `completed_times(jax.jit(product), values, 3)` and note whether the "
            "first is larger. Then time the same call without `block_until_ready` in a scratch "
            "copy and compare, keeping both values labeled as local observations."
        ),
    ),
    26: Reasoning(
        approach=(
            "Keep two resource tools apart from the values they produce. `jax.checkpoint` "
            "recomputes intermediates during differentiation instead of storing them, so "
            "every derivative must equal the plain derivative of `sum(x ** 3)`, which is "
            "`3 * x ** 2`. Donation lets a compiled function reuse its input buffer, so the "
            "caller must continue from the returned array."
        ),
        correctness=(
            "At [-2, 0, 2] the slope `3 * x ** 2` gives [12, 0, 12], and at [1, 2, 3] it gives "
            "[3, 12, 27]. Two donated increments take [1, 2] to [3, 4]. A fresh [4, 5] plus one "
            "is [5, 6] by either path. The Hessian is diagonal with entries `6 * x`, so [1, 2] "
            "gives [[6, 0], [0, 12]]. Four float64 entries occupy 32 bytes of array payload."
        ),
        pitfalls=(
            "Reporting -12 at x = -2 keeps the sign of the cube. The derivative squares the "
            "input, so negative and positive points have the same slope 12.",
            "Expecting `jax.checkpoint` to change the gradient misreads it as an "
            "approximation. It only trades stored intermediates for recomputation, so values "
            "match the unwrapped function exactly.",
            "Calling `consume` on the original array after donating it breaks the ownership "
            "contract. Where the backend honors donation that buffer is invalidated, so the "
            "next call must use the returned state.",
            "Building the baseline from the same array that was donated could read consumed "
            "storage. The reference creates two independent [4, 5] arrays for the two paths.",
            "Expecting off-diagonal Hessian entries assumes the coordinates interact. The sum "
            "of cubes is separable, so every mixed second derivative is zero.",
            "Treating `result.nbytes`, 32, as the memory the update used ignores allocator "
            "pools, compiled program storage and intermediates. It is the logical size of the "
            "returned array only, not peak memory.",
        ),
        verification=(
            "With `jax-026: 8 asserted cases passed` on screen, set "
            "`jax.grad(rematerialized)` beside `jax.grad(cubic_sum)` on the same inputs to see "
            "identical values. Then print `jax.make_jaxpr(jax.grad(rematerialized))(x)` and "
            "look for an equation named `checkpoint` or `remat`, which records the recomputation."
        ),
    ),
    27: Reasoning(
        approach=(
            "Keep three things separate: the device inventory, the layout specification and "
            "the values. The mesh is built from exactly one CPU device under the name `data`. "
            "`PartitionSpec('data', None)` says rows would be split along that axis, and the "
            "empty spec says the array is replicated. With one device both layouts store the "
            "same full table, so every task checks values or metadata, never speedup."
        ),
        correctness=(
            "The mesh has one CPU device on its `data` axis. Placing the (3, 2) table and "
            "reading it back returns the same six values, because the array is fully "
            "addressable. The two specs compare equal to the specs they were built from. The "
            "gradient of a sum of squares is `2 * x`. A (5, 2) table keeps its global shape and "
            "its single shard holds all five rows."
        ),
        pitfalls=(
            "Reading the axis name `data` as evidence of data parallelism assumes devices "
            "that were never supplied. The mesh shape reports one device, and that is the "
            "whole inventory.",
            "Assuming `np.asarray` always works on a sharded array ignores addressability. In "
            "a multi-process setting a process may hold only some shards; here the check "
            "`is_fully_addressable` justifies the conversion.",
            "Concluding that the row layout and the replicated layout are the same because "
            "their storage matches on one device erases intent. Their specs differ and would "
            "place data differently on a larger mesh.",
            "Expecting device placement to change the derivative treats layout as part of the "
            "mathematics. The gradient of the sum of squares is still `2 * host`, whatever "
            "sharding the input carries.",
            "Testing the layout only on the original three rows could hide a helper that "
            "hard-codes the observation count. The (5, 2) table shows the spec names axis "
            "meaning, not a fixed size.",
            "Reporting that the sharded computation scaled across devices claims hardware "
            "that did not run. `len(placed.devices())` is 1, so the lesson makes no scaling "
            "claim at all.",
        ),
        verification=(
            "Run the reference and confirm `jax-027: 8 asserted cases passed`. Print "
            "`jax.devices()` to see the single CPU device, then print `placed.sharding` and "
            "`placed.addressable_shards[0].index` to confirm that the one shard covers every "
            "row. Comparing `replicated.spec` with `row_layout.spec` shows the only "
            "difference is the declared axis."
        ),
    ),
    28: Reasoning(
        approach=(
            "Combine sums and counts, never local means. Each participant contributes its "
            "local sum and its local count, `psum` adds both across the named `replica` axis, "
            "and one division produces the global mean on every participant. `jax.vmap` with "
            "`axis_name` simulates the participants on one CPU so the arithmetic can be "
            "checked exactly."
        ),
        correctness=(
            "Sums [2, 12] over counts [1, 3] give 14 / 4 = 3.5 on both participants. Sums "
            "[2, 6] over counts [2, 2] give 8 / 4 = 2, the same as the mean of local means "
            "because the counts are equal. Adding a participant with sum 0 and count 0 leaves "
            "14 / 4. `all_gather` of [2, 5] gives each participant [2, 5], while `psum` of "
            "[2, 5, 7] gives each one 14."
        ),
        pitfalls=(
            "Validating with the equal-count fixture alone accepts the mean of local means, "
            "since 1 and 3 averaged equals 2 there. Unequal counts are the case that "
            "exposes the wrong weighting.",
            "Having each participant divide first, `local_sum / local_count`, makes the empty "
            "participant compute 0 / 0 and inject NaN into the reduction. Summing before "
            "dividing keeps the denominator 4.",
            "Expecting `all_gather` to return 7 confuses it with `psum`. Gather keeps one "
            "entry per participant, so the output gains a participant axis of length two.",
            "Adding up the three replicated `psum` outputs reports 42, counting the global "
            "total three times. Each participant already holds the full sum 14.",
            "Treating the compiled run as evidence of a multi-device collective overstates "
            "it. `jax.jit(mapped_mean)` checks compilation parity on one CPU and says nothing "
            "about network communication.",
            "Averaging the local gradient means -4 and about -38.67 gives about -21.33, not "
            "the true -120 / 4 = -30. The participant with three observations deserves three "
            "times the weight.",
        ),
        verification=(
            "Run the reference and confirm `jax-028: 8 asserted cases passed`. Compute "
            "`local_sums.sum() / local_counts.sum()` with ordinary array operations and "
            "compare it with `mapped_mean`. Then compute `(local_sums / local_counts).mean()` "
            "and see (2 + 4) / 2 = 3 instead of 3.5, the same weighting error on the value side."
        ),
    ),
    29: Reasoning(
        approach=(
            "Port each formula term by term. Attention scores are `q k^T / sqrt(d)`, masked "
            "entries become negative infinity, a row-wise softmax gives weights, and the "
            "weights average the value rows. With zero queries and keys every allowed score "
            "is zero, so each query takes a plain average of the value rows it may see. The "
            "adapter is `I + 2 * A @ B` with A of shape (8, 2) and B of shape (2, 8)."
        ),
        correctness=(
            "Under the causal mask, query 0 sees row 0, query 1 rows 0 and 1, and query 2 all "
            "three, so changing row 2 cannot reach the first two outputs. Summing outputs "
            "gives row 0 weight 1 + 1/2 + 1/3 = 11/6, row 1 weight 5/6 and row 2 weight 1/3. "
            "Scores [1 / sqrt(2), 0] give probability `sigmoid(1 / sqrt(2))` near 0.67. The "
            "adapter has 16 + 16 = 32 entries and rank at most two."
        ),
        pitfalls=(
            "Checking only that the mask is lower triangular does not prove the output path "
            "respects it. Changing the future value row to [100, 200] tests the complete "
            "computation directly.",
            "Dropping the `sqrt(d)` scale gives `sigmoid(1)` near 0.73 instead of about 0.67. "
            "The zero-score fixture cannot catch this, because zero divided by any scale is "
            "still zero.",
            "Masking with a large negative number such as -1e9 instead of rejecting a query "
            "with no allowed key hides the problem. With all entries equal, softmax spreads "
            "weight over forbidden keys; with -inf everywhere it returns NaN.",
            "Expecting every value row to get gradient one per feature assumes each query "
            "uses every key. Row 0 is visible to all three queries and row 2 only to the "
            "last, so the weights differ.",
            "Reading the rank bound as a statement that A @ B has at most two nonzero "
            "entries confuses rank with sparsity. At the given values B is zero, so the "
            "product is zero; trained factors can fill all 64 entries.",
            "Calling `admit_attention` inside `jax.jit` fails, since `np.asarray(allowed)` "
            "needs a concrete array. Only the pure `attention` helper is compiled, after "
            "validation on the host.",
        ),
        verification=(
            "Run the reference and confirm `jax-029: 8 asserted cases passed`. Print "
            "`attention(q, k, v, mask)` and check rows [2, 0], [1, 1] and [8/3, 8/3] against "
            "the causal averages. Then remove the square-root division in a scratch copy and "
            "watch only the nonuniform scale task fail."
        ),
    ),
    30: Reasoning(
        approach=(
            "Assemble the component from pieces with distinct jobs. `admit` checks contracts "
            "on the host: matching row counts, a nonempty Boolean mask, a finite nonnegative "
            "penalty and finite data. `objective` states the penalized masked mean squared "
            "error. `solve` builds the normal equations of that same objective, so its answer "
            "must make the objective's gradient zero."
        ),
        correctness=(
            "Setting the gradient of `mean((Xw - y) ** 2) + lambda * w . w` to zero gives "
            "`(X'X / n + lambda I) w = X'y / n`, which is what `solve` builds. Targets "
            "[1, 3, 5] follow 1 + 2x, so penalty zero returns [1, 2] in any row order; penalty "
            "0.1 shrinks it. Targets [2, 5, 8] follow 2 + 3x and give [2, 3]."
        ),
        pitfalls=(
            "Penalizing only the slope, as many regression libraries do, gives a different "
            "weight. Its objective gradient would not be zero here, because this contract "
            "penalizes both coefficients.",
            "Reversing the design rows but not the targets pairs each row with another "
            "target and changes the fitted line. Permutation invariance holds only when rows, "
            "targets and mask move together.",
            "Letting an all-false mask reach `solve` divides by a zero count and returns "
            "non-finite values rather than an error. `admit` rejects the empty population "
            "first.",
            "Relying on the solve to fail for a negative penalty does not work here: with "
            "-0.1 the matrix stays invertible because the smallest eigenvalue of `X'X / 3` is "
            "about 0.28. The contract rule must reject it.",
            "Moving `admit` inside the compiled function breaks it, because `np.asarray` "
            "cannot read a tracer. Validation stays on the host and only `solve` is passed "
            "to `jax.jit`.",
            "Returning [1, 2] from a helper that memorized the first fixture would pass the "
            "first few checks. The new targets [2, 5, 8] demand [2, 3] and expose a "
            "hard-coded answer.",
        ),
        verification=(
            "Run the reference and confirm `jax-030: 8 asserted cases passed`. Print "
            "`solve(design, targets, mask, .1)` and confirm both coefficients move from "
            "[1, 2]. Then evaluate `objective` at that weight and at small perturbations of it "
            "to see the minimum, and confirm `jax.grad(objective)` is zero there."
        ),
    ),
    31: Reasoning(
        approach=(
            "Build the comparison in layers that can each be checked alone. `features` maps an "
            "input to [1, x, x squared], `targets` is the known rule 1 + 2x - 0.5x squared, "
            "and `loss` is the mean squared residual. `advance` runs plain gradient descent "
            "with step 0.02 inside `jax.lax.scan`, so a fixed number of steps is one compiled "
            "loop whose only carried state is the coefficient vector."
        ),
        correctness=(
            "The gradient of the mean squared residual is `2 X'(Xw - y) / n`, which the first "
            "task writes out by hand. Targets are exactly quadratic in x, so least squares on "
            "the five training rows recovers [1, 2, -0.5]. Each update reads only `state` and "
            "fixed data, which makes 200 plus 200 steps equal 400. At x = 3 the rule gives "
            "1 + 6 - 4.5 = 2.5."
        ),
        pitfalls=(
            "Comparing the trained weights with [1, 2, -0.5] and calling a mismatch a bug "
            "overlooks the budget. Four hundred steps at rate 0.02 need not converge, so "
            "the exact optimum comes from `lstsq` instead.",
            "Dividing the explicit gradient by nothing, or forgetting its factor of two, "
            "gives a vector proportional to the autodiff result but not equal. The first "
            "task fails for either slip.",
            "Carrying a step counter or learning-rate schedule in the loop and dropping it "
            "on resume would break the 200 plus 200 replay. Here the transition is fixed, so "
            "coefficients alone suffice.",
            "Shuffling the training rows each step with a fresh random key would make a "
            "replay disagree unless the key is saved. This study has no random order, which "
            "is why the second run matches.",
            "Treating the held-out points at -1.5, -0.5, 0.5 and 1.5 as extrapolation "
            "misreads the split. They sit between training inputs; x = 3 lies outside the "
            "training range of -2 to 2.",
            "Claiming that a learned model will extrapolate to 2.5 at x = 3 borrows a "
            "guarantee from the synthetic oracle. Only the known rule gives that value; a "
            "real fit would need evidence beyond its support.",
        ),
        verification=(
            "Run the reference and confirm `jax-031: 8 asserted cases passed`. Print the "
            "second output of `advance(jnp.zeros(3), 400)` to see the loss trajectory fall, "
            "and print `trained` next to `optimum` to see how close the budget came. "
            "Evaluating `loss(trained, heldout_design, heldout_y)` gives the held-out error "
            "for the report."
        ),
    ),
    32: Reasoning(
        approach=(
            "Sort each observation into the evidence layer it actually reaches: CPU numerical "
            "behavior, accelerator compilation, device execution with readback, memory "
            "accounting, precision, and device health. For every scenario, name what the "
            "observation supports, name the next observation still missing, and refuse to "
            "promote a lower layer into a claim about a higher one."
        ),
        correctness=(
            "A CPU pass shows the mathematics, not the accelerator toolchain. A lowered program "
            "shows compilation, while execution needs synchronized output checked against an "
            "independent value. Reserved memory includes allocator pools, so it can exceed "
            "`nbytes` without a leak. A GPU probe says nothing about a TPU, and a reaped child "
            "process does not prove the device recovered."
        ),
        pitfalls=(
            "Marking the GPU lesson qualified because every CPU assertion passed skips the "
            "accelerator package, driver and device stages entirely. The CPU record is a "
            "baseline, not a substitute.",
            "Reporting a successful lowering as a working GPU path omits execution. A "
            "program can compile and still fail or return wrong values when it actually runs "
            "on the device.",
            "Calling reserved memory far above array `nbytes` a leak ignores preallocation "
            "by the allocator and temporary buffers. A leak claim needs repeated controlled "
            "measurements that keep growing.",
            "Timing float32 against float64 before checking their errors mixes two outcomes. "
            "A faster precision that loses the answer on an ill-conditioned input has not "
            "won the comparison.",
            "Extending a GPU success to TPU because both are accelerators reuses evidence "
            "across backends. TPU needs its own environment, allocation, computation and "
            "readback observations.",
            "Starting a new device job automatically after reaping an interrupted one "
            "assumes the hardware is healthy. Process cleanup and device recovery are "
            "separate facts for the resource owner.",
        ),
        verification=(
            "Write a one-line ledger for each of the six scenarios with three columns: "
            "observation, supported claim, and next missing observation. Check that no row's "
            "claim mentions a layer its observation did not reach, and that the device health "
            "row ends with an explicit owner decision rather than an automatic retry."
        ),
    ),
    33: Reasoning(
        approach=(
            "Treat a multi-host program as a lifecycle with fixed order: initialize the "
            "distributed runtime, check the participant and device inventory, then build "
            "global arrays under that topology. At every later step, distinguish what one "
            "process can see from what the whole job holds, and keep correctness, failure "
            "handling and performance as separate questions."
        ),
        correctness=(
            "Initialization must come first because device queries before it describe only "
            "the local process. A process holding two of four shards can vouch for those two "
            "alone. Overlapping record loads count some samples twice, which changes the "
            "global loss even when every collective is correct. A named-axis CPU model checks "
            "reduction arithmetic, not network traffic or throughput."
        ),
        pitfalls=(
            "Calling `jax.devices()` before distributed initialization and trusting its count "
            "builds arrays for a one-process view. The later global layout then disagrees "
            "with the intended topology.",
            "Checking the two locally addressable shards and declaring the global array "
            "valid generalizes from a partial view. The unseen shards need an explicit global "
            "validation step.",
            "Blaming the collective when the global loss looks wrong can miss duplicated "
            "data. If two processes read overlapping records, `psum` faithfully sums the "
            "duplicated contributions.",
            "Testing participant failure by killing a process and waiting for the collective "
            "to finish can hang forever. The experiment needs a timeout or cancellation "
            "bound and planned cleanup.",
            "Presenting the `vmap` model with `axis_name` as a multi-host demonstration "
            "inflates its scope. It runs on one CPU and proves only the reduction formula.",
            "Comparing one host at batch 64 with two hosts at batch 128 measures two "
            "different training problems. A fair scaling study fixes the effective data and "
            "reduction before timing.",
        ),
        verification=(
            "For each scenario, state the observation you would retain and the claim it can "
            "support. Then cross-check the plans against each other: the initialization order "
            "must precede the shard inspection, the sample-ID audit must precede any loss "
            "interpretation, and the scaling study must cite the CPU model only as a "
            "numerical oracle."
        ),
    ),
    34: Reasoning(
        approach=(
            "Treat a custom kernel or FFI call as a new component that must earn its place. "
            "Start from a measured limitation of a correct high-level baseline, define the "
            "accepted layouts and transformations explicitly, validate values and derivatives "
            "against an independent oracle, and only then benchmark completed work on named "
            "hardware. The closing review defends one concrete claim per evidence layer."
        ),
        correctness=(
            "A lower-level API is not itself a benefit, so the justification must name a "
            "bottleneck. A shape does not fix strides, so layout needs a stated policy. A VJP "
            "rule does not supply JVP, `vmap` or higher derivatives. Timing that omits "
            "synchronization or transfers measures dispatch. Without a GPU, derivation and a "
            "CPU reference remain honest progress."
        ),
        pitfalls=(
            "Writing a kernel because the high-level version feels slow, without a profile, "
            "adds maintenance with no demonstrated gain. The baseline and its bottleneck "
            "must be measured first.",
            "Indexing a transposed input as if it were contiguous reads the wrong elements "
            "or invalid memory. A noncontiguous counterexample exposes the assumption before "
            "users meet it.",
            "Assuming `vmap` works because `jax.grad` does confuses two transformation rules. "
            "Each advertised transformation needs its own implementation and test, or an "
            "explicit refusal.",
            "Timing the fused operator without `block_until_ready` while timing the baseline "
            "after readback compares dispatch with completed work. The comparison then "
            "favors whichever side skipped synchronization.",
            "Writing a passed GPU check into the record when no GPU was available fabricates "
            "evidence. Compilation, runtime, device correctness and profiling stay marked as "
            "pending.",
            "Defending the final component with the number of lessons completed answers the "
            "wrong question. A reviewer needs a claim, the observation behind it and a test "
            "that could refute it.",
        ),
        verification=(
            "Check the review against its own evidence: every stated benefit cites a "
            "measurement, every supported layout and transformation has a test, and every "
            "pending GPU item is labeled pending. Then pose one unfamiliar input, such as a "
            "transposed operand, and confirm the plan predicts whether it is handled or "
            "refused."
        ),
    ),
}
