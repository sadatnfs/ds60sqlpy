"""Differentiation, transformations and explicit training-state mechanisms."""

from model import Unit, case

UNITS = [
    Unit(
        7,
        "Differentiate a scalar loss and audit one update",
        "beginner",
        (6,),
        ("gradient", "scalar objective", "value_and_grad", "stop_gradient"),
        "Derive a scalar gradient, compare it independently, and separate differentiation from parameter updating.",
        r"""A derivative measures how an output changes for a small change in an input. It is not a new parameter value. JAX's grad takes a scalar-valued numerical function and returns another function that evaluates its derivative. For a vector of parameters, the result contains one sensitivity for each parameter coordinate. For a parameter pytree, the gradients follow the same structure.

The scalar-output requirement is substantive. A vector of per-example losses describes several outputs. Turning it into a sum or mean specifies how those examples influence one training objective. A mean and a sum have gradients differing by the example count, so choosing a reduction changes the optimizer step even if every per-example prediction is unchanged.

Use value_and_grad when both the objective and its gradient are needed at the same parameter state. Those returned values still describe the pre-update computation. Subtracting a learning rate times the gradient returns a new parameter; calculate a fresh objective if you want the post-update loss. JAX does not maintain a mutable .grad field like the ordinary PyTorch leaf-tensor workflow.

An independent oracle is stronger than comparing two wrappers around the same calculation. We can derive the one-parameter squared-error gradient algebraically, then compare it with autodiff and a central finite difference. Finite differences are approximate, and their step size interacts with rounding and curvature. They are a diagnostic for a specified smooth point, not a universal proof of differentiability.

Stopping a gradient preserves forward values while deliberately changing the derivative path. This is useful for a defined modeling reason, but a zero gradient caused by stop_gradient is not evidence that the objective is locally constant as an ordinary mathematical function. Keep the forward equation and the differentiation contract separate when explaining the result.""",
        r"""For \(x=[1,2,3]\), \(y=2x\), the mean squared objective is \(L(w)=\frac{14}{3}(w-2)^2\). Thus \(L'(w)=\frac{28}{3}(w-2)\). At zero, the loss is \(56/3\) and the gradient is \(-56/3\). SGD with \(\eta=0.1\) gives \(w'=28/15\), whose fresh loss is \(56/675\). These four numbers are separate observations. A different denominator or broadcast can preserve one while changing the others.""",
        """x = jnp.array([1., 2., 3.])
y = 2 * x


def loss(weight):
    return jnp.mean((weight * x - y) ** 2)""",
        (
            case(
                "Four quantities in one update",
                "Calculate loss and gradient at zero, apply rate 0.1, then recalculate loss.",
                "56/3, -56/3, 28/15 and 56/675 respectively.",
                "value_and_grad returns values at the original weight. The final call evaluates the changed state rather than reporting the stale first loss.",
                "value, gradient = jax.value_and_grad(loss)(jnp.float64(0.))\nupdated = -.1 * gradient\nclose(value, 56 / 3)\nclose(gradient, -56 / 3)\nclose(updated, 28 / 15)\nclose(loss(updated), 56 / 675)",
                "Write the algebraic derivative before calling grad.",
            ),
            case(
                "Same forward value, different derivative",
                "Compare a square with a square whose input is wrapped in stop_gradient at x=3.",
                "Both forward values 9; derivatives 6 and 0.",
                "The stopped branch explicitly defines a different autodiff path without changing the evaluated value.",
                "ordinary = lambda z: z * z\nstopped = lambda z: jax.lax.stop_gradient(z) ** 2\nclose(ordinary(3.), stopped(3.))\nclose(jax.grad(ordinary)(3.), 6.)\nclose(jax.grad(stopped)(3.), 0.)",
                "The function value alone cannot identify its tracked dependencies.",
            ),
        ),
        (
            case(
                "Check another smooth point",
                "Evaluate the gradient at weight one using the closed form.",
                "-28/3.",
                "Moving halfway to the optimum halves the gradient magnitude for this quadratic.",
                "close(jax.grad(loss)(1.), -28 / 3)",
                "Substitute w=1 into the derivative.",
            ),
            case(
                "Use a central difference",
                "Estimate the derivative at w=0.7 with h=1e-5 and compare to autodiff.",
                "Agreement within absolute 1e-8.",
                "Both perturbed losses must recompute the full expression from their own weight.",
                "w, h = .7, 1e-5\nnumerical = (loss(w + h) - loss(w - h)) / (2 * h)\nclose(numerical, jax.grad(loss)(w), atol=1e-8, rtol=0.)",
                "Do not hold an intermediate prediction fixed while perturbing the weight.",
            ),
            case(
                "Change the reduction",
                "Differentiate the summed squared error at zero.",
                "-56, three times the mean-loss gradient.",
                "A sum gives each of the three observations its full contribution without dividing by count.",
                "summed = lambda w: jnp.sum((w * x - y) ** 2)\nclose(jax.grad(summed)(0.), -56.)",
                "Differentiate the denominator as a constant count.",
            ),
            case(
                "Inspect the optimum",
                "Evaluate value and derivative at w=2.",
                "Both zero.",
                "This exact fixture has an algebraic zero-residual solution; a general fitted model need not.",
                "value, gradient = jax.value_and_grad(loss)(2.)\nclose(value, 0.)\nclose(gradient, 0.)",
                "A zero derivative alone would not prove a global minimum for an arbitrary function.",
            ),
            case(
                "Differentiate a parameter tree",
                "Differentiate mean squared error for a weight and bias, both initially zero.",
                "Weight gradient -56/3; bias gradient -8.",
                "The bias derivative averages two times each residual, while the weight derivative also multiplies by input.",
                "def affine_loss(p):\n    return jnp.mean((p['weight'] * x + p['bias'] - y) ** 2)\ng = jax.grad(affine_loss)({'weight': jnp.float64(0.), 'bias': jnp.float64(0.)})\nclose(g['weight'], -56 / 3)\nclose(g['bias'], -8.)",
                "Derive both coordinates independently.",
            ),
            case(
                "Choose a scalar objective",
                "Demonstrate that grad refuses an unreduced vector loss, then reduce it explicitly.",
                "TypeError for vector output; a finite gradient for its mean.",
                "The repair chooses a mathematical objective. It is not merely making an error message disappear.",
                "vector_loss = lambda w: (w * x - y) ** 2\ntry:\n    jax.grad(vector_loss)(0.)\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError('vector objective accepted')\nclose(jax.grad(lambda w: vector_loss(w).mean())(0.), -56 / 3)",
                "State which observations receive which weights.",
            ),
        ),
        "For a surprising derivative, inspect reduction, shape, stopped paths and whether the independent finite difference recomputes the full function. For a surprising reported training loss, check whether it came from before or after the update. Increasing tolerance cannot repair a wrong objective.",
        "Compare this exact scalar oracle with torch-008 and tf-008 using matched dtype, inputs and reduction. Explain returned gradients versus mutable gradient buffers. A matching one-step result is a useful porting check, not proof that whole training workflows are equivalent.",
        (
            (
                "Automatic differentiation",
                "https://docs.jax.dev/en/latest/automatic-differentiation.html",
            ),
            (
                "stop_gradient",
                "https://docs.jax.dev/en/latest/_autosummary/jax.lax.stop_gradient.html",
            ),
        ),
    ),
    Unit(
        8,
        "JVPs and VJPs are shaped linear maps",
        "intermediate",
        (7,),
        ("Jacobian", "tangent", "cotangent", "pushforward", "pullback"),
        "Compute directional derivatives and pullbacks with explicit input/output shapes and an independent duality check.",
        r"""A scalar gradient is one instance of a more general derivative map. For a function from two inputs to three outputs, its Jacobian has three rows and two columns. Each row describes one output's sensitivity to the two inputs. Forming the whole matrix is possible for a tiny fixture, but often unnecessary for a large computation.

A Jacobian-vector product, or JVP, asks how the outputs change in one input direction. Its tangent has the same shape as the input; the resulting output tangent has the same shape as the function output. A vector-Jacobian product, or VJP, starts with an output cotangent and pulls it back to input coordinates. A scalar-loss gradient is a pullback from the scalar output with cotangent one.

The names vector and Jacobian can hide an orientation choice. This lesson treats column-coordinate vectors: JVP is J times v, while the pullback is J-transpose times u. JAX's vjp returns the ordinary output and a callable pullback. Calling that pullback requires an output-shaped cotangent, and it returns a tuple matching the differentiated input arguments.

For a smooth function, the identity u dot (Jv) equals v dot (J-transpose u) gives a useful independent consistency check. It compares two views of the same local linear map. This does not prove that the map was derived for the right original function, so retain a hand-computed Jacobian or finite-difference directional check too.

Choosing forward or reverse mode is a computational decision. The number and structure of inputs and outputs matter, as do memory and reuse. Do not generalize a tiny timing result into a universal claim that one mode is always faster. First learn to predict the shapes and the question each operation answers.""",
        r"""Let \(f(x)=(x_0^2,x_0x_1,\sin x_1)\). At \(x=(2,0)\), the Jacobian is \(J=\begin{bmatrix}4&0\\0&2\\0&1\end{bmatrix}\). With \(v=(3,4)\), \(Jv=(12,8,4)\). With \(u=(1,2,3)\), \(J^{\mathsf T}u=(4,7)\). Both inner products in the duality relation equal 40. The derivative depends on the evaluation point, not only the function's input shape.""",
        """def function(value):
    a, b = value
    return jnp.stack((a * a, a * b, jnp.sin(b)))

point = jnp.array([2., 0.])
jacobian = jnp.array([[4., 0.], [0., 2.], [0., 1.]])""",
        (
            case(
                "Push one input direction",
                "Compute a JVP at [2,0] in direction [3,4].",
                "Primal [4,0,0]; tangent [12,8,4].",
                "The primal and tangent are separate outputs. The tangent is a local sensitivity, not a new evaluation at point plus direction.",
                "value, tangent = jax.jvp(function, (point,), (jnp.array([3., 4.]),))\nclose(value, [4., 0., 0.])\nclose(tangent, [12., 8., 4.])",
                "Multiply the written Jacobian by the direction.",
            ),
            case(
                "Pull back an output weighting",
                "Create the VJP pullback and apply output cotangent [1,2,3].",
                "Input cotangent [4,7].",
                "The cotangent gives the weights of a local scalar combination of output changes. The returned tuple has one entry because the function has one differentiated argument.",
                "value, pullback = jax.vjp(function, point)\n(input_cotangent,) = pullback(jnp.array([1., 2., 3.]))\nclose(input_cotangent, [4., 7.])",
                "The cotangent belongs to the three-dimensional output space.",
            ),
        ),
        (
            case(
                "Probe the first input coordinate",
                "Use direction [1,0] in a JVP.",
                "[4,0,0], the first Jacobian column.",
                "A coordinate-direction probe selects one column of the derivative map.",
                "close(jax.jvp(function, (point,), (jnp.array([1., 0.]),))[1], [4., 0., 0.])",
                "Columns correspond to input coordinates.",
            ),
            case(
                "Probe the second output coordinate",
                "Use output cotangent [0,1,0] in the pullback.",
                "[0,2], the second Jacobian row transposed.",
                "A coordinate cotangent selects one output's sensitivities to all inputs.",
                "_, back = jax.vjp(function, point)\nclose(back(jnp.array([0., 1., 0.]))[0], [0., 2.])",
                "Rows correspond to output coordinates.",
            ),
            case(
                "Check duality",
                "Compare u dot Jv with v dot the pullback of u for the stated vectors.",
                "Both 40.",
                "This identity connects the forward and reverse linear maps at one point.",
                "v, u = jnp.array([3., 4.]), jnp.array([1., 2., 3.])\njv = jax.jvp(function, (point,), (v,))[1]\n_, back = jax.vjp(function, point)\nclose(jnp.vdot(u, jv), 40.)\nclose(jnp.vdot(v, back(u)[0]), 40.)",
                "Do not swap a tangent with a cotangent of a different shape.",
            ),
            case(
                "Check a directional finite difference",
                "Perturb point along [3,4] using h=1e-5.",
                "Agreement with JVP within absolute 1e-8.",
                "The perturbation changes the input in exactly the direction supplied to JVP.",
                "direction, h = jnp.array([3., 4.]), 1e-5\nfinite = (function(point + h * direction) - function(point - h * direction)) / (2 * h)\nclose(finite, jacobian @ direction, atol=1e-8, rtol=0.)",
                "A vector output can be compared coordinate by coordinate.",
            ),
            case(
                "Change the point",
                "Evaluate the Jacobian at [1,1] with jacfwd.",
                "[[2,0],[1,1],[0,cos(1)]].",
                "The bilinear and sinusoidal derivatives change with the evaluation point.",
                "close(jax.jacfwd(function)(jnp.array([1., 1.])), [[2., 0.], [1., 1.], [0., math.cos(1.)]])",
                "Differentiate before substituting the new point.",
            ),
            case(
                "Recover a scalar gradient",
                "Differentiate the weighted output sum with weights [1,2,3].",
                "[4,7], matching the VJP.",
                "A scalar objective supplies one cotangent; its chain rule is the same pullback.",
                "weights = jnp.array([1., 2., 3.])\nclose(jax.grad(lambda z: jnp.vdot(weights, function(z)))(point), [4., 7.])",
                "Write the scalar combination explicitly.",
            ),
        ),
        "A tangent shape belongs to the input and a cotangent shape belongs to the output. If the result is transposed or has the wrong length, write these spaces down before changing an axis. Agreement between two autodiff calls should still be paired with an independent analytical or directional oracle.",
        "Explain how a scientific simulator with many outputs and few parameters differs from a scalar training objective with many parameters. Choose a derivative question before choosing a mode, then connect the choice to memory and the number of directions actually needed.",
        (
            ("JVP", "https://docs.jax.dev/en/latest/_autosummary/jax.jvp.html"),
            ("VJP", "https://docs.jax.dev/en/latest/_autosummary/jax.vjp.html"),
        ),
    ),
]

UNITS.extend(
    [
        Unit(
            9,
            "Jacobians, curvature and matrix-free products",
            "intermediate",
            (8,),
            ("Jacobian", "Hessian", "Hessian-vector product", "curvature"),
            "Inspect second-order structure and calculate a Hessian-vector product without requiring a dense Hessian.",
            r"""The derivative of a gradient is a Hessian. For a scalar function of two parameters, the Hessian is a two-by-two matrix. Its entries describe how one gradient coordinate changes as another parameter changes. A positive curvature along a direction means the local slope increases along that direction; it does not by itself establish a global theorem for an arbitrary nonquadratic function.

Small matrices are useful for learning because every entry can be checked. Large models make a dense Hessian expensive: storage grows with the square of parameter count. Many algorithms need only the Hessian applied to one vector. A JVP of the gradient computes that local product directly, avoiding a requirement to materialize every column.

Forward-over-reverse and reverse-over-forward are compositions of transformations, not separate mathematical definitions of curvature. They should agree on the same smooth objective under an appropriate numerical tolerance. Shape and differentiation-domain choices still matter. A vector-valued function has a Jacobian; calling a second transform does not erase the need to say which scalar objective is being studied.

A finite-difference check of a Hessian-vector product perturbs the gradient along the same direction. This numerical comparison depends on step size, floating precision and local smoothness. It becomes unreliable at a kink or singular point. Include a smooth quadratic with an exact oracle before moving to nonlinear examples, and report what was actually checked.

The point of this unit is not to recommend Newton's method universally. Curvature computations can support sensitivity analysis, optimization, diagnostics or approximation. Their usefulness depends on the objective and computational budget. Correctly producing a Hessian does not establish that a statistical model is identified, that a numerical simulator is accurate, or that the chosen optimizer will converge globally.""",
            r"""For \(f(x)=x_0^2+x_0x_1+2x_1^2\), the gradient is \((2x_0+x_1,x_0+4x_1)\) and \(H=\begin{bmatrix}2&1\\1&4\end{bmatrix}\). At \((1,2)\), the gradient is \((4,9)\). Applying H to \((2,-1)\) gives \((3,-2)\), and the directional curvature \(v^{\mathsf T}Hv\) is 8. The constant Hessian makes this a controlled oracle rather than a claim about every learned objective.""",
            """def quadratic(value):
    a, b = value
    return a * a + a * b + 2 * b * b

point = jnp.array([1., 2.])
expected_hessian = jnp.array([[2., 1.], [1., 4.]])""",
            (
                case(
                    "Inspect every curvature entry",
                    "Calculate the Hessian with jacfwd applied to grad.",
                    "[[2,1],[1,4]], symmetric.",
                    "Each column is a direction of change in the gradient. The cross terms agree because this polynomial is smooth.",
                    "hessian = jax.jacfwd(jax.grad(quadratic))(point)\nclose(hessian, expected_hessian)\nclose(hessian, hessian.T)",
                    "Differentiate the two gradient coordinates by hand.",
                ),
                case(
                    "Ask only for the needed product",
                    "Compute a JVP of grad in direction [2,-1].",
                    "[3,-2], matching H times the direction.",
                    "The product asks one linear-map question rather than requesting every Hessian entry.",
                    "direction = jnp.array([2., -1.])\nproduct = jax.jvp(jax.grad(quadratic), (point,), (direction,))[1]\nclose(product, [3., -2.])\nclose(product, expected_hessian @ direction)",
                    "The function being differentiated is now the gradient.",
                ),
            ),
            (
                case(
                    "Check the first derivative",
                    "Calculate grad at [1,2] before inspecting curvature.",
                    "[4,9].",
                    "A second-order check is difficult to interpret if the first-order objective is wrong.",
                    "close(jax.grad(quadratic)(point), [4., 9.])",
                    "Derive the gradient from the original scalar function.",
                ),
                case(
                    "Reverse the transform order",
                    "Compare jacrev of grad with jacfwd of grad.",
                    "Both match the same two-by-two matrix.",
                    "The algorithms differ, while the smooth local derivative contract is the same.",
                    "close(jax.jacrev(jax.grad(quadratic))(point), expected_hessian)",
                    "Keep the point, dtype and objective fixed.",
                ),
                case(
                    "Check a matrix-free product numerically",
                    "Central-difference the gradient along [2,-1] with h=1e-5.",
                    "[3,-2] within absolute 1e-8.",
                    "This perturbs the complete gradient calculation in the exact direction under investigation.",
                    "v, h = jnp.array([2., -1.]), 1e-5\ngradient = jax.grad(quadratic)\nfinite = (gradient(point + h * v) - gradient(point - h * v)) / (2 * h)\nclose(finite, [3., -2.], atol=1e-8, rtol=0.)",
                    "Do not perturb only one coordinate unless it is the chosen direction.",
                ),
                case(
                    "Interpret directional curvature",
                    "Calculate v dot H v for v=[2,-1].",
                    "8, a positive curvature in this direction.",
                    "The scalar weights a local second-order change along one direction.",
                    "v = jnp.array([2., -1.])\nclose(jnp.vdot(v, expected_hessian @ v), 8.)",
                    "This is one scalar quadratic form.",
                ),
                case(
                    "Change the evaluation point",
                    "Evaluate the quadratic's Hessian at [-3,7].",
                    "The same constant Hessian.",
                    "A degree-two polynomial has a constant second derivative. A nonlinear objective need not.",
                    "close(jax.hessian(quadratic)(jnp.array([-3., 7.])), expected_hessian)",
                    "Ask which part of the derivative still depends on x.",
                ),
                case(
                    "Contrast nonlinear curvature",
                    "Evaluate the second derivative of x^4 at x=0 and x=2.",
                    "0 and 48.",
                    "Curvature now depends on the point, so one stored Hessian cannot describe every region.",
                    "second = jax.grad(jax.grad(lambda z: z ** 4))\nclose(second(0.), 0.)\nclose(second(2.), 48.)",
                    "Differentiate twice symbolically before comparing.",
                ),
            ),
            "A dense Hessian's successful construction can conceal an unnecessary memory cost. Check whether the task needs the full matrix, a diagonal approximation or products with selected vectors. Do not interpret finite-difference failure at a nonsmooth point as proof that all autodiff is broken.",
            "Connect curvature to the least-squares Hessian in the statistics book. Explain when a matrix-free product would be sufficient for an iterative method, and which additional convergence and conditioning assumptions that method would need.",
            (("Autodiff cookbook", "https://docs.jax.dev/en/latest/301/cookbook.html"),),
        ),
        Unit(
            10,
            "JIT tracing, static inputs and compilation reuse",
            "intermediate",
            (9,),
            ("tracer", "static argument", "specialization", "compilation cache"),
            "Predict which Python behavior happens during tracing and choose a valid compilation boundary.",
            r"""JIT compilation separates describing a computation from executing its compiled form. During tracing, JAX follows Python structure using abstract information about array arguments, such as shape and dtype. Numerical operations become a representation that can be compiled. Ordinary Python side effects encountered during that trace do not become reliable per-execution numerical state updates.

This explains a common surprise: an ordinary print or list append may happen when the function is first traced and not on a later call reusing the compiled form. A Python counter inside the function is therefore not a sound count of numerical executions. Use explicit numerical state or an appropriate debugging API for the question you are asking.

Static arguments supply values to Python-level decisions at trace time. A loop length can be static when it comes from a deliberately small configuration set. The resulting compiled specialization depends on that static value. Marking frequently changing data static can create excessive recompilation and misses the intended computational model.

A traced array value cannot generally decide a Python if statement. Python wants a concrete truth value while tracing; the runtime array value is not available in that form. The correct repair may be structured array control flow, taught in the next unit, or a genuinely static configuration. Choosing static solely to suppress an error can change compilation behavior and resource use.

Compilation reuse also has a lifetime. The classroom starts a new process for every Run. Repeating a call within one submitted program can reuse its compiled function; pressing Run again does not prove reuse of the previous process's cache. Keep first-call work and warm execution separate, and never infer performance from a timer that did not wait for the computation to complete.""",
            r"""For a fixed scalar configuration n, \(f(x,n)=\sum_{i=1}^{n}x=nx\). Python can unroll a small static n during tracing. For dynamic values, an array control-flow representation is a different implementation choice. A cache specialization is associated with more than the displayed numeric value of x: shape, dtype, static configuration and function identity can matter. The exact trace count below is a local diagnostic for a freshly created function in this pinned environment.""",
            """def repeat_add(value, n):
    result = 0. * value
    for _ in range(n):
        result = result + value
    return result

compiled_repeat = jax.jit(repeat_add, static_argnames=("n",))""",
            (
                case(
                    "A deliberate static loop",
                    "Compile repeat_add with n static and compare n=3 and n=4 for x=2.",
                    "6 and 8.",
                    "The loop length is an authored configuration, so Python can build a finite computation for each supplied static value.",
                    "close(compiled_repeat(2., n=3), 6.)\nclose(compiled_repeat(2., n=4), 8.)",
                    "Decide whether n is configuration or changing runtime data.",
                ),
                case(
                    "Trace-time effects are not runtime counters",
                    "Append input shape to a list while tracing a fresh jitted function, then call twice with the same shape.",
                    "One trace-list entry, while both calls return their own numerical results.",
                    "The list append observes tracing. The second call can execute compiled arithmetic with a different value without repeating that Python side effect.",
                    "traces = []\ndef observed(z):\n    traces.append(z.shape)\n    return z + 1\ncompiled = jax.jit(observed)\nclose(compiled(jnp.array([1., 2.])), [2., 3.])\nclose(compiled(jnp.array([4., 5.])), [5., 6.])\nassert traces == [(2,)]",
                    "Keep function identity, shape and dtype fixed.",
                ),
            ),
            (
                case(
                    "Compare eager and compiled values",
                    "Evaluate a smooth polynomial eagerly and under JIT on [1,2,3].",
                    "Both give [3,7,13].",
                    "Compilation should preserve the declared operation within its numerical contract.",
                    "function = lambda z: z * z + z + 1\nvalues = jnp.array([1., 2., 3.])\nclose(function(values), [3., 7., 13.])\nclose(jax.jit(function)(values), function(values))",
                    "Use a nonconstant input vector.",
                ),
                case(
                    "Observe a shape specialization",
                    "Call one fresh traced function with length two and length three.",
                    "Two trace-list entries with the corresponding shapes.",
                    "Abstract shape information changes the specialization even when the elementwise formula is unchanged.",
                    "traces = []\ndef shaped(z):\n    traces.append(z.shape)\n    return z * 2\ncompiled = jax.jit(shaped)\ncompiled(jnp.ones(2)).block_until_ready()\ncompiled(jnp.ones(3)).block_until_ready()\nassert traces == [(2,), (3,)]",
                    "A different shape can require a new compiled program.",
                ),
                case(
                    "Expose a traced Boolean error",
                    "JIT a Python if that depends on the numerical value of an array scalar.",
                    "TracerBoolConversionError.",
                    "The Python branch asks for a concrete truth value during tracing. Dynamic numerical control needs an array control-flow primitive.",
                    "def bad(z):\n    if z > 0:\n        return z\n    return -z\ntry:\n    jax.jit(bad)(jnp.float64(2.))\nexcept jax.errors.TracerBoolConversionError:\n    pass\nelse:\n    raise AssertionError('dynamic Python condition accepted')",
                    "Distinguish an array value from shape metadata.",
                ),
                case(
                    "Keep zero iterations defined",
                    "Evaluate the static loop with n=0.",
                    "Zero with the input's scalar shape.",
                    "The initial carry is the result when no iterations execute.",
                    "close(compiled_repeat(3., n=0), 0.)",
                    "State the loop's identity value.",
                ),
                case(
                    "Compose differentiation with compilation",
                    "Differentiate the compiled square-sum function at [1,2].",
                    "Gradient [2,4].",
                    "A supported transformation composition preserves the chain rule for the same scalar objective.",
                    "compiled_loss = jax.jit(lambda z: jnp.sum(z * z))\nclose(jax.grad(compiled_loss)(jnp.array([1., 2.])), [2., 4.])",
                    "The output must still be a scalar for grad.",
                ),
                case(
                    "Inspect the staged operations",
                    "Create a jaxpr for x*x+1 and identify numerical equations.",
                    "A jaxpr with numerical equations and one output variable.",
                    "This is inspection of the staged computation, not proof of speed or a particular hardware instruction schedule.",
                    "closed = jax.make_jaxpr(lambda z: z * z + 1)(jnp.float64(2.))\nassert len(closed.jaxpr.eqns) >= 1\nassert len(closed.jaxpr.outvars) == 1",
                    "Avoid brittle tests of pretty-printed compiler text.",
                ),
            ),
            "For repeated recompilation, inspect function identity, static values, shapes and dtypes. For a missing Python side effect, ask whether it happened only during tracing. Do not introduce mutable global state to communicate between compiled calls.",
            "Explain why a static batch size and a dynamic threshold are different decisions. Design a small family of acceptable shapes or configurations and name the evidence needed to measure compilation overhead separately from warm execution.",
            (("JIT compilation", "https://docs.jax.dev/en/latest/jit-compilation.html"),),
        ),
    ]
)

UNITS.extend(
    [
        Unit(
            11,
            "Structured control flow and fixed-shape carries",
            "intermediate",
            (10,),
            ("cond", "scan", "while_loop", "loop carry", "dynamic shape"),
            "Express dynamic decisions and repeated state transitions in forms compatible with the intended JAX transformations.",
            r"""Python control flow and numerical control flow answer different questions during tracing. A Python branch can choose a static configuration before compilation. A runtime array value needs a representation whose decision remains part of the numerical computation. lax.cond supplies that representation for a scalar predicate, with branches that agree on output structure and shape.

A loop also has a state contract. lax.scan applies one transition repeatedly over a sequence and can return both the final carry and a history of outputs. The carry must retain its shape, dtype and tree structure at each step. A changing-length Python list is not a valid replacement for a fixed numerical carry. If the task needs variable-length records, padding, masks or a separate admission policy can provide a fixed storage representation without pretending padding is an observation.

Scan is especially useful for training and simulation because it makes the transition explicit. The mathematical recurrence should be derived before the code. A hidden dependency on a later input, an incorrect initial value or a different recurrence coefficient changes the function even if every output shape remains legal.

Dynamic while loops have a different differentiation contract from a fixed scan. A condition based on a runtime value can control how many iterations execute. Ordinary reverse-mode differentiation through such a dynamic loop is not generally supported by the standard primitive, whereas forward-mode can answer some local sensitivity questions. Do not replace a meaningful stopping rule with a fixed number of iterations merely to hide a differentiation error without explaining the changed computation.

A padded batch and a fixed-length scan are implementation tools, not permission to dilute an objective. Keep the count of participating events explicit. The next units will compose these control-flow choices with vectorization and masked objectives, retaining the same separation between storage and statistical meaning.""",
            r"""The recurrence \(h_{t+1}=\frac12h_t+x_t\), starting at zero with inputs \([2,2,2]\), gives states \([2,3,3.5]\). The final sensitivity to the initial state is \((1/2)^3=1/8\). Sensitivities to the three inputs are \([1/4,1/2,1]\): earlier inputs pass through more attenuation steps. These independently derived coefficients test the transition and its differentiation together.""",
            """def recurrence(initial, values):
    def step(carry, value):
        updated = .5 * carry + value
        return updated, updated
    return jax.lax.scan(step, initial, values)


def branch(value):
    return jax.lax.cond(value >= 0., lambda x: x * x, lambda x: -x, value)""",
            (
                case(
                    "Trace a scan",
                    "Evaluate the recurrence on three values equal to two.",
                    "Final 3.5, history [2,3,3.5].",
                    "The returned carry and history have different roles. The final carry is the last updated state; the history makes every transition inspectable.",
                    "last, history = recurrence(jnp.float64(0.), jnp.array([2., 2., 2.]))\nclose(last, 3.5)\nclose(history, [2., 3., 3.5])",
                    "Write every intermediate state on paper.",
                ),
                case(
                    "Branch on a runtime value",
                    "JIT branch and evaluate positive two and negative two.",
                    "4 and 2.",
                    "Both branches return one scalar with the same dtype. The condition is represented inside the numerical program rather than converted to a Python Boolean during tracing.",
                    "compiled = jax.jit(branch)\nclose(compiled(jnp.float64(2.)), 4.)\nclose(compiled(jnp.float64(-2.)), 2.)",
                    "Keep branch output structures compatible.",
                ),
            ),
            (
                case(
                    "Differentiate the initial carry",
                    "Differentiate the final scan output with respect to initial state.",
                    "1/8 for three steps.",
                    "Each transition multiplies the incoming initial-state sensitivity by one half.",
                    "values = jnp.array([2., 2., 2.])\nclose(jax.grad(lambda h: recurrence(h, values)[0])(0.), .125)",
                    "Compose the three local derivatives.",
                ),
                case(
                    "Differentiate sequence inputs",
                    "Differentiate the final output with respect to the three input values.",
                    "[1/4,1/2,1].",
                    "The last input reaches the output directly; earlier ones pass through later transitions.",
                    "close(jax.grad(lambda values: recurrence(jnp.float64(0.), values)[0])(jnp.array([2., 2., 2.])), [.25, .5, 1.])",
                    "Count the transitions after each input enters.",
                ),
                case(
                    "Handle an empty scan",
                    "Run the recurrence on an empty input vector with initial state five.",
                    "Final five and a length-zero history.",
                    "No transition executes, so the identity of the empty computation is its initial carry.",
                    "last, history = recurrence(jnp.float64(5.), jnp.array([], dtype=jnp.float64))\nclose(last, 5.)\nassert history.shape == (0,)",
                    "The empty sequence does not imply a zero state.",
                ),
                case(
                    "Use a fixed-index loop",
                    "Accumulate the first four nonnegative integers with fori_loop.",
                    "6.",
                    "The loop runs indices zero through three and retains one scalar carry.",
                    "result = jax.lax.fori_loop(0, 4, lambda i, total: total + i, jnp.int64(0))\nassert int(result) == 6",
                    "Check whether the upper bound is included.",
                ),
                case(
                    "Inspect a dynamic stopping rule",
                    "Double a positive scalar until it is at least ten; calculate its local JVP at one.",
                    "Output 16, forward sensitivity 16 under this local four-step path.",
                    "The stopping count is stable in a neighborhood of the chosen point. This does not imply differentiability at every threshold boundary.",
                    "def double_until(value):\n    return jax.lax.while_loop(lambda z: z < 10., lambda z: 2. * z, value)\nvalue, tangent = jax.jvp(double_until, (jnp.float64(1.),), (jnp.float64(1.),))\nclose(value, 16.)\nclose(tangent, 16.)",
                    "Separate the local path from a global smoothness claim.",
                ),
                case(
                    "Transfer to a batched state",
                    "Run the same recurrence with a two-coordinate carry and two input rows.",
                    "Final [2,4] from inputs [[2,4],[1,2]].",
                    "The carry can be an array as long as its shape remains unchanged across steps.",
                    "last, history = recurrence(jnp.zeros(2), jnp.array([[2., 4.], [1., 2.]]))\nclose(last, [2., 4.])\nassert history.shape == (2, 2)",
                    "Keep time and feature axes distinct.",
                ),
            ),
            "For a carry error, compare shape, dtype and tree structure before and after one transition. For a gradient failure, identify the primitive and the differentiation mode. A branch that changes output shape needs a different representation or explicit static configuration.",
            "Write a fixed-step simulation transition and explain how a runtime stopping criterion changes its numerical and derivative contract. Connect the difference to solver tolerance and discretization error rather than treating all loops as interchangeable syntax.",
            (("Control flow", "https://docs.jax.dev/en/latest/control-flow.html"),),
        ),
        Unit(
            12,
            "Vectorization, per-example gradients and axis meaning",
            "intermediate",
            (11,),
            ("vmap", "mapped axis", "shared argument", "per-example gradient"),
            "Vectorize a scalar example computation while preserving shared parameters, sample identity and the chosen gradient reduction.",
            r"""A function that predicts one observation can be transformed to predict a batch. vmap introduces a mapped axis around the function. It does not require rewriting the function as a Python loop, and it does not automatically mean execution on several devices. The mapped axis is a computational batching contract.

The in_axes specification identifies which arguments vary across examples. A parameter vector shared by the whole batch should normally be unmapped, while the observation matrix is mapped along its row axis. Mapping the parameters too would describe a collection of different models, not one model applied to several observations. Both operations can be valid, so state the intended experiment explicitly.

Per-example gradients make this distinction concrete. Differentiate a one-example loss, then vmap that gradient over observations. The result retains one gradient vector per example. Differentiating the mean batch loss instead returns their mean under this separable equally weighted objective. The equality can fail when the objective couples examples, such as an in-batch contrastive denominator, or when different weights are used.

Vectorization can also be nested. One axis might enumerate observations while another enumerates candidate parameter vectors. Draw the resulting axes before coding. Equal dimensions can conceal a wrong mapping, so test with two observations, three candidates or other deliberately unequal sizes.

A transformed batch can consume substantial memory because it retains results for all mapped examples. This is especially relevant for per-example gradients. Correctly vectorizing a function does not prove the chosen batch size is efficient or feasible. Later performance lessons compare completed work and resource behavior while keeping the numerical objective fixed.""",
            r"""Let \(\widehat y=w^{\mathsf T}x\) and \(\ell(w,x,y)=(w^{\mathsf T}x-y)^2\). Then \(\nabla_w\ell=2(w^{\mathsf T}x-y)x\). For rows \([1,2]\), \([3,4]\), targets \([1,2]\), and \(w=0\), the individual gradients are \([-2,-4]\) and \([-12,-16]\). Their mean is \([-7,-10]\). This is the gradient of the mean because differentiation and a finite weighted sum commute for this stated separable objective.""",
            """def predict_one(weight, features):
    return jnp.vdot(weight, features)


def loss_one(weight, features, target):
    return (predict_one(weight, features) - target) ** 2

features = jnp.array([[1., 2.], [3., 4.]])
targets = jnp.array([1., 2.])""",
            (
                case(
                    "Share one model across rows",
                    "Map predict_one over feature rows with weight [2,-1] shared.",
                    "Predictions [0,2].",
                    "in_axes=(None,0) says that the first argument is shared and the second is mapped along rows.",
                    "predict_batch = jax.vmap(predict_one, in_axes=(None, 0))\nclose(predict_batch(jnp.array([2., -1.]), features), [0., 2.])",
                    "Label argument roles before assigning axes.",
                ),
                case(
                    "Retain per-example derivatives",
                    "Map grad(loss_one) over features and targets at zero weight.",
                    "Gradient matrix [[-2,-4],[-12,-16]].",
                    "The first axis identifies examples; the second identifies parameter coordinates. Reducing the first axis produces a different object with a different purpose.",
                    "per_example = jax.vmap(jax.grad(loss_one), in_axes=(None, 0, 0))\nclose(per_example(jnp.zeros(2), features, targets), [[-2., -4.], [-12., -16.]])",
                    "Derive each row before averaging.",
                ),
            ),
            (
                case(
                    "Compare with a literal loop",
                    "Evaluate the shared predictor by a Python list of calls and by vmap.",
                    "The same [0,2] values.",
                    "The loop supplies a transparent oracle for this tiny batch; it is not a performance benchmark.",
                    "w = jnp.array([2., -1.])\nloop = jnp.stack([predict_one(w, row) for row in features])\nclose(jax.vmap(predict_one, in_axes=(None, 0))(w, features), loop)",
                    "Keep the same parameter vector in every loop iteration.",
                ),
                case(
                    "Reduce gradients deliberately",
                    "Compare the mean per-example gradient with grad of the mean loss.",
                    "Both [-7,-10].",
                    "The equality depends on the stated separable loss and equal observation weights.",
                    "batch_loss = lambda w: jnp.mean(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))\nclose(jax.grad(batch_loss)(jnp.zeros(2)), [-7., -10.])",
                    "The reduction axis is the example axis.",
                ),
                case(
                    "Change to a sum",
                    "Differentiate the summed batch loss.",
                    "[-14,-20], twice the mean gradient.",
                    "The batch contains two equally weighted observations, so sum and mean differ by two.",
                    "summed = lambda w: jnp.sum(jax.vmap(loss_one, in_axes=(None, 0, 0))(w, features, targets))\nclose(jax.grad(summed)(jnp.zeros(2)), [-14., -20.])",
                    "Retain the active count.",
                ),
                case(
                    "Map several models",
                    "Apply weights [[1,0],[0,1],[1,1]] separately to feature [2,3].",
                    "[2,3,5].",
                    "Now the model axis is mapped and the input observation is shared. This answers a different question from a single-model prediction batch.",
                    "weights = jnp.array([[1., 0.], [0., 1.], [1., 1.]])\nclose(jax.vmap(predict_one, in_axes=(0, None))(weights, jnp.array([2., 3.])), [2., 3., 5.])",
                    "Use different axis lengths to expose accidental pairing.",
                ),
                case(
                    "Compose with JIT",
                    "JIT the vectorized predictor and compare the values.",
                    "Same predictions [0,2].",
                    "Vectorization and compilation can compose without changing the requested mathematical mapping.",
                    "compiled = jax.jit(jax.vmap(predict_one, in_axes=(None, 0)))\nclose(compiled(jnp.array([2., -1.]), features), [0., 2.])",
                    "Preserve the shared-parameter axis contract.",
                ),
                case(
                    "Allocate random streams per row",
                    "Split one root into three keys and map a fixed-shape normal draw over them.",
                    "Array shape (3,2); replay with the same key batch agrees.",
                    "The mapped argument is a batch of keys rather than one key implicitly reused for every example.",
                    "keys = jax.random.split(jax.random.key(23), 3)\ndraw = jax.vmap(lambda key: jax.random.normal(key, (2,)))\na, b = draw(keys), draw(keys)\nassert a.shape == (3, 2)\nclose(a, b)",
                    "Map keys in the same order as their associated examples.",
                ),
            ),
            "When a vectorized result is wrong, write the unmapped function signature, every in_axes entry and the expected output axes. When a gradient comparison differs, check whether the objective couples examples or uses a different reduction before blaming vmap.",
            "Design a two-axis comparison of candidate parameter vectors and observations. Explain why vmap alone does not establish multi-device parallelism, and estimate the memory cost of retaining a gradient for every example in a larger model.",
            (("vmap", "https://docs.jax.dev/en/latest/_autosummary/jax.vmap.html"),),
        ),
    ]
)

UNITS.extend(
    [
        Unit(
            13,
            "Stable categorical losses and active-target masks",
            "intermediate",
            (12,),
            ("logits", "log-softmax", "target mask", "active denominator"),
            "Compute a stable masked categorical objective and verify its value and direct logit gradients.",
            r"""A categorical model emits one score for each candidate. These logits are not probabilities. Softmax normalizes them, while log-softmax computes their normalized logarithms in a stable form. A target index selects the event whose assigned log probability is scored. The loss therefore depends on candidate identity, not just a sorted list of scores.

A mask selects which target events contribute to the objective. Its denominator must count the same events as its numerator. Padding adds storage positions without adding observations. Dividing by padded width makes the reported mean and every gradient depend on padding density. A lower number produced that way is not better prediction.

Ignoring a label does not erase its input representation from a complete model. An attention mask controls information access; a loss mask controls direct supervision. This unit supplies literal logits, so it isolates the loss and direct logit derivatives without claiming to test a whole decoder's attention or embedding paths.

Admission is deliberately separate from the transformed numerical function. Host-side checks confirm shape, at least one active target and legal active class indices. The pure loss then replaces ignored sentinel indices with a safe gather index before selecting log probabilities. A masked invalid index should not be used in a gather and only discarded afterward.

Uniform logits make an exact baseline: every class has equal probability. That is useful for checking the active count, but it can hide target permutations because every target has the same loss. Also retain a nonuniform example whose correct class identity matters. The combination of value, active count and per-row gradients supplies stronger evidence than a single mean.""",
            r"""With C classes and active indicators \(m_i\), define \(L=-\frac{\sum_i m_i\log p_i(y_i)}{\sum_i m_i}\). For N active targets, the derivative of an active logit is \((p_{ij}-\mathbf1_{\{j=y_i\}})/N\). At uniform three-class probabilities and three active targets, true-class coordinates have derivative \(-2/9\), other coordinates \(1/9\), and ignored rows zero. An all-ignored batch has no defined empirical mean.""",
            """def admit(logits, targets, active):
    labels, mask = np.asarray(targets), np.asarray(active)
    if logits.ndim != 2 or labels.shape != (logits.shape[0],) or mask.shape != labels.shape:
        raise ValueError("one target and mask per logit row")
    if mask.dtype != np.bool_ or not mask.any():
        raise ValueError("at least one active Boolean target")
    if np.any(labels[mask] < 0) or np.any(labels[mask] >= logits.shape[1]):
        raise ValueError("active target outside classes")


def token_mean(logits, targets, active):
    safe = jnp.where(active, targets, 0)
    selected = jnp.take_along_axis(jax.nn.log_softmax(logits), safe[:, None], axis=1)[:, 0]
    return -jnp.where(active, selected, 0.).sum() / active.sum()

logits = jnp.zeros((4, 3))
targets = jnp.array([0, 1, 2, -100])
active = jnp.array([True, True, True, False])""",
            (
                case(
                    "Uniform active-target accounting",
                    "Admit the fixture and compute its mean loss.",
                    "log(3), with three active targets.",
                    "The ignored row contributes neither negative log probability nor denominator count.",
                    "admit(logits, targets, active)\nassert int(active.sum()) == 3\nclose(token_mean(logits, targets, active), math.log(3.))",
                    "Count selected events rather than stored rows.",
                ),
                case(
                    "Inspect direct gradients",
                    "Differentiate the loss with respect to every logit.",
                    "Diagonal true-class entries -2/9, other active entries 1/9, ignored row all zero.",
                    "This exposes supervision identity even when uniform logits give equal losses for every target.",
                    "g = jax.grad(token_mean)(logits, targets, active)\nexpected = np.full((4, 3), 1 / 9)\nexpected[np.arange(3), np.arange(3)] = -2 / 9\nexpected[3] = 0.\nclose(g, expected)",
                    "Derive one row, then apply the active mean count.",
                ),
            ),
            (
                case(
                    "Append ignored storage",
                    "Append two ignored rows and show that the objective stays the same.",
                    "Still log(3).",
                    "Padding is not evidence and does not change the active count.",
                    "padded = jnp.zeros((6, 3))\nlabels = jnp.array([0, 1, 2, -100, -100, -100])\nmask = jnp.array([True, True, True, False, False, False])\nadmit(padded, labels, mask)\nclose(token_mean(padded, labels, mask), math.log(3.))",
                    "Extend labels and masks together.",
                ),
                case(
                    "Reject an empty objective",
                    "Admit a mask with no active targets.",
                    "ValueError before loss reduction.",
                    "A zero denominator cannot be reinterpreted as perfect prediction.",
                    "try:\n    admit(logits, targets, jnp.zeros(4, dtype=bool))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('empty supervision accepted')",
                    "State the no-target policy explicitly.",
                ),
                case(
                    "Check target identity",
                    "Use logits [log(3),0] and compare targets zero and one.",
                    "Losses log(4/3) and log(4).",
                    "A nonuniform row detects a target swap that the uniform fixture could hide.",
                    "scores = jnp.array([[math.log(3.), 0.]])\nmask = jnp.array([True])\nclose(token_mean(scores, jnp.array([0]), mask), math.log(4 / 3))\nclose(token_mean(scores, jnp.array([1]), mask), math.log(4.))",
                    "Normalize the masses [3,1].",
                ),
                case(
                    "Keep an extreme logit finite",
                    "Score target zero for logits [1000,0,-1000].",
                    "Finite loss near zero.",
                    "Stable log-softmax avoids an unnecessary exponential overflow.",
                    "value = token_mean(jnp.array([[1000., 0., -1000.]]), jnp.array([0]), jnp.array([True]))\nassert bool(jnp.isfinite(value))\nclose(value, 0.)",
                    "Use normalized log probabilities directly.",
                ),
                case(
                    "Reject an active sentinel",
                    "Mark the -100 target active and apply admission.",
                    "ValueError.",
                    "The sentinel is only permitted outside the supervised target set.",
                    "try:\n    admit(logits, targets, jnp.ones(4, dtype=bool))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('active sentinel accepted')",
                    "Validate only the selected target domain, but validate it strictly.",
                ),
                case(
                    "Compile the admitted calculation",
                    "JIT token_mean on the admitted fixture and compare with the eager objective.",
                    "Same log(3) value.",
                    "The host admission check and pure numerical loss have distinct execution roles.",
                    "admit(logits, targets, active)\nclose(jax.jit(token_mean)(logits, targets, active), math.log(3.))",
                    "Do not move NumPy host validation blindly inside JIT.",
                ),
            ),
            "A suspiciously small loss can come from a wrong denominator, wrong class axis or masking after an invalid operation. Inspect active target identities and direct gradients. The host admission function is intentionally not a transformed numerical kernel.",
            "Map this objective to shifted next-token labels in llm-017 and llm-031. Explain why excluding prompt targets does not imply zero gradient through all prompt representations in a full causal model.",
            (("JAX neural-network functions", "https://docs.jax.dev/en/latest/jax.nn.html"),),
        ),
        Unit(
            14,
            "Optimizer updates are explicit state transitions",
            "intermediate",
            (13,),
            ("SGD", "momentum", "Adam", "optimizer state", "bias correction"),
            "Implement and audit scalar optimizer transitions while distinguishing parameters from the state determining their next update.",
            r"""A gradient tells an optimizer about the current objective's local sensitivity. The optimizer combines that information with a learning rate and, for stateful methods, its history. Two runs with identical parameters and current gradients can therefore take different next steps if their optimizer states differ.

Start with SGD: subtract the chosen rate times the gradient. Momentum retains a velocity-like accumulated quantity, so the next update also depends on earlier gradients. Adam retains first and second moments plus a step count. Its second moment is an average of squared gradients, not a centered sample variance. Bias correction depends on the number of updates that have actually occurred.

In JAX, these quantities can be explicit returned values. A function receives parameters, optimizer state and gradients, then returns updated parameters and state. The caller must keep the returned state. Reusing the original zero moments on every step implements a different algorithm, even if the function is named Adam.

The tiny scalar examples below deliberately avoid an optimizer package so the arithmetic is visible. That is not a recommendation to maintain a production optimizer from scratch. Once the mechanism is understood, a separately prepared library can supply tested transformations and additional policies. Its package version and state contract must still be explicit.

Weight decay, clipping, schedules and gradient accumulation introduce additional choices. Do not assume that clipping a gradient bounds the complete displacement of every stateful optimizer. Likewise, a scheduler counter belongs in a continuation contract if it influences the next learning rate. This unit checks one exact update rule and its state transitions, not a universal convergence claim.""",
            r"""Momentum here uses \(v_t=0.9v_{t-1}+g_t\) and \(w_t=w_{t-1}-\eta v_t\). Adam uses \(m_t=\beta_1m_{t-1}+(1-\beta_1)g_t\), \(v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2\), with corrections \(\widehat m_t=m_t/(1-\beta_1^t)\) and \(\widehat v_t=v_t/(1-\beta_2^t)\). The update is \(w_t=w_{t-1}-\eta\widehat m_t/(\sqrt{\widehat v_t}+\epsilon)\). Each denominator is a complete expression; the exponent belongs to beta with its subscript.""",
            """def momentum_step(weight, velocity, gradient, rate=.1):
    new_velocity = .9 * velocity + gradient
    return weight - rate * new_velocity, new_velocity


def adam_step(weight, state, gradient, rate=.1):
    mean, square, step = state
    step = step + 1
    mean = .9 * mean + .1 * gradient
    square = .999 * square + .001 * gradient * gradient
    corrected_mean = mean / (1 - .9 ** step)
    corrected_square = square / (1 - .999 ** step)
    updated = weight - rate * corrected_mean / (jnp.sqrt(corrected_square) + 1e-8)
    return updated, (mean, square, step)

zero_state = (jnp.float64(0.), jnp.float64(0.), jnp.int64(0))""",
            (
                case(
                    "Momentum remembers",
                    "Apply gradient two at weight zero with velocity zero, then velocity one.",
                    "Weights -0.2 and -0.29.",
                    "The current gradient and weight are identical, while the saved velocity changes the next update.",
                    "fresh, v0 = momentum_step(0., 0., 2.)\ncontinued, v1 = momentum_step(0., 1., 2.)\nclose(fresh, -.2)\nclose(continued, -.29)\nclose(v1, 2.9)",
                    "Compute velocity before changing weight.",
                ),
                case(
                    "Audit Adam's first correction",
                    "Apply gradient two from zero moments and step zero.",
                    "Moments 0.2 and 0.004; step one; weight -0.2/(2+1e-8).",
                    "Dividing by 1-beta at the first step reconstructs gradient two and squared gradient four before the parameter update.",
                    "weight, state = adam_step(0., zero_state, 2.)\nclose(state[0], .2)\nclose(state[1], .004)\nassert int(state[2]) == 1\nclose(weight, -.2 / (2. + 1e-8))",
                    "Do not confuse the raw and bias-corrected moments.",
                ),
            ),
            (
                case(
                    "Trace plain SGD",
                    "Update w=1 with gradient three and rate 0.2.",
                    "0.4.",
                    "Plain SGD uses no history in this defined rule.",
                    "close(1. - .2 * jnp.float64(3.), .4)",
                    "Subtract, rather than add, the gradient step.",
                ),
                case(
                    "Continue momentum",
                    "Apply gradient two twice from weight and velocity zero.",
                    "First weight -0.2; second -0.58; final velocity 3.8.",
                    "The second velocity includes 90 percent of the first plus the new gradient.",
                    "w, v = momentum_step(0., 0., 2.)\nw, v = momentum_step(w, v, 2.)\nclose(w, -.58)\nclose(v, 3.8)",
                    "Feed both returned values into the next transition.",
                ),
                case(
                    "Continue Adam's counter",
                    "Apply the same gradient twice while retaining Adam state.",
                    "Step two; weight approximately -0.2.",
                    "For this constant gradient, corrected moments remain two and four on both steps.",
                    "w, s = adam_step(0., zero_state, 2.)\nw, s = adam_step(w, s, 2.)\nassert int(s[2]) == 2\nclose(w, -2 * .2 / (2. + 1e-8))",
                    "A counter reset changes the bias correction.",
                ),
                case(
                    "Preserve zero-gradient history",
                    "After one positive gradient, apply a zero gradient with retained Adam state.",
                    "The parameter still moves because the first moment retains history.",
                    "Zero current gradient is not equivalent to a fresh optimizer or no update.",
                    "w, s = adam_step(0., zero_state, 2.)\nnext_w, next_s = adam_step(w, s, 0.)\nassert float(next_w) < float(w)\nassert int(next_s[2]) == 2",
                    "Inspect retained moments before predicting displacement.",
                ),
                case(
                    "Compile the transition",
                    "JIT adam_step and compare its first update with eager execution.",
                    "Equal parameter and state leaves.",
                    "Pure state transitions compose with compilation when their structures and operations are supported.",
                    "a, sa = adam_step(0., zero_state, 2.)\nb, sb = jax.jit(adam_step)(0., zero_state, 2.)\nclose(a, b)\nfor x, y in zip(sa, sb):\n    close(x, y)",
                    "Compare all state, not only the displayed weight.",
                ),
                case(
                    "Reverse the gradient",
                    "Apply gradient minus two from zero state.",
                    "A positive parameter update of 0.2/(2+1e-8).",
                    "The first moment changes sign while the squared moment does not.",
                    "w, s = adam_step(0., zero_state, -2.)\nclose(w, .2 / (2. + 1e-8))\nclose(s[0], -.2)\nclose(s[1], .004)",
                    "Separate sign-sensitive and squared state.",
                ),
            ),
            "If continued training differs, compare parameters, moments, step count, learning-rate policy and the actual next batch/key. An optimizer name is not proof that returned state was retained. Match epsilon placement and reduction before comparing frameworks.",
            "Describe the minimum state needed to reproduce one next update under this Adam rule. Explain what changes if dropout, a scheduler or data shuffling is introduced, then connect those additions to the later continuation capstone.",
            (
                (
                    "JAX training cookbook",
                    "https://docs.jax.dev/en/latest/the-training-cookbook.html",
                ),
                ("Adam paper", "https://arxiv.org/abs/1412.6980"),
            ),
        ),
    ]
)

UNITS.extend(
    [
        Unit(
            15,
            "Train a small neural network with visible parameters",
            "intermediate",
            (14,),
            ("MLP", "initialization", "training loop", "held-out evaluation"),
            "Assemble a bounded neural training experiment and distinguish optimization progress from evidence about new observations.",
            r"""A multilayer perceptron combines affine maps with nonlinear functions. The nonlinearity matters: composing only affine maps still produces an affine map. Here a hidden tanh layer receives one feature, produces four hidden coordinates, then an output projection returns one prediction. Every weight and bias is visible in a pytree.

Initialization is part of the experiment. We split a key for the two weight matrices and use small random values, with zero biases. Reusing a key would tie random construction unintentionally. Repeating initialization with the same complete policy supports replay in the pinned environment, but does not make different random seeds irrelevant to a scientific comparison.

The training step computes a scalar mean loss, differentiates it with respect to the parameter tree and returns updated parameters. A short Python loop repeatedly calls the compiled step. Data stays literal and small; no model download or opaque trainer is required. The reported final loss is computed after the final update.

The target rule in this fixture is tanh(2x). Training points and held-out interpolation points are listed separately. Their numerical relationship is deliberately simple, making the experiment auditable. A reduced training loss shows that the optimization path addressed the authored objective. A held-out error adds a separate observation on the listed points, but those few values do not establish broad population reliability.

Failure diagnosis should proceed from input shape to forward values, loss reduction, gradient tree, update state and fresh evaluation. Increasing model width or training steps before checking those contracts can hide a basic defect. Later capstones ask for a defensible comparison, not just a longer loop that happens to print a smaller number.""",
            r"""For row inputs \(X\in\mathbb R^{N\times1}\), compute \(H=\tanh(XW_1+b_1)\) with \(W_1\in\mathbb R^{1\times4}\), then \(\widehat Y=HW_2+b_2\) with \(W_2\in\mathbb R^{4\times1}\). The model contains 4+4+4+1=13 parameters. Its mean loss reduces N scalar prediction events. The gradient tree must have the same structure and leaf shapes as those 13 parameters.""",
            """def initialize(key):
    first, second = jax.random.split(key)
    return {
        "w1": .3 * jax.random.normal(first, (1, 4), dtype=jnp.float64),
        "b1": jnp.zeros(4),
        "w2": .3 * jax.random.normal(second, (4, 1), dtype=jnp.float64),
        "b2": jnp.zeros(1),
    }


def forward(parameters, inputs):
    hidden = jnp.tanh(inputs @ parameters["w1"] + parameters["b1"])
    return hidden @ parameters["w2"] + parameters["b2"]


def objective(parameters, inputs, labels):
    return jnp.mean((forward(parameters, inputs) - labels) ** 2)


def step(parameters, inputs, labels):
    gradients = jax.grad(objective)(parameters, inputs, labels)
    return jax.tree.map(lambda p, g: p - .05 * g, parameters, gradients)

compiled_step = jax.jit(step)
train_x = jnp.array([[-1.], [-.5], [0.], [.5], [1.]])
train_y = jnp.tanh(2 * train_x)
heldout_x = jnp.array([[-.75], [.75]])
heldout_y = jnp.tanh(2 * heldout_x)


def train():
    parameters = initialize(jax.random.key(31))
    for _ in range(120):
        parameters = compiled_step(parameters, train_x, train_y)
    return parameters""",
            (
                case(
                    "Trace the architecture",
                    "Initialize the model and inspect parameter count and output shape.",
                    "13 parameters; predictions shape (5,1), all finite.",
                    "The final singleton is an output-feature axis. It must match the target shape exactly before calculating the loss.",
                    "parameters = initialize(jax.random.key(31))\nassert sum(x.size for x in jax.tree.leaves(parameters)) == 13\npredictions = forward(parameters, train_x)\nassert predictions.shape == train_y.shape == (5, 1)\nassert bool(jnp.isfinite(predictions).all())",
                    "Write both affine-map shapes before multiplying.",
                ),
                case(
                    "A bounded optimization observation",
                    "Train for exactly 120 updates from the fixed initialization and recompute the loss.",
                    "Finite final training loss smaller than its initial value.",
                    "The assertion concerns this deterministic optimization fixture. Held-out evaluation and scientific interpretation remain separate observations.",
                    "initial = initialize(jax.random.key(31))\ntrained = train()\nbefore = objective(initial, train_x, train_y)\nafter = objective(trained, train_x, train_y)\nassert bool(jnp.isfinite(after))\nassert float(after) < float(before)",
                    "Evaluate the final parameters rather than retaining a stale pre-update scalar.",
                ),
            ),
            (
                case(
                    "Replay initialization",
                    "Initialize twice from the same key and compare every leaf.",
                    "Matching tree structure and values.",
                    "The complete deterministic initialization policy, not only a label called seed, establishes this replay.",
                    "a = initialize(jax.random.key(31))\nb = initialize(jax.random.key(31))\nfor x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):\n    close(x, y)",
                    "Compare all weights and biases.",
                ),
                case(
                    "Inspect gradients",
                    "Differentiate the training objective at initialization.",
                    "Matching parameter/gradient structures and shapes; finite gradients with nonzero total norm.",
                    "A particular zero bias gradient can be a symmetry of this data rather than a disconnected graph.",
                    "p = initialize(jax.random.key(31))\ng = jax.grad(objective)(p, train_x, train_y)\nassert jax.tree.structure(p) == jax.tree.structure(g)\nfor a, b in zip(jax.tree.leaves(p), jax.tree.leaves(g)):\n    assert a.shape == b.shape\n    assert bool(jnp.isfinite(b).all())\nassert sum(float(jnp.vdot(x, x)) for x in jax.tree.leaves(g)) > 0.",
                    "Inspect the aggregate norm without requiring every coordinate to be nonzero.",
                ),
                case(
                    "Check one compiled update",
                    "Compare one eager step and one compiled step from identical state.",
                    "Matching updated leaves.",
                    "This is a compilation parity check with the same batch, reduction and learning rate.",
                    "p = initialize(jax.random.key(31))\na, b = step(p, train_x, train_y), compiled_step(p, train_x, train_y)\nfor x, y in zip(jax.tree.leaves(a), jax.tree.leaves(b)):\n    close(x, y)",
                    "Keep the starting state identical.",
                ),
                case(
                    "Evaluate untouched inputs",
                    "Calculate loss at the two held-out interpolation points after the fixed training budget.",
                    "A finite nonnegative held-out loss over exactly two targets.",
                    "The numerical value is an observation to report, not a threshold tuned on these final points.",
                    "p = train()\nvalue = objective(p, heldout_x, heldout_y)\nassert heldout_x.shape[0] == 2\nassert bool(jnp.isfinite(value)) and float(value) >= 0.",
                    "Keep these points out of the update loop.",
                ),
                case(
                    "Separate training from inference",
                    "Run forward twice with the trained parameters and the same inputs.",
                    "Matching deterministic predictions; no parameter update.",
                    "This model has no stochastic or mutable inference state. A later dropout model needs an explicit mode/key policy.",
                    "p = train()\na, b = forward(p, heldout_x), forward(p, heldout_x)\nclose(a, b)",
                    "Calling forward is not an optimizer step.",
                ),
                case(
                    "Check an architecture change",
                    "Explain and verify how adding one hidden coordinate changes the parameter count for this layout.",
                    "Width five would contain 16 parameters, three more than width four.",
                    "Each new hidden unit adds one input weight, one hidden bias and one output weight; the output bias is shared.",
                    "count = lambda width: width + width + width + 1\nassert count(4) == 13 and count(5) == 16",
                    "Count each matrix and bias independently.",
                ),
            ),
            "If training does not improve, inspect an exact one-step state, the objective reduction and the gradient tree before adjusting the budget. If held-out results disappoint, report them without retuning on those same points. Do not confuse the fixed synthetic target rule with an empirical population claim.",
            "Port the one-step calculation to an existing framework route with matched initial arrays. Explain what an optimizer package or model library would add, then design a separate validation split before comparing widths or learning rates.",
            (
                ("Pytrees and MLPs", "https://docs.jax.dev/en/latest/pytrees.html"),
                ("Training cookbook", "https://docs.jax.dev/en/latest/the-training-cookbook.html"),
            ),
        ),
        Unit(
            16,
            "Dropout, evaluation and stochastic objective contracts",
            "intermediate",
            (15,),
            ("dropout", "training mode", "evaluation", "random-key ownership"),
            "Implement an explicit stochastic training transform and show why evaluation and replay require a declared mode/key policy.",
            r"""Dropout changes a training computation by randomly suppressing some activations. In the inverted convention used here, retained activations are divided by the keep probability. This preserves their expectation for a fixed input under the stated Bernoulli sampling model. It does not mean every sampled output equals the original input.

Evaluation uses the deterministic identity in this convention. The training flag is therefore part of the function's contract. An enclosing object named model or a variable named eval does not automatically change a separately written helper. Pass the policy explicitly and decide which values are static configuration when compiling it.

Random-key ownership remains essential. Replaying with the same key reproduces the same mask, which is useful for debugging and controlled comparisons. Continuing training with the same key every step, however, reuses masks when new randomness was intended. Split the key at the state boundary and retain the next key with the rest of training state.

The expected-value statement and an observed finite sample are different evidence. A large literal array of ones lets us inspect a sample mean, but that one sample does not prove unbiasedness. Derive the expectation independently, then use the sample as a bounded mechanism check. For a differentiable computation conditional on a fixed sampled mask, the derivative follows that fixed mask's scaling; differentiation does not turn the discrete sampling step into a continuously differentiable draw.

This unit does not train a model to establish that dropout improves generalization. Such a claim needs a controlled study with held-out tasks, matched budgets and a defined uncertainty analysis. The local exercise establishes mode behavior, key flow and scaling so that a later study can be interpreted.""",
            r"""For keep probability \(q\in(0,1]\), sample \(m_i\sim\operatorname{Bernoulli}(q)\) and return \(z_i=m_ix_i/q\) in training. Since \(\mathbb E[m_i]=q\), \(\mathbb E[z_i]=x_i\). Conditional on a fixed mask, \(\partial z_i/\partial x_i=m_i/q\). Evaluation returns \(z_i=x_i\). The boundary q=0 is undefined for this scaling and must be rejected before execution.""",
            """def validate_keep(keep):
    if not math.isfinite(keep) or not 0. < keep <= 1.:
        raise ValueError("keep probability must be in (0,1]")


def dropout(values, key, *, training, keep=.5):
    if not training:
        return values
    mask = jax.random.bernoulli(key, keep, values.shape)
    return jnp.where(mask, values / keep, 0.)

values = jnp.ones(16)
key = jax.random.key(41)""",
            (
                case(
                    "Inspect a training mask",
                    "Apply training dropout with keep probability one half to ones.",
                    "Every output is either zero or two.",
                    "The inverse keep factor applies only to retained values; the realized mean need not equal one for 16 draws.",
                    "validate_keep(.5)\nresult = dropout(values, key, training=True, keep=.5)\nassert bool(jnp.all((result == 0.) | (result == 2.)))",
                    "Separate support of a draw from its expected mean.",
                ),
                case(
                    "Evaluation is explicit",
                    "Apply the same helper with training false and two different keys.",
                    "Both outputs equal the input exactly.",
                    "The evaluation branch ignores random sampling under this convention.",
                    "close(dropout(values, key, training=False), values)\nclose(dropout(values, jax.random.key(99), training=False), values)",
                    "Name the convention before deciding evaluation behavior.",
                ),
            ),
            (
                case(
                    "Replay a mask",
                    "Use the same key twice in training mode.",
                    "Identical outputs.",
                    "Determinism supports debugging but is not independent fresh sampling.",
                    "a = dropout(values, key, training=True)\nb = dropout(values, key, training=True)\nclose(a, b)",
                    "A random function does not mutate its key.",
                ),
                case(
                    "Keep every activation",
                    "Use keep probability one in training mode.",
                    "Output equals input.",
                    "The Bernoulli mask is all true and the scale is one.",
                    "validate_keep(1.)\nclose(dropout(values, key, training=True, keep=1.), values)",
                    "Check a mathematically defined boundary.",
                ),
                case(
                    "Reject zero keep probability",
                    "Validate q=0 before the transform.",
                    "ValueError.",
                    "Division by zero is not a usable all-dropped training policy under this contract.",
                    "try:\n    validate_keep(0.)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('zero keep accepted')",
                    "Validate configuration before tracing numerical work.",
                ),
                case(
                    "Differentiate with a fixed mask",
                    "Differentiate the sum of dropped activations with respect to the input.",
                    "Gradient coordinates equal the zero-or-two mask scaling.",
                    "The derivative is conditional on the supplied key's sampled mask; no derivative of the discrete key is requested.",
                    "g = jax.grad(lambda x: dropout(x, key, training=True).sum())(values)\nclose(g, dropout(values, key, training=True))",
                    "Use the same key in the independent mask oracle.",
                ),
                case(
                    "Compile the mode policy",
                    "JIT the helper with training and keep static, then test evaluation.",
                    "Deterministic identity output.",
                    "These are a small configuration set rather than per-element changing data.",
                    "compiled = jax.jit(dropout, static_argnames=('training', 'keep'))\nclose(compiled(values, key, training=False, keep=.5), values)",
                    "A Python if needs a deliberate static mode or structured control flow.",
                ),
                case(
                    "Inspect a larger sample without a universal claim",
                    "Drop a length-4096 vector of ones with the pinned key and report its mean.",
                    "Finite mean between zero and two; every entry obeys the mask support.",
                    "The interval follows the output support. The expectation one is established algebraically, not guaranteed for this finite sample.",
                    "result = dropout(jnp.ones(4096), key, training=True)\nmean = float(result.mean())\nassert 0. <= mean <= 2.\nassert bool(jnp.all((result == 0.) | (result == 2.)))",
                    "Do not tune a statistical tolerance merely to make one seed pass.",
                ),
            ),
            "If evaluation changes with a random key, inspect the explicit mode path. If training repeats masks, inspect returned-key ownership. A fixed-mask gradient can be correct even though the random sampling operation itself is discrete.",
            "Design a fair dropout comparison using a separate validation set and preserved key/state policy. Explain what additional evidence would support a generalization claim beyond the exact mask/scaling checks here.",
            (
                ("Random numbers", "https://docs.jax.dev/en/latest/random-numbers.html"),
                (
                    "Stateful computations",
                    "https://docs.jax.dev/en/latest/stateful-computations.html",
                ),
            ),
        ),
    ]
)

UNITS.extend(
    [
        Unit(
            17,
            "Continuation requires parameters, history and keys",
            "intermediate",
            (16,),
            ("checkpoint", "optimizer history", "random state", "next-step parity"),
            "Define and verify a bounded continuation contract that preserves every state component used by the next update.",
            r"""A checkpoint should be specified by the continuation it promises. An inference snapshot may need parameters and preprocessing. A training continuation can also require optimizer moments, step count, random keys, scheduler state and data position. Matching today's prediction is weaker than reproducing the next update.

This lesson uses a scalar momentum update with a small random perturbation of its gradient. Its state is weight, velocity, typed random key and update count. We advance the state before saving, so history and key progression are nontrivial. A weights-only snapshot would omit two mechanisms that influence the next step.

Serialization is a boundary between numerical objects and durable representation. NumPy arrays in an npz file store the scalar values and key data without requiring object pickles. The key algorithm is explicitly fixed for this fixture, so reconstruction does not silently reinterpret raw key words under a different algorithm. A real artifact also needs versions, shapes, dtype, model construction and the relevant data contract.

The ordinary classroom worker owns a temporary directory that is removed after each Run. Saving a small file within one Run demonstrates a local save/read transition; it does not create a durable learner checkpoint available to a later Run. Source, notes and result receipts have their own supported persistence channels. A production checkpoint workflow needs an explicitly prepared artifact location and lifecycle.

Compare an uninterrupted next state with one computed after reconstruction. Then deliberately omit velocity while keeping the same key, so the negative control isolates optimizer history rather than changing several causes at once. This evidence establishes the stated scalar continuation, not a distributed data loader, cross-version bitwise portability or a large-model storage system.""",
            r"""The transition draws noise \(\xi_t\) from its current key, forms \(g_t=2(w_t-2)+0.01\xi_t\), updates \(v_{t+1}=0.9v_t+g_t\) and \(w_{t+1}=w_t-0.1v_{t+1}\), and returns the next key and count. Reconstructing only w generally changes the next result because v and the next draw also appear in these equations. Equal keys isolate the missing-velocity comparison.""",
            """import tempfile
from pathlib import Path


def next_state(state):
    weight, velocity, key, count = state
    next_key, draw_key = jax.random.split(key)
    noise = jax.random.normal(draw_key, (), dtype=jnp.float64)
    gradient = 2. * (weight - 2.) + .01 * noise
    velocity = .9 * velocity + gradient
    return weight - .1 * velocity, velocity, next_key, count + 1


def prepared_state():
    state = (jnp.float64(0.), jnp.float64(0.), jax.random.key(52, impl="threefry2x32"), jnp.int64(0))
    return next_state(next_state(state))


def save_state(path, state):
    w, v, key, count = state
    np.savez(path, weight=np.asarray(w), velocity=np.asarray(v), key=np.asarray(jax.random.key_data(key)), count=np.asarray(count))


def load_state(path):
    with np.load(path, allow_pickle=False) as saved:
        return (jnp.asarray(saved['weight']), jnp.asarray(saved['velocity']),
                jax.random.wrap_key_data(jnp.asarray(saved['key']), impl="threefry2x32"),
                jnp.asarray(saved['count']))


def compare(left, right):
    close(left[0], right[0])
    close(left[1], right[1])
    assert np.array_equal(np.asarray(jax.random.key_data(left[2])), np.asarray(jax.random.key_data(right[2])))
    assert int(left[3]) == int(right[3])""",
            (
                case(
                    "Reconstruct the next transition",
                    "Save the two-step state to an owned temporary file, load it and compare the next update with uninterrupted continuation.",
                    "Matching next weight, velocity, key data and step count three.",
                    "The check inspects all state used by the actual transition, not only current predictions or one serialized array.",
                    "state = prepared_state()\nwith tempfile.TemporaryDirectory() as directory:\n    path = Path(directory) / 'state.npz'\n    save_state(path, state)\n    restored = load_state(path)\n    compare(next_state(state), next_state(restored))\n    assert int(next_state(restored)[3]) == 3",
                    "Compare next states after identical transitions.",
                ),
                case(
                    "Omit history deliberately",
                    "Keep the saved weight and key but reset velocity to zero before the next step.",
                    "A different next weight.",
                    "Using the same key holds the next random perturbation fixed, so the difference identifies missing momentum history.",
                    "state = prepared_state()\nwrong = (state[0], jnp.float64(0.), state[2], state[3])\nassert not np.isclose(float(next_state(state)[0]), float(next_state(wrong)[0]))",
                    "Change only the state component being diagnosed.",
                ),
            ),
            (
                case(
                    "Check a nontrivial checkpoint",
                    "Inspect the prepared state's update count and velocity.",
                    "Count two and nonzero velocity.",
                    "Saving before any update would not exercise retained history.",
                    "state = prepared_state()\nassert int(state[3]) == 2\nassert float(state[1]) != 0.",
                    "Use a state after actual transitions.",
                ),
                case(
                    "Replay from the same root",
                    "Construct the two-step state twice from the same root key.",
                    "Every state component agrees.",
                    "The transition and initialization policy are deterministic in this pinned environment.",
                    "compare(prepared_state(), prepared_state())",
                    "Compare key data as well as numerical values.",
                ),
                case(
                    "Validate serialization values",
                    "Save and load once without taking another step.",
                    "Matching reconstructed state and scalar dtypes/shapes.",
                    "This isolates representation correctness from continuation arithmetic.",
                    "state = prepared_state()\nwith tempfile.TemporaryDirectory() as directory:\n    path = Path(directory) / 'state.npz'\n    save_state(path, state)\n    restored = load_state(path)\n    compare(state, restored)\n    assert restored[0].shape == () and restored[0].dtype == jnp.float64",
                    "Avoid object-pickle dependence for this numerical fixture.",
                ),
                case(
                    "Show random-state importance",
                    "Keep weight/velocity/count but replace the key before one update.",
                    "The next key identity differs; the random transition contract has changed.",
                    "A changed stream is a distinct continuation even if two rounded scalar outputs happened to be close.",
                    "state = prepared_state()\nother = (state[0], state[1], jax.random.key(999, impl='threefry2x32'), state[3])\na, b = next_state(state), next_state(other)\nassert not np.array_equal(np.asarray(jax.random.key_data(a[2])), np.asarray(jax.random.key_data(b[2])))",
                    "State identity matters independently of one displayed number.",
                ),
                case(
                    "Check owned cleanup",
                    "Save inside TemporaryDirectory and verify that its file is gone after the scope.",
                    "File exists inside the scope and is absent afterward.",
                    "The demonstration owns and removes its temporary artifact. It does not delete an unrelated checkpoint.",
                    "with tempfile.TemporaryDirectory() as directory:\n    path = Path(directory) / 'state.npz'\n    save_state(path, prepared_state())\n    assert path.is_file()\nassert not path.exists()",
                    "Keep cleanup scoped to the directory created by the example.",
                ),
                case(
                    "Continue twice",
                    "Compare two further steps after a save/load round trip.",
                    "Matching final state with count four.",
                    "The stored state supports repeated application of the same declared transition.",
                    "state = prepared_state()\nwith tempfile.TemporaryDirectory() as directory:\n    path = Path(directory) / 'state.npz'\n    save_state(path, state)\n    restored = load_state(path)\n    left, right = next_state(next_state(state)), next_state(next_state(restored))\n    compare(left, right)\n    assert int(right[3]) == 4",
                    "Do not reuse the original key after restoring continuation.",
                ),
            ),
            "If continuation differs, compare the next key, current optimizer history, dtype, update count and configuration before increasing tolerance. The current example reconstructs numerical state within one process; a fresh-process and persistent-storage acceptance test is an additional workflow, not implied by this file round trip.",
            "Extend the contract on paper to a shuffled dataset and learning-rate schedule. Identify the extra state and a fresh-process test. Compare the separate prepared checkpoint workflows in torch-028 and tf-028 while preserving the classroom's temporary-file boundary.",
            (
                (
                    "Stateful computations",
                    "https://docs.jax.dev/en/latest/stateful-computations.html",
                ),
                ("Random API", "https://docs.jax.dev/en/latest/jax.random.html"),
            ),
        ),
        Unit(
            18,
            "Debug the first broken transformation invariant",
            "intermediate",
            (17,),
            ("tracer error", "debug print", "checkify", "finite intermediates"),
            "Distinguish host conversion, dynamic shape and numerical-domain failures using bounded diagnostics.",
            r"""A transformation error is often a useful description of an invalid boundary. A traced value cannot be converted to a host NumPy array merely because an eager version worked. A Boolean selection can produce an output length that depends on runtime data, conflicting with a fixed-shape compiled calculation. A finite final value can conceal an undefined derivative in an intermediate branch.

Start diagnosis with the earliest incorrect assumption. Record the intended shape, dtype and domain, then examine the operation that first violates them. Rewriting many operations at once makes it difficult to learn which repair mattered. Turning off JIT can help localize behavior, but an eager-only success is not evidence that the transformed version is now correct.

Use jax.debug.print for bounded runtime values inside transformed functions. Ordinary Python printing primarily observes tracing and may show tracers instead of the expected numeric values. Debug output can also affect execution order and timing, so remove it from performance measurements. The classroom is noninteractive; a breakpoint that waits for terminal input does not fit its job contract.

Checkify can transform explicit checks into an error value carried alongside numerical results. The caller can inspect that error at the host boundary. This is different from inserting an ordinary Python assertion on a traced Boolean. A check does not necessarily make a later invalid numerical operation safe; validate or reformulate its domain as well.

For masked formulas, avoid undefined intermediates. Selecting zero after computing log of an invalid input can still produce problematic derivatives. A safe formulation replaces invalid log inputs with a valid neutral value before taking the logarithm, then applies the selection. The algebraic and differentiation domains should both be explained.""",
            r"""For positive x, \(d\log x/dx=1/x\). If the intended extension returns zero for nonpositive x, define the computational branch so that log is only applied to a valid positive surrogate there. This is an explicit piecewise extension, not a claim that log itself is defined on negative numbers. At the chosen smooth positive points, the derivative must still equal \(1/x\). At a boundary, state the selected differentiation convention rather than asserting ordinary smoothness.""",
            """from jax.experimental import checkify


def safe_log_extension(values):
    positive = values > 0.
    safe_inputs = jnp.where(positive, values, 1.)
    return jnp.where(positive, jnp.log(safe_inputs), 0.)""",
            (
                case(
                    "Repair an undefined intermediate",
                    "Evaluate the piecewise log extension and its summed gradient on [-1,0,2].",
                    "Values [0,0,log(2)] and finite gradient [0,0,0.5].",
                    "Replacing invalid log inputs before evaluation keeps the selected computational path numerically defined.",
                    "values = jnp.array([-1., 0., 2.])\nclose(safe_log_extension(values), [0., 0., math.log(2.)])\ng = jax.grad(lambda x: safe_log_extension(x).sum())(values)\nclose(g, [0., 0., .5])\nassert bool(jnp.isfinite(g).all())",
                    "Repair the domain before applying the outer selection.",
                ),
                case(
                    "Carry a dynamic check",
                    "Transform a positivity check with checkify and inspect good and bad inputs.",
                    "No error for [1,2]; an error message for [1,-2].",
                    "The check becomes an explicit result to inspect at the host boundary rather than a Python Boolean decision during tracing.",
                    "def checked(values):\n    checkify.check(jnp.all(values > 0.), 'positive inputs required')\n    return values.sum()\nrun = jax.jit(checkify.checkify(checked))\ngood, total = run(jnp.array([1., 2.]))\nbad, _ = run(jnp.array([1., -2.]))\nassert good.get() is None\nassert bad.get() is not None\nclose(total, 3.)",
                    "Separate the error result from the numerical result.",
                ),
            ),
            (
                case(
                    "Expose a host conversion",
                    "Attempt np.asarray on an argument inside JIT.",
                    "TracerArrayConversionError.",
                    "A traced runtime value is not a concrete host array available to NumPy during staging.",
                    "try:\n    jax.jit(lambda x: np.asarray(x) + 1)(jnp.ones(2))\nexcept jax.errors.TracerArrayConversionError:\n    pass\nelse:\n    raise AssertionError('host conversion accepted')",
                    "Keep numerical work in JAX or move host conversion outside the transform.",
                ),
                case(
                    "Expose a dynamic output length",
                    "JIT x[x>0] on a mixed-sign vector.",
                    "NonConcreteBooleanIndexError.",
                    "The number of retained values depends on runtime data, so this expression does not specify a fixed output shape.",
                    "try:\n    jax.jit(lambda x: x[x > 0.])(jnp.array([-1., 2.]))\nexcept jax.errors.NonConcreteBooleanIndexError:\n    pass\nelse:\n    raise AssertionError('dynamic shape accepted')",
                    "A fixed-size mask can preserve storage while selecting contributions.",
                ),
                case(
                    "Use a fixed-shape alternative",
                    "Sum positive values using where and a fixed-shaped vector.",
                    "2 for [-1,2].",
                    "This asks for a sum, so retaining a padded vector is sufficient and does not require a variable-length selection.",
                    "function = jax.jit(lambda x: jnp.where(x > 0., x, 0.).sum())\nclose(function(jnp.array([-1., 2.])), 2.)",
                    "Repair the computation according to its desired output, not merely its syntax.",
                ),
                case(
                    "Print a runtime diagnostic",
                    "Emit a bounded sum through debug.print inside a jitted function.",
                    "A diagnostic containing total=3 and unchanged returned total three.",
                    "Runtime diagnostics observe numerical values; they are excluded from later timing claims.",
                    "def observed(x):\n    total = x.sum()\n    jax.debug.print('total={total}', total=total)\n    return total\nclose(jax.jit(observed)(jnp.array([1., 2.])), 3.)",
                    "Use named placeholders and synchronize the returned result.",
                ),
                case(
                    "Compare with JIT disabled",
                    "Evaluate the same jitted polynomial within and outside disable_jit.",
                    "Matching values at [1,2].",
                    "The comparison localizes transformation behavior without treating eager success as the final acceptance criterion.",
                    "function = jax.jit(lambda x: x * x + 1)\nwith jax.disable_jit():\n    eager = function(jnp.array([1., 2.]))\nclose(function(jnp.array([1., 2.])), eager)",
                    "Keep inputs and dtype fixed.",
                ),
                case(
                    "Retain the positive-domain derivative",
                    "Differentiate the safe extension at positive values [1,2,4].",
                    "[1,0.5,0.25].",
                    "A repair for invalid inputs must not damage the intended formula on its valid domain.",
                    "close(jax.grad(lambda x: safe_log_extension(x).sum())(jnp.array([1., 2., 4.])), [1., .5, .25])",
                    "Test valid behavior as well as refusal or extension behavior.",
                ),
            ),
            "Do not catch every exception and report success. Each negative case here names a specific violated contract, while the repaired valid path has its own assertion. Debug printing is observation, not a substitute for a numerical oracle.",
            "Given an unfamiliar transformed program, classify its first failure as shape, host boundary, static configuration, numerical domain or state ownership. Propose one repair and a test that would reject a plausible wrong repair.",
            (
                ("Debugging", "https://docs.jax.dev/en/latest/debugging.html"),
                ("Errors", "https://docs.jax.dev/en/latest/errors.html"),
            ),
        ),
    ]
)
