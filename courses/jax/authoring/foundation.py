"""First-contact array, state and random-key investigations."""

from model import Unit, case

UNITS = [
    Unit(
        1,
        "From a Python function to a numerical contract",
        "beginner",
        (),
        ("function", "prediction unit", "shape", "independent oracle"),
        "Specify a small computation and distinguish its numerical result from a model-quality claim.",
        r"""A numerical program starts with a question about values. JAX adds transformations to Python functions, but those transformations cannot choose the intended question. Begin with a linear predictor: one input number represents one observation, one parameter multiplies it, and the output is one prediction for that observation. A function takes named inputs and returns a result. Returning a new value is different from changing an object that another part of the program owns.

Suppose the observed inputs are 1, 2 and 3 and the targets are twice those values. At weight zero every prediction is zero. We can calculate the errors without a library: -2, -4 and -6. Squaring produces 4, 16 and 36. Their mean is 56/3. This number describes an explicitly chosen error summary on three authored observations. It does not estimate performance on unseen data by itself.

Arrays organize these observations. Shape (3,) means a vector with three entries. Shape (3,1) means three rows and one column. These representations can interact differently with a target vector even when printing makes them appear similar. A shape assertion is therefore part of the mathematical specification. Later JAX transformations preserve the computation we write, including an unintended broadcast if it is otherwise legal.

The classroom runs a complete source submission in a fresh process. An import makes a library available; a function definition creates a callable object; calling the function performs the described computation. An assertion asks whether the observed value satisfies a contract. A successful assertion is evidence for that case. Keep the source, predicted result and actual receipt together, and change one meaningful assumption at a time when investigating a failure.

This first unit intentionally uses tiny data and no fitted neural network. The purpose is to learn the evidence discipline that makes a larger calculation interpretable: identify the input unit, state the operation, calculate an independent expected answer, and explain which claim remains outside the experiment.""",
        r"""For inputs \(x_i\), targets \(y_i\) and scalar weight \(w\), define \(\widehat y_i=wx_i\) and \(L(w)=N^{-1}\sum_i(\widehat y_i-y_i)^2\). The denominator counts observations because each observation has one output here. With several output coordinates, a mean over every array entry would answer a different weighting question. At \(w=0\), the three residual squares sum to 56 and the loss is \(56/3\). At \(w=2\), every residual is zero. Neither calculation uses a gradient or updates a parameter.""",
        """def predict(weight, inputs):
    return weight * inputs


def mse(weight, inputs, targets):
    if inputs.ndim != 1 or inputs.shape != targets.shape or inputs.size == 0:
        raise ValueError("one nonempty target per input")
    return jnp.mean((predict(weight, inputs) - targets) ** 2)

x = jnp.array([1., 2., 3.])
y = 2 * x""",
        (
            case(
                "A hand-calculated loss",
                "Evaluate the zero-weight predictor on the three observations.",
                "Loss 56/3, predictions [0,0,0].",
                "The assertion compares JAX with a calculation made from the three squared residuals. It checks the mean denominator as well as the prediction rule.",
                "close(predict(0., x), [0., 0., 0.])\nclose(mse(0., x, y), 56 / 3)",
                "Write the three errors before squaring.",
            ),
            case(
                "A plausible shape mistake",
                "Replace the target vector with a column and apply the contract before subtraction.",
                "ValueError rather than an unintended 3-by-3 error matrix.",
                "Broadcasting can be legal while the pairing is wrong. The guard rejects this representation before JAX has a chance to compute a misleading mean.",
                "try:\n    mse(0., x, y[:, None])\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('shape mismatch accepted')",
                "Compare both ndim and the full shape tuple.",
            ),
        ),
        (
            case(
                "Trace another predictor",
                "Calculate predictions at weight 1, then their mean squared error.",
                "[1,2,3] and 14/3.",
                "Each error equals minus the corresponding input; square and average.",
                "close(predict(1., x), [1., 2., 3.])\nclose(mse(1., x, y), 14 / 3)",
                "A prediction is not the same array as an error.",
            ),
            case(
                "Construct an exact fit",
                "Find a weight that matches every supplied target and verify it.",
                "Weight 2 gives zero loss.",
                "All targets follow the same declared rule, so this is an algebraic fit to the fixture.",
                "close(mse(2., x, y), 0.)",
                "Inspect target/input ratios.",
            ),
            case(
                "Change the target",
                "Use targets [2,4,7] while keeping weight 2.",
                "Loss 1/3.",
                "Only the final target differs by one; the denominator remains three.",
                "close(mse(2., x, jnp.array([2., 4., 7.])), 1 / 3)",
                "Identify which residual is nonzero.",
            ),
            case(
                "Reject missing observations",
                "Define the behavior for two empty vectors.",
                "ValueError, not a NaN mean.",
                "An empty mean does not describe a prediction experiment under this contract.",
                "try:\n    mse(0., jnp.array([]), jnp.array([]))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('empty loss accepted')",
                "Check size before reduction.",
            ),
            case(
                "Separate sum from mean",
                "Calculate the zero-weight sum of squared errors and compare it with three times the mean.",
                "Both are 56.",
                "The equality relies on exactly three equally weighted output entries.",
                "close(jnp.sum((0. * x - y) ** 2), 56.)\nclose(3 * mse(0., x, y), 56.)",
                "Retain the count with the accumulated sum.",
            ),
            case(
                "Transfer to new inputs",
                "Evaluate weight 2 on inputs [4,5], then explain what a zero fixture error establishes.",
                "Predictions [8,10]; no population-quality claim.",
                "The same algebra transfers to new literal inputs. These two authored numbers are not an independent real-world evaluation dataset.",
                "close(predict(2., jnp.array([4., 5.])), [8., 10.])",
                "Separate the software rule from a data-generating assumption.",
            ),
        ),
        "If a loss differs, inspect shapes and the denominator before changing tolerance. If a variable is undefined, reconstruct the complete program rather than assuming state survived an earlier Run. A successful import is not a passed numerical check.",
        "Revisit python-05, python-16 and python-numpy-02 if function arguments or shapes are unfamiliar. Explain this fixture to another learner without using the word model as a substitute for the actual multiplication and reduction.",
        (("How to think in JAX", "https://docs.jax.dev/en/latest/notebooks/thinking_in_jax.html"),),
    ),
    Unit(
        2,
        "Array axes, broadcasting and functional updates",
        "beginner",
        (1,),
        ("axis", "broadcasting", "functional update", "index contract"),
        "Control the shape and meaning of every reduction and update in a small array calculation.",
        r"""An axis has both a length and a meaning. In a two-row table of three features, axis zero identifies observations and axis one identifies features. A sum over axis one returns one total per observation. A sum over axis zero returns one total per feature. Both operations are valid, so neither a successful call nor a finite result tells you which question was intended.

Broadcasting aligns trailing dimensions. A vector of three feature offsets can be added to a (2,3) table. A vector of two observation offsets needs an explicit column axis to express a separate offset for each row. Adding the wrong shape may fail loudly; adding a coincidentally compatible shape can silently express a different computation. Deliberately use unequal axis lengths when testing an axis contract.

JAX arrays present immutable values to ordinary Python code. A functional update such as x.at[index].set(value) returns an updated array; it does not make assigning into the old array a supported operation. The compiler may optimize storage internally, but the programming contract remains that the old value is unchanged. Later buffer-donation lessons discuss a separate explicit permission to reuse storage.

Index behavior also deserves a declared contract. Do not infer that an out-of-range gather or scatter must behave like a Python list or NumPy array. For this lesson, a small host-side validator accepts only integer indices within a fixed known array length before calling the numerical helper. This validator is intentionally outside JIT. A later transformed computation needs a compatible validation or masking policy instead of applying Python decisions to traced values.""",
        r"""For \(X\in\mathbb R^{2\times3}\), row sums satisfy \(r_i=\sum_{j=0}^{2}X_{ij}\) and column sums satisfy \(c_j=\sum_{i=0}^{1}X_{ij}\). Row centering is \(X_{ij}-\frac13\sum_kX_{ik}\). Keeping the reduced axis as a singleton makes the subtraction's intended broadcast visible. The centered row sums should be zero, which is a stronger oracle than checking only the output shape.""",
        """table = jnp.arange(6., dtype=jnp.float64).reshape(2, 3)


def replace_at(values, index, value):
    if type(index) is not int or not 0 <= index < values.shape[0]:
        raise ValueError("index outside the vector")
    return values.at[index].set(value)""",
        (
            case(
                "Two valid reductions",
                "Calculate row and column totals of [[0,1,2],[3,4,5]].",
                "Rows [3,12]; columns [3,5,7].",
                "Different result lengths reveal the reduced axis. Labeling both results merely a sum hides the statistical unit.",
                "close(table.sum(axis=1), [3., 12.])\nclose(table.sum(axis=0), [3., 5., 7.])",
                "Draw which entries belong in one sum.",
            ),
            case(
                "Return a changed value",
                "Replace index one of [10,20,30] with 99 and inspect both arrays.",
                "New [10,99,30]; original [10,20,30].",
                "The update is a function from old value and instruction to new value. Retaining both arrays makes the ownership contract observable.",
                "old = jnp.array([10., 20., 30.])\nnew = replace_at(old, 1, 99.)\nclose(new, [10., 99., 30.])\nclose(old, [10., 20., 30.])",
                "Bind the returned array to a different name.",
            ),
        ),
        (
            case(
                "Center each observation",
                "Subtract each row's mean while preserving a singleton feature axis.",
                "Both rows [-1,0,1]; row sums zero.",
                "keepdims retains shape (2,1), so each row receives its own mean.",
                "centered = table - table.mean(axis=1, keepdims=True)\nclose(centered, [[-1., 0., 1.], [-1., 0., 1.]])\nclose(centered.sum(axis=1), [0., 0.])",
                "Write the mean array's shape first.",
            ),
            case(
                "Broadcast feature offsets",
                "Add [10,20,30] to each observation.",
                "[[10,21,32],[13,24,35]].",
                "The three offsets align with the final dimension.",
                "close(table + jnp.array([10., 20., 30.]), [[10., 21., 32.], [13., 24., 35.]])",
                "The offset vector identifies columns.",
            ),
            case(
                "Broadcast observation offsets",
                "Add 10 to row zero and 20 to row one.",
                "[[10,11,12],[23,24,25]].",
                "A (2,1) array repeats each offset across that row's features.",
                "close(table + jnp.array([10., 20.])[:, None], [[10., 11., 12.], [23., 24., 25.]])",
                "Insert the singleton feature dimension.",
            ),
            case(
                "Accumulate an update",
                "Add five at index zero using .at and retain the original vector.",
                "New [6,2], original [1,2].",
                "add expresses an increment, whereas set replaces the old value.",
                "old = jnp.array([1., 2.])\nclose(old.at[0].add(5.), [6., 2.])\nclose(old, [1., 2.])",
                "Choose the update operation from its meaning.",
            ),
            case(
                "Enforce the index boundary",
                "Try replacing index three in a three-element vector.",
                "ValueError from the declared host-side guard.",
                "The lesson refuses this request explicitly rather than relying on backend-specific bounds behavior.",
                "try:\n    replace_at(jnp.zeros(3), 3, 1.)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('bad index accepted')",
                "The largest valid index is length minus one.",
            ),
            case(
                "Transfer the axis rule",
                "Row-center a 3-by-2 table and assert each row sum, without hard-coding row count.",
                "Shape (3,2), all row sums zero.",
                "Changing both axis lengths catches implementations that accidentally relied on a square or fixed-size example.",
                "other = jnp.arange(6.).reshape(3, 2)\ncentered = other - other.mean(axis=1, keepdims=True)\nassert centered.shape == (3, 2)\nclose(centered.sum(axis=1), jnp.zeros(3))",
                "Express the operation using axis meaning, not a literal shape.",
            ),
        ),
        "A shape-correct result may still reduce the wrong population. Check a row-specific invariant and use nonsquare fixtures. Keep index admission outside transformed numerical code until the tracing rules have been taught.",
        "Compare this value-oriented update with NumPy mutation in python-numpy-01. Explain why an implementation's possible in-place optimization does not make arbitrary Python mutation part of JAX's public array contract.",
        (("JAX NumPy", "https://docs.jax.dev/en/latest/jax.numpy.html"),),
    ),
]

UNITS.extend(
    [
        Unit(
            3,
            "Dtypes, precision and numerical error contracts",
            "beginner",
            (2,),
            ("dtype", "rounding", "X64", "absolute and relative error"),
            "Choose a precision policy and distinguish floating-point error from a wrong mathematical operation.",
            r"""A dtype determines which numbers an array can represent, not only how many bytes it occupies. Floating-point numbers use finite precision. Near a large value, neighboring representable numbers can be farther apart than one. Adding one may then round back to the original value. More printed decimal digits cannot recover information that was never represented.

JAX normally disables 64-bit array creation by default. This course's executable header deliberately enables X64 before creating arrays, so the small scientific oracles can use float64. The precision lesson still constructs float32 explicitly to expose the difference. Inspect the actual dtype instead of assuming that a requested dtype or a Python decimal literal established the desired precision.

An error tolerance should reflect the operation and the scale of its inputs. Absolute tolerance permits a fixed distance from the expected result. Relative tolerance permits an error proportional to the expected magnitude. Near zero, an absolute term matters because relative error alone is unstable or undefined. Exact integer counts, shapes and Boolean decisions should not be weakened into approximate checks.

A stable formula avoids unnecessary loss of information. Logarithms of sums of exponentials appear in probabilistic objectives. Directly exponentiating a score of one thousand can overflow, even though the final logarithm is approximately one thousand and perfectly representable. A stable log-sum-exp formulation computes the same mathematical quantity through a different intermediate representation. It does not repair bad inputs, wrong axes or a scientifically inappropriate objective.

Precision is also a resource and hardware choice. A CPU demonstration of float64 arithmetic does not establish float64 throughput on a GPU. Later units will separate numerical acceptance from performance measurement. Here the goal is to explain why two correct finite-precision implementations may differ and when that disagreement is instead evidence of a programming defect.""",
            r"""Machine epsilon is the gap from 1 to the next larger representable value. For binary float32 it is \(2^{-23}\); for float64 it is \(2^{-52}\). A typical comparison accepts \(|a-b|\le\mathrm{atol}+\mathrm{rtol}|b|\). This is a chosen error contract, not a theorem about every algorithm. For log-sum-exp, subtracting \(m=\max_i z_i\) gives \(m+\log\sum_i e^{z_i-m}\); all exponentials are at most one.""",
            """def add_then_subtract(big, increment):
    intermediate = big + increment
    return intermediate - big""",
            (
                case(
                    "An increment disappears",
                    "Add one to 1e8 and subtract 1e8 using explicit float32, then float64.",
                    "Float32 gives 0; float64 gives 1.",
                    "The float32 addition rounds before the later subtraction. The mathematical identity did not fail; the intermediate representation changed.",
                    "close(add_then_subtract(jnp.float32(1e8), jnp.float32(1.)), 0.)\nclose(add_then_subtract(jnp.float64(1e8), jnp.float64(1.)), 1.)",
                    "Inspect the intermediate dtype and spacing.",
                ),
                case(
                    "A finite stable objective",
                    "Evaluate log(exp(0)+exp(1000)) without constructing the huge exponential.",
                    "A finite value equal to 1000 within tolerance.",
                    "logaddexp forms the stable scalar log-sum. Avoid using an overflowing calculation as the reference for the stable one.",
                    "value = jnp.logaddexp(jnp.float64(0.), jnp.float64(1000.))\nassert bool(jnp.isfinite(value))\nclose(value, 1000.)",
                    "Factor out the larger exponential symbolically.",
                ),
            ),
            (
                case(
                    "Inspect precision",
                    "Construct float32 and float64 arrays and assert their actual dtypes.",
                    "The requested two distinct dtypes are retained under the declared X64 policy.",
                    "The header establishes policy before arrays exist; explicit dtype assertions make that assumption visible.",
                    "assert jnp.array([1.], dtype=jnp.float32).dtype == jnp.float32\nassert jnp.array([1.], dtype=jnp.float64).dtype == jnp.float64",
                    "Check metadata, not printed formatting.",
                ),
                case(
                    "Calculate epsilon",
                    "Compare each floating dtype's epsilon with its exact binary expression.",
                    "2^-23 and 2^-52.",
                    "Epsilon describes spacing near one, not constant spacing over the whole number line.",
                    "assert float(jnp.finfo(jnp.float32).eps) == 2. ** -23\nassert float(jnp.finfo(jnp.float64).eps) == 2. ** -52",
                    "Separate significand width from exponent range.",
                ),
                case(
                    "Use an absolute bound",
                    "Check a 1e-12 discrepancy from zero with atol 2e-12 and rtol zero.",
                    "The explicit absolute-error check passes.",
                    "Near zero, the relative term contributes no useful allowance.",
                    "close(jnp.float64(1e-12), 0., atol=2e-12, rtol=0.)",
                    "Write the acceptance inequality.",
                ),
                case(
                    "Keep counts exact",
                    "Add integer counts [2,3,5] and verify shape and exact total.",
                    "Scalar integer total 10.",
                    "There is no statistical or floating approximation in this bounded integer count.",
                    "counts = jnp.array([2, 3, 5], dtype=jnp.int32)\nassert counts.sum().shape == ()\nassert int(counts.sum()) == 10",
                    "Do not use a tolerance to excuse an off-by-one count.",
                ),
                case(
                    "Shift scores safely",
                    "Compare log-sum-exp for [0,log(3)] and the same scores shifted by 1000.",
                    "The values differ by exactly 1000 within tolerance.",
                    "Adding a common offset changes log-normalization by that offset, while normalized probabilities would remain unchanged.",
                    "scores = jnp.array([0., math.log(3.)])\na = jax.scipy.special.logsumexp(scores)\nb = jax.scipy.special.logsumexp(scores + 1000.)\nclose(a, math.log(4.))\nclose(b - a, 1000.)",
                    "Distinguish the log-normalizer from softmax probabilities.",
                ),
                case(
                    "Recognize invalid data",
                    "Inspect a NaN and an infinity before applying an approximate comparison.",
                    "Both fail the finite-value predicate.",
                    "Tolerance is meaningful only after the declared numeric domain is satisfied.",
                    "assert not bool(jnp.isfinite(jnp.array([jnp.nan, jnp.inf])).all())",
                    "Validate the domain before estimating numerical error.",
                ),
            ),
            "When a check fails, inspect dtype, value scale, conditioning and intermediate overflow before widening tolerance. A float32-versus-float64 difference is not by itself an implementation defect. A wrong reduction or integer count remains wrong in either precision.",
            "Connect this example to the numerical-accuracy discussion in the statistics and CUDA paths. Describe one computation where a stable formulation matters more than simply requesting another dtype, and state what hardware measurement would be needed for a performance conclusion.",
            (
                (
                    "Default dtypes and X64",
                    "https://docs.jax.dev/en/latest/101/default_dtypes.html",
                ),
                ("Numerical accuracy", "https://docs.jax.dev/en/latest/accuracy.html"),
            ),
        ),
        Unit(
            4,
            "Pure functions and explicit state transitions",
            "beginner",
            (3,),
            ("purity", "state", "transition", "replay"),
            "Represent a changing computation as inputs and returned state that can be replayed and inspected.",
            r"""A stateful task need not hide its state. A running average changes as observations arrive, but we can represent that change with a pure function. Give the function the current sum and count plus one observation. Return a new sum and count. The output depends on those inputs, and the caller decides whether to retain the new state.

This separation matters for JAX transformations. Tracing observes numerical operations and static Python structure. Mutating a global list or a Python object's field is not an ordinary numerical state transition that a transformation can reliably replay for every execution. We will investigate that failure under JIT later. First, learn to make the state visible without using any transformation.

The representation should contain what the next step needs. A mean alone is insufficient to combine groups of unequal size. The pair (sum,count) is enough to calculate the mean and to merge another such pair. The same principle later determines a training checkpoint: parameters alone may reproduce today's predictions while failing to reproduce tomorrow's optimizer update.

Immutability does not mean that nothing changes. It means a change is represented by a new value with an explicit relationship to the old one. Keeping both values enables a useful test: apply the same transition twice to the same old state and verify equal results. Applying the transition to its own returned state is a different experiment because the input state has changed.

External effects belong at a boundary. Printing, writing a receipt and reading a data source are useful program activities, but they should not be confused with the pure numerical transition. A small functional core can be tested with literal inputs while the outer program manages effects and ownership. This unit deliberately does not claim durable file storage or a persistent process between classroom Runs.""",
            r"""Let state be \(s=(a,n)\), with accumulated total \(a\) and nonnegative count \(n\). One observation \(x\) gives \(T(s,x)=(a+x,n+1)\). The mean is \(a/n\) only for \(n>0\). Combining states uses \((a_1+a_2,n_1+n_2)\), so grouping observations does not change the mathematical mean. Averaging two means without their counts generally defines a different weighting rule.""",
            """def transition(state, value):
    total, count = state
    return total + value, count + 1


def mean_of(state):
    total, count = state
    if int(count) <= 0:
        raise ValueError("no observations")
    return total / count

initial = (jnp.float64(0.), jnp.int64(0))""",
            (
                case(
                    "Retain old and new state",
                    "Apply observation 3 to the empty state and inspect both states.",
                    "Old (0,0); new (3,1), mean 3.",
                    "A function returning a new tuple makes the update explicit. The caller still owns the old value.",
                    "new = transition(initial, 3.)\nclose(initial[0], 0.)\nassert int(initial[1]) == 0\nclose(mean_of(new), 3.)",
                    "Do not overwrite the old binding until after inspecting it.",
                ),
                case(
                    "Counts change weighting",
                    "Combine a two-observation group totaling 4 with a singleton totaling 10.",
                    "Combined mean 14/3, not the equal-group mean 6.",
                    "The total/count representation preserves the observation-weighted question. Group means alone conceal the unequal sample sizes.",
                    "combined = (jnp.float64(4. + 10.), jnp.int64(2 + 1))\nclose(mean_of(combined), 14 / 3)\nassert not np.isclose(float(mean_of(combined)), 6.)",
                    "Add sufficient totals before dividing.",
                ),
            ),
            (
                case(
                    "Replay a transition",
                    "Apply observation 5 twice, independently, to the same empty state.",
                    "Both returned states are (5,1).",
                    "Replay means identical inputs. It does not mean feeding the first result into the second call.",
                    "left = transition(initial, 5.)\nright = transition(initial, 5.)\nclose(left[0], right[0])\nassert int(left[1]) == int(right[1]) == 1",
                    "Keep the initial state in both calls.",
                ),
                case(
                    "Accumulate a sequence",
                    "Process observations [1,3,8] in order using returned state.",
                    "Total 12, count 3, mean 4.",
                    "Each next transition consumes the previous returned state.",
                    "state = initial\nfor value in [1., 3., 8.]:\n    state = transition(state, value)\nclose(state[0], 12.)\nassert int(state[1]) == 3\nclose(mean_of(state), 4.)",
                    "Draw the state after each observation.",
                ),
                case(
                    "Refuse an empty mean",
                    "Request the mean of the empty state.",
                    "ValueError.",
                    "Zero observations does not imply a mean of zero.",
                    "try:\n    mean_of(initial)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('empty mean accepted')",
                    "Validate the denominator.",
                ),
                case(
                    "Extend a saved state",
                    "Continue from total 12/count 3 with observation 20.",
                    "Total 32, count 4, mean 8.",
                    "Continuation requires the actual state, not only the previous displayed mean.",
                    "state = transition((jnp.float64(12.), jnp.int64(3)), 20.)\nclose(mean_of(state), 8.)",
                    "A mean of four does not tell you the old count.",
                ),
                case(
                    "Check order-independent totals",
                    "Accumulate [8,3,1] and compare with the same values in ascending order.",
                    "Equal sum/count and mean for these exactly representable values.",
                    "The mathematical aggregation is order-independent; larger floating reductions can still differ by rounding.",
                    "state = initial\nfor value in [8., 3., 1.]:\n    state = transition(state, value)\nclose(state[0], 12.)\nassert int(state[1]) == 3",
                    "Separate exact algebra from a universal bitwise claim.",
                ),
                case(
                    "Merge states",
                    "Merge totals/counts (6,2), (9,3), (5,1) and explain the sufficient information.",
                    "Total 20, count 6, mean 10/3.",
                    "The pair retains enough information for this objective. Variance would require additional information.",
                    "groups = [(6., 2), (9., 3), (5., 1)]\nclose(sum(a for a, n in groups) / sum(n for a, n in groups), 10 / 3)",
                    "Choose state from the next operation's needs.",
                ),
            ),
            "If replay differs, look for hidden mutable state or an external input. If merging groups changes the target quantity, inspect missing counts. The int(count) guard is a host-side boundary in this lesson; it is not yet a JIT-compatible dynamic validation rule.",
            "List the state that would determine the next optimizer update, random draw and dataset position. Compare the explicit transition here with the checkpoint contracts in torch-028 and tf-028. Explain why a saved printed average is not a sufficient general checkpoint.",
            (
                (
                    "Stateful computations",
                    "https://docs.jax.dev/en/latest/stateful-computations.html",
                ),
            ),
        ),
        Unit(
            5,
            "Typed random keys and independent streams",
            "beginner",
            (4,),
            ("PRNG key", "split", "fold_in", "randomness contract"),
            "Thread random keys explicitly and detect accidental reuse without claiming statistical independence from one sample.",
            r"""A pseudorandom function is deterministic given its key and arguments. JAX exposes that key as a value. Calling a random function does not secretly advance the key object. Reusing the same key with the same function, shape and dtype reproduces the same result. That feature supports replay, but it also makes accidental reuse easy to mistake for independent sampling.

Use a typed key created with jax.random.key. To obtain separate streams, split a key and deliberately assign the resulting keys to operations. A common transition keeps one child key as the next state and uses another for the current draw. The exact bookkeeping convention can vary; it must make key ownership clear. A variable named seed is not a substitute for a documented stream policy.

Folding an integer identity into a key supports deterministic association with a step, record or process. This is useful when work is reordered: the intended identifier can determine the draw rather than an accidental loop position. The identifiers and algorithm still belong to the experiment. Changing how keys are split or folded can change the sample even when the initial integer seed is unchanged.

A random sample is not a proof of independence or distributional quality. In this lesson, assertions inspect reproducibility and distinct key identities; statistical summaries are explanatory observations under a pinned setup. A test that two sample values differ is weak because equal random values can occur legitimately. Compare the key policy first, then evaluate stochastic behavior at the appropriate statistical scale.

Later vectorized training and simulation will require choosing whether randomness is shared across examples or separated by example. Both can be meaningful designs. Reusing one dropout mask across every record, however, is not the same experiment as drawing per-record masks. Batched and sequential random generation also need not produce identical arrays merely because the total number of values is the same.""",
            r"""Write a stochastic computation as a deterministic map \((k,x)\mapsto y\). A transition can first compute \((k_{\mathrm{next}},k_{\mathrm{draw}})=\operatorname{split}(k)\), then evaluate the draw with \(k_{\mathrm{draw}}\) and return \(k_{\mathrm{next}}\). No derivative is taken with respect to a key. Reproducibility requires the key, random operation, shape, dtype and relevant implementation version, not just a printed scalar sample.""",
            """def draw_step(key):
    next_key, sample_key = jax.random.split(key)
    return next_key, jax.random.normal(sample_key, shape=(4,), dtype=jnp.float64)


def same_key(left, right):
    return np.array_equal(np.asarray(jax.random.key_data(left)), np.asarray(jax.random.key_data(right)))""",
            (
                case(
                    "Reuse reproduces",
                    "Draw twice from the same typed key with the same shape.",
                    "Arrays agree exactly in this pinned process.",
                    "The random call is a deterministic function of the key; it does not mutate the key.",
                    "key = jax.random.key(7)\na = jax.random.normal(key, (4,))\nb = jax.random.normal(key, (4,))\nassert np.array_equal(np.asarray(a), np.asarray(b))",
                    "Check what state the call returns.",
                ),
                case(
                    "Return the next key",
                    "Call draw_step, then feed its returned key to another step.",
                    "The key changes at each transition; replay from the original key reproduces the first draw.",
                    "State progression is visible and can be stored with the computation's other state.",
                    "key = jax.random.key(7)\nnext_key, first = draw_step(key)\nlast_key, second = draw_step(next_key)\nassert not same_key(key, next_key)\nassert not same_key(next_key, last_key)\nclose(draw_step(key)[1], first)",
                    "Use the returned key for continuation, the old key for replay.",
                ),
            ),
            (
                case(
                    "Inspect a typed key",
                    "Create a key and inspect its scalar shape and key-data representation.",
                    "Key shape (); key_data is an integer array.",
                    "The typed key is not an ordinary floating scalar. Its representation is exposed for inspection or explicit serialization boundaries.",
                    "key = jax.random.key(11)\nassert key.shape == ()\nassert np.issubdtype(np.asarray(jax.random.key_data(key)).dtype, np.integer)",
                    "Do not do arithmetic directly on random-key values.",
                ),
                case(
                    "Split four streams",
                    "Split one key into four and verify pairwise different key data.",
                    "Four distinct key identities in the declared split.",
                    "This checks allocation of streams, not a statistical theorem based on four observed numbers.",
                    "keys = jax.random.split(jax.random.key(11), 4)\nassert keys.shape == (4,)\nassert len({np.asarray(jax.random.key_data(k)).tobytes() for k in keys}) == 4",
                    "Inspect keys rather than requiring arbitrary random samples to be unequal.",
                ),
                case(
                    "Replay a record identity",
                    "Fold record ID 42 into the same root twice.",
                    "Identical folded keys and draws.",
                    "The association is deterministic when both root and identifier agree.",
                    "root = jax.random.key(3)\na = jax.random.fold_in(root, 42)\nb = jax.random.fold_in(root, 42)\nassert same_key(a, b)\nclose(jax.random.uniform(a, (3,)), jax.random.uniform(b, (3,)))",
                    "State which identifier is part of the experiment.",
                ),
                case(
                    "Separate identities",
                    "Fold IDs 42 and 43 into one root and compare key data.",
                    "Different key data.",
                    "A changed identity receives a separate deterministic stream under this policy.",
                    "root = jax.random.key(3)\nassert not same_key(jax.random.fold_in(root, 42), jax.random.fold_in(root, 43))",
                    "Do not replace a stable record ID with its current display order.",
                ),
                case(
                    "Replay a whole transition",
                    "Run three draw_step transitions twice from root key 19.",
                    "All corresponding draws and final keys agree.",
                    "A sequence is reproducible when its transition and starting state are the same.",
                    "def sequence():\n    key = jax.random.key(19)\n    values = []\n    for _ in range(3):\n        key, value = draw_step(key)\n        values.append(value)\n    return key, jnp.stack(values)\na, x = sequence()\nb, y = sequence()\nassert same_key(a, b)\nclose(x, y)",
                    "Compare continuation state as well as outputs.",
                ),
                case(
                    "Diagnose repeated example masks",
                    "Call Bernoulli twice with one key and compare it with an explicit split policy.",
                    "Same-key masks repeat; split keys are distinct even if some sampled mask entries coincide.",
                    "The defect is key reuse when independence was intended, not the coincidence of individual Boolean values.",
                    "key = jax.random.key(5)\na = jax.random.bernoulli(key, .5, (8,))\nb = jax.random.bernoulli(key, .5, (8,))\nassert np.array_equal(np.asarray(a), np.asarray(b))\nk1, k2 = jax.random.split(key)\nassert not same_key(k1, k2)",
                    "A sample can coincide legitimately; inspect the stream assignment.",
                ),
            ),
            "Repeated randomness often comes from discarding the returned key or broadcasting one key over all examples. Unexpected non-replay can come from changed shape, dtype, split order or version. Do not promise cross-version bitwise identity without an explicit tested contract.",
            "Design a stream policy for a simulation with independent records and repeated steps. Name what stays reproducible if record order changes, then explain how that policy differs from consuming one sequential stream. Connect the result to cuda-050 without claiming GPU execution.",
            (
                ("Random numbers", "https://docs.jax.dev/en/latest/random-numbers.html"),
                ("fold_in", "https://docs.jax.dev/en/latest/_autosummary/jax.random.fold_in.html"),
            ),
        ),
        Unit(
            6,
            "Pytrees organize parameters and state",
            "beginner",
            (5,),
            ("pytree", "leaf", "tree structure", "parameter update"),
            "Inspect, transform and reconstruct structured numerical state while preserving leaf identities and shapes.",
            r"""A real numerical computation rarely has one parameter. A two-layer model may contain a matrix and bias for each layer, plus optimizer moments and a step counter. JAX calls a nested structure of supported containers and leaves a pytree. Transformations can operate on its numerical leaves while preserving the surrounding structure.

Tree structure carries meaning. A dictionary with a weight and bias is different from a tuple whose first and second elements happen to contain the same arrays. When mapping over several trees, corresponding containers must align. Equal total element counts do not establish compatibility. A missing bias or differently nested optimizer state should be diagnosed as a contract mismatch.

Use jax.tree.map to apply a leaf-level operation consistently. For an SGD update, each parameter leaf is paired with its gradient leaf. The output tree has the same structure as the parameter tree. This is not a special neural-network object system: the mechanism works for simulation state, diagnostics and other nested numerical data too.

Flattening produces a list of leaves plus a structure description. Keep both when reconstructing the original object. Flattening alone discards the container arrangement. A shape tuple is itself a container of integers, which can surprise a learner who expected it to behave like one opaque leaf. Likewise, None is handled specially by ordinary pytree traversal. Inspect the actual tree representation instead of guessing from printed nesting.

Custom container registration becomes useful when a domain object holds numerical arrays and static metadata. The flattening contract must decide which fields are transformed and which are part of the structure. This unit uses standard containers first so that the core behavior stays visible. Advanced compilation lessons will explain why static metadata also affects specialization and caching.""",
            r"""For corresponding parameter and gradient trees \(P\) and \(G\), an SGD map applies \(P'_\ell=P_\ell-\eta G_\ell\) at every leaf \(\ell\). The index denotes a tree leaf, not an array coordinate. Within a leaf the ordinary array shape contract still applies. A correct tree-level match does not prevent a gradient with a broadcastable but unintended leaf shape, so verify both structure and each leaf's shape.""",
            """params = {"weight": jnp.array([[1., 2.], [3., 4.]]), "bias": jnp.array([1., -1.])}


def checked_update(parameters, gradients, rate):
    if jax.tree.structure(parameters) != jax.tree.structure(gradients):
        raise ValueError("gradient tree differs")
    for p, g in zip(jax.tree.leaves(parameters), jax.tree.leaves(gradients)):
        if p.shape != g.shape:
            raise ValueError("gradient leaf shape differs")
    return jax.tree.map(lambda p, g: p - rate * g, parameters, gradients)""",
            (
                case(
                    "Map an update over a tree",
                    "Subtract rate 0.1 times all-one gradient leaves.",
                    "Every numerical parameter decreases by 0.1; old params remain unchanged.",
                    "The same scalar rule is applied independently at corresponding leaves, preserving dictionary keys and array shapes.",
                    "gradients = jax.tree.map(jnp.ones_like, params)\nupdated = checked_update(params, gradients, .1)\nclose(updated['weight'], [[.9, 1.9], [2.9, 3.9]])\nclose(updated['bias'], [.9, -1.1])\nclose(params['bias'], [1., -1.])",
                    "Compare tree structure before comparing values.",
                ),
                case(
                    "Reject a misleading broadcast",
                    "Supply a scalar bias gradient instead of the length-two gradient leaf.",
                    "ValueError despite legal scalar-array subtraction.",
                    "Tree shape and array shape are separate contracts. Broadcasting a scalar would conceal a missing per-coordinate derivative.",
                    "wrong = {'weight': jnp.ones((2, 2)), 'bias': jnp.float64(1.)}\ntry:\n    checked_update(params, wrong, .1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('bad leaf shape accepted')",
                    "A dictionary-key match is only the first check.",
                ),
            ),
            (
                case(
                    "Inspect the leaf ledger",
                    "Map each parameter leaf to its shape.",
                    "Weight (2,2), bias (2,).",
                    "This ledger explains which arrays a later transformation will receive.",
                    "shapes = jax.tree.map(lambda x: x.shape, params)\nassert shapes == {'weight': (2, 2), 'bias': (2,)}",
                    "Do not confuse the output shape tuples with original array leaves.",
                ),
                case(
                    "Count stored scalars",
                    "Count the parameter entries across all leaves.",
                    "Six scalar entries.",
                    "The count is four matrix entries plus two biases, not the number of containers.",
                    "assert sum(x.size for x in jax.tree.leaves(params)) == 6",
                    "Count each array's size after obtaining leaves.",
                ),
                case(
                    "Reconstruct the tree",
                    "Flatten params, retain the structure, then unflatten.",
                    "Same structure and values.",
                    "The structure descriptor preserves how leaves belong to containers.",
                    "leaves, structure = jax.tree.flatten(params)\nrestored = jax.tree.unflatten(structure, leaves)\nassert jax.tree.structure(restored) == jax.tree.structure(params)\nclose(restored['weight'], params['weight'])",
                    "Keep the treedef with the leaf list.",
                ),
                case(
                    "Reject a missing field",
                    "Try updating with a tree that lacks the bias.",
                    "ValueError before mapping.",
                    "A smaller gradient tree does not describe an update for every parameter under this contract.",
                    "try:\n    checked_update(params, {'weight': jnp.ones((2, 2))}, .1)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('missing leaf accepted')",
                    "Compare structural identity, not dictionary length alone.",
                ),
                case(
                    "Apply distinct gradients",
                    "Use matrix gradient 2 and bias gradient [3,-4] at rate 0.5.",
                    "Weight [[0,1],[2,3]], bias [-0.5,1].",
                    "Leaf correspondence preserves which gradient belongs to which parameter.",
                    "g = {'weight': jnp.full((2, 2), 2.), 'bias': jnp.array([3., -4.])}\nu = checked_update(params, g, .5)\nclose(u['weight'], [[0., 1.], [2., 3.]])\nclose(u['bias'], [-.5, 1.])",
                    "Derive the two bias updates separately.",
                ),
                case(
                    "Transfer to nested state",
                    "Map zeros_like over a tuple containing params and a scalar counter array.",
                    "Same structure; all seven numerical entries zero.",
                    "The mechanism is about nested numerical state, not only one model dictionary.",
                    "state = (params, jnp.int64(4))\nzero = jax.tree.map(jnp.zeros_like, state)\nassert jax.tree.structure(zero) == jax.tree.structure(state)\nassert all(bool(jnp.all(x == 0)) for x in jax.tree.leaves(zero))",
                    "Treat the counter according to its role rather than assuming every leaf is a trainable parameter.",
                ),
            ),
            "A mismatch can come from container structure, leaf shape, dtype or semantic identity. Diagnose them separately. Do not assume that every leaf in a state tree should receive a gradient or optimizer update; counters and random keys have different roles.",
            "Design separate parameter, optimizer and diagnostic trees for a two-layer model. Explain what must be preserved to resume one update and which metadata should remain static. Compare this explicit representation with registered parameter objects in torch-003.",
            (("Pytrees", "https://docs.jax.dev/en/latest/pytrees.html"),),
        ),
    ]
)
