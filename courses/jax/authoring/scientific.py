"""Scientific computations and advanced derivative mechanisms."""

from model import Unit, case

UNITS = [
    Unit(
        19,
        "Linear solves, residuals and sensitivity",
        "advanced",
        (18,),
        ("linear solve", "conditioning", "residual", "implicit sensitivity"),
        "Solve and differentiate a small linear system while checking its numerical and mathematical assumptions independently.",
        r"""A linear system asks for x satisfying Ax=b. Solving that system is different from explicitly constructing an inverse matrix and multiplying it by b. A direct solve communicates the intended task and avoids materializing an object that may not be needed. The numerical method still depends on the matrix and its conditioning.

A residual measures how closely the returned value satisfies the equation. A small residual is necessary evidence, but an ill-conditioned matrix can amplify a small perturbation into a large change in the solution. Therefore a small residual alone does not prove that the solution is insensitive to measurement or rounding error. Separate the linear algebra contract from the reliability of the problem data.

Differentiating a solve asks how its solution changes when A or b changes. The derivative assumes the local problem is nonsingular and sufficiently regular. If the matrix becomes singular, a smooth derivative of a unique solution may no longer exist. A finite printed gradient cannot create the missing mathematical assumptions.

This unit uses an ordinary solve, an analytic diagonal parameterization and a ridge-regression example. Each has an independent oracle. The host admission helper implements one declared condition-number policy for the fixture. It is not a universal threshold for scientific validity, and it is intentionally outside the transformed numerical calculation.

Regularization changes the equation rather than merely repairing an implementation. Adding a diagonal penalty can improve conditioning while changing the estimated parameters. Explain that bias and its purpose before presenting a better-conditioned numerical result as a better scientific answer.""",
        r"""Differentiating \(A(\theta)x(\theta)=b(\theta)\) gives \(A\,dx/db=I\) when only b varies, and \(dx/d\theta=A^{-1}(db/d\theta-(dA/d\theta)x)\). This identity describes a solve, not a recommendation to form an inverse. For \(A=\operatorname{diag}(2+\theta,3)\), \(b=(2,6)\), the solution is \((2/(2+\theta),2)\). At zero, the derivative of its summed coordinates is \(-1/2\).""",
        """matrix = jnp.array([[3., 1.], [1., 2.]])
right = jnp.array([9., 8.])


def admitted_matrix(value):
    condition = np.linalg.cond(np.asarray(value))
    if not np.isfinite(condition) or condition > 1e10:
        raise ValueError("matrix outside the declared conditioning policy")


def parameter_solution(theta):
    a = jnp.diag(jnp.array([2. + theta, 3.]))
    return jnp.linalg.solve(a, jnp.array([2., 6.]))""",
        (
            case(
                "Check a solve by its equation",
                "Solve the two-by-two system and reconstruct its right-hand side.",
                "Solution [2,3]; residual zero within tolerance.",
                "The independently supplied solution and residual check serve different purposes: one checks this exact fixture, while the other checks the defining equation.",
                "admitted_matrix(matrix)\nsolution = jnp.linalg.solve(matrix, right)\nclose(solution, [2., 3.])\nclose(matrix @ solution - right, [0., 0.])",
                "Multiply the proposed solution back through A.",
            ),
            case(
                "Differentiate a controlled matrix change",
                "Differentiate the sum of parameter_solution at theta zero.",
                "Solution [1,2] and derivative -0.5.",
                "The diagonal algebra supplies an independent sensitivity oracle rather than another autodiff wrapper.",
                "close(parameter_solution(0.), [1., 2.])\nclose(jax.grad(lambda theta: parameter_solution(theta).sum())(0.), -.5)",
                "Differentiate 2/(2+theta) directly.",
            ),
        ),
        (
            case(
                "Change the right-hand side",
                "Solve the same matrix for b=[4,3].",
                "[1,1].",
                "Holding A fixed changes only the forcing values.",
                "close(jnp.linalg.solve(matrix, jnp.array([4., 3.])), [1., 1.])",
                "Check A times [1,1].",
            ),
            case(
                "Differentiate with respect to b",
                "Differentiate the sum of solved coordinates with respect to the right-hand side.",
                "[0.2,0.4].",
                "The pullback solves the transposed system against an all-ones output cotangent.",
                "gradient = jax.grad(lambda b: jnp.linalg.solve(matrix, b).sum())(right)\nclose(gradient, [.2, .4])\nclose(matrix.T @ gradient, [1., 1.])",
                "Write the transpose equation for the pullback.",
            ),
            case(
                "Reject a singular fixture",
                "Apply the declared admission policy to [[1,2],[2,4]].",
                "ValueError.",
                "The second row is twice the first, so the system does not define a unique solution for arbitrary b.",
                "try:\n    admitted_matrix(jnp.array([[1., 2.], [2., 4.]]))\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('singular matrix admitted')",
                "Inspect linear dependence before trusting solver output.",
            ),
            case(
                "Check the sensitivity numerically",
                "Central-difference the summed parameterized solution at zero with h=1e-5.",
                "-0.5 within absolute 1e-8.",
                "The perturbed matrices remain within the local nonsingular regime.",
                "h = 1e-5\nfinite = (parameter_solution(h).sum() - parameter_solution(-h).sum()) / (2 * h)\nclose(finite, -.5, atol=1e-8, rtol=0.)",
                "Perturb the matrix-generating parameter, not the solved x directly.",
            ),
            case(
                "Interpret ridge regularization",
                "Fit y=2x on x=[1,2,3] with penalty lambda=14 and no intercept.",
                "Ridge coefficient one, versus unpenalized two.",
                "The denominator changes from 14 to 28 while the cross-product numerator remains 28.",
                "x = jnp.array([[1.], [2.], [3.]])\ny = 2 * x[:, 0]\nridge = jnp.linalg.solve(x.T @ x + 14 * jnp.eye(1), x.T @ y)\nclose(ridge, [1.])",
                "A regularized estimate targets a changed objective.",
            ),
            case(
                "Compile a valid solve",
                "JIT the solution calculation and compare its residual.",
                "The same [2,3] result with a small residual.",
                "Compilation does not eliminate the need for conditioning and problem-admission checks.",
                "compiled = jax.jit(jnp.linalg.solve)\nsolution = compiled(matrix, right)\nclose(solution, [2., 3.])\nclose(matrix @ solution, right)",
                "Keep numerical-domain admission separate from transformation compatibility.",
            ),
        ),
        "A large sensitivity with a small residual can be an ill-conditioned problem rather than a broken solver. An admission threshold is a declared policy, not a theorem. State the assumptions of a differentiable unique solution and test both primal residual and derivative behavior.",
        "Connect the ridge calculation to the statistics book's bias-variance discussion. Design a sensitivity report that separates perturbation of data, regularization choice and floating-point effects instead of calling every difference solver error.",
        (
            ("JAX NumPy linear algebra", "https://docs.jax.dev/en/latest/jax.numpy.html"),
            (
                "Custom linear solves",
                "https://docs.jax.dev/en/latest/_autosummary/jax.lax.custom_linear_solve.html",
            ),
        ),
    ),
    Unit(
        20,
        "Differentiate a simulation and measure discretization error",
        "advanced",
        (19,),
        ("Euler method", "scan", "discretization", "parameter sensitivity"),
        "Build a differentiable fixed-step simulation and distinguish the derivative of the discretized algorithm from the continuous model.",
        r"""A numerical simulator approximates a mathematical model through a specified algorithm. Autodiff differentiates the implemented algorithm. Those derivatives can be exactly consistent with the code while differing from the derivatives of an ideal continuous model because the discretization is approximate.

Consider exponential decay with rate k. A forward Euler step subtracts k times the current value times the step duration. Repeating that step with scan makes the state transition explicit. A smaller step duration generally reduces this method's discretization error over the same fixed horizon in the stable regime, while requiring more steps.

The horizon must stay fixed when comparing step sizes. Halving the duration per step without doubling the step count changes both the algorithm and the simulated time. That would not isolate discretization error. Retain the initial value, rate, horizon and reference solution when studying convergence.

Parameter calibration adds another layer. An optimizer can fit the discretized simulator to observations, but its fitted parameter may absorb numerical error or model misspecification. A lower residual does not show that the continuous physical parameter has been recovered. Synthetic observations with a known generating model help expose these distinctions before real data are introduced.

The examples below use a one-dimensional system with a closed-form solution. This makes both the simulated value and its sensitivity independently inspectable. More complex models need their own solver accuracy, stability and identification analysis. A JAX transformation does not supply those scientific assumptions automatically.""",
        r"""For \(dx/dt=-kx\), the continuous solution at horizon T is \(x(T)=x_0e^{-kT}\). Euler with n steps of size \(h=T/n\) gives \(x_n=x_0(1-kh)^n\). Its rate derivative is \(-nhx_0(1-kh)^{n-1}\), while the continuous derivative is \(-Tx_0e^{-kT}\). These are different finite-step formulas that approach one another under a suitable refinement regime.""",
        """def simulate(rate, initial=1., *, steps=10, horizon=1.):
    dt = horizon / steps
    def transition(value, unused):
        updated = value * (1 - rate * dt)
        return updated, updated
    return jax.lax.scan(transition, jnp.asarray(initial, dtype=jnp.float64), xs=None, length=steps)[0]""",
        (
            case(
                "Check the discretized value",
                "Simulate rate one for ten steps over horizon one.",
                "0.9^10, approximately 0.34867844.",
                "This matches the Euler recurrence. It is below the continuous value exp(-1), revealing finite-step error.",
                "value = simulate(1.)\nclose(value, .9 ** 10)\nassert float(value) < math.exp(-1.)",
                "Compute the per-step multiplier before raising it to n.",
            ),
            case(
                "Refine at the same horizon",
                "Compare ten and twenty steps with the same rate and horizon.",
                "The twenty-step value is closer to exp(-1).",
                "Doubling the count while halving duration isolates this discretization change.",
                "error10 = abs(float(simulate(1., steps=10)) - math.exp(-1.))\nerror20 = abs(float(simulate(1., steps=20)) - math.exp(-1.))\nassert error20 < error10",
                "Keep total simulated time equal.",
            ),
        ),
        (
            case(
                "Differentiate the implemented algorithm",
                "Calculate the rate derivative for ten Euler steps at rate one.",
                "-0.9^9.",
                "The derivative belongs to the discretized recurrence, not directly to the continuous exponential.",
                "close(jax.grad(simulate)(1.), -(.9 ** 9))",
                "Differentiate (1-k/10)^10.",
            ),
            case(
                "Compare continuous sensitivity",
                "Calculate the continuous rate derivative at horizon one and compare it with Euler's.",
                "Continuous -exp(-1), different from the ten-step derivative.",
                "A disagreement here is expected discretization error rather than an autodiff defect.",
                "continuous = -math.exp(-1.)\ndiscrete = float(jax.grad(simulate)(1.))\nassert not np.isclose(continuous, discrete, atol=1e-4, rtol=0.)",
                "Identify which mathematical object each derivative describes.",
            ),
            case(
                "Refine the derivative",
                "Compare derivative errors for ten and twenty steps.",
                "The twenty-step derivative is closer to the continuous derivative.",
                "Derivative convergence should be examined separately from value convergence.",
                "exact = -math.exp(-1.)\na = abs(float(jax.grad(lambda k: simulate(k, steps=10))(1.)) - exact)\nb = abs(float(jax.grad(lambda k: simulate(k, steps=20))(1.)) - exact)\nassert b < a",
                "Use the same horizon and parameter in both comparisons.",
            ),
            case(
                "Check zero rate",
                "Simulate rate zero starting from three.",
                "The state remains three.",
                "The transition multiplier becomes one, so no decay occurs.",
                "close(simulate(0., initial=3.), 3.)",
                "Check a physically interpretable boundary.",
            ),
            case(
                "Differentiate the initial state",
                "Calculate sensitivity to the initial value at rate one.",
                "0.9^10.",
                "This linear system scales every initial perturbation by the complete discrete decay factor.",
                "close(jax.grad(lambda initial: simulate(1., initial=initial))(2.), .9 ** 10)",
                "Separate initial-condition and rate sensitivity.",
            ),
            case(
                "Inspect an unstable numerical regime",
                "Use one Euler step with rate three over horizon one.",
                "-2, despite positive continuous decay exp(-3).",
                "The large step leaves the intended stable positive-decay regime. A finite result does not make the discretization appropriate.",
                "close(simulate(3., steps=1), -2.)\nassert math.exp(-3.) > 0.",
                "Inspect the multiplier 1-kh before running many steps.",
            ),
        ),
        "Before interpreting a gradient or fitted parameter, check time horizon, step size, stability and solver error. A successful scan only proves that the chosen recurrence executed. Do not use a differentiable but unstable algorithm as unqualified evidence about a continuous system.",
        "Design a calibration study with independent synthetic observations, at least two discretizations and a sensitivity analysis. State whether the estimated parameter describes the continuous model, its numerical approximation or a misspecified surrogate.",
        (
            ("Control flow", "https://docs.jax.dev/en/latest/control-flow.html"),
            ("Numerical accuracy", "https://docs.jax.dev/en/latest/accuracy.html"),
        ),
    ),
]

UNITS.extend(
    [
        Unit(
            21,
            "Monte Carlo estimates and pathwise sensitivity",
            "advanced",
            (20,),
            ("Monte Carlo", "reparameterization", "common random numbers", "sampling error"),
            "Differentiate a fixed-sample reparameterized objective and separate that derivative from population expectations and Monte Carlo uncertainty.",
            r"""A Monte Carlo estimate replaces an expectation with an average of sampled values. Its finite-sample variability remains even when every arithmetic operation is correct. JAX can batch and differentiate a simulation, but it cannot make sampling uncertainty disappear.

A reparameterization expresses a random quantity using a parameter-free draw and a deterministic transformation. For a normal variable, write x=mu+sigma times epsilon, with epsilon drawn from a standard normal. Holding the sampled epsilon values fixed makes the sample objective a deterministic function of mu and sigma. Autodiff then computes its pathwise derivative.

The derivative of that finite sample need not equal the derivative of the population expectation exactly. Under appropriate assumptions, it can estimate the desired sensitivity. Those assumptions include the model, sampling design and conditions for exchanging differentiation and expectation. Discrete sampling requires additional methods or a different estimator; calling grad does not automatically create a meaningful derivative of a categorical draw.

Common random numbers help compare nearby parameter values: use the same base draws for both, so the difference isolates the parameter change rather than adding independent simulation noise. This is especially useful for a finite-difference check. A new random draw for each perturbation measures a different noisy comparison.

The two-point worked fixture uses authored values -1 and 1 as an exact arithmetic control, not as evidence that two random normal observations represent a population. A separate seeded draw demonstrates the actual Monte Carlo path. Keep those sources of evidence labeled and report the sample count with any estimate or uncertainty summary.""",
            r"""For \(X=\mu+\sigma\epsilon\) with standard normal epsilon, \(\mathbb E[X^2]=\mu^2+\sigma^2\). A fixed sample estimates this by \(\widehat M=N^{-1}\sum_i(\mu+\sigma\epsilon_i)^2\). Its derivatives are \(2N^{-1}\sum_i(\mu+\sigma\epsilon_i)\) and \(2N^{-1}\sum_i(\mu+\sigma\epsilon_i)\epsilon_i\). For the authored symmetric pair and \((\mu,\sigma)=(2,3)\), these give 13, 4 and 6 exactly.""",
            """def sample_objective(mean, scale, noise):
    return jnp.mean((mean + scale * noise) ** 2)

control = jnp.array([-1., 1.])
noise = jax.random.normal(jax.random.key(61), (1024,), dtype=jnp.float64)""",
            (
                case(
                    "An exact fixed-sample control",
                    "Calculate the sample objective and both parameter derivatives on noise [-1,1].",
                    "Objective 13, mean derivative 4, scale derivative 6.",
                    "The selected pair has mean zero and mean square one by construction. It is an algebraic test of the pathwise formula.",
                    "value, gradients = jax.value_and_grad(sample_objective, argnums=(0, 1))(2., 3., control)\nclose(value, 13.)\nclose(gradients[0], 4.)\nclose(gradients[1], 6.)",
                    "Evaluate the two transformed samples [-1,5].",
                ),
                case(
                    "Inspect a real sampled estimate",
                    "Compute a seeded 1024-draw objective and compare its autodiff gradient with the explicit sample formula.",
                    "Finite estimate; exact agreement of both sample-gradient constructions within tolerance.",
                    "The population value 13 is a reference expectation, not a required exact result of this random sample.",
                    "value, gradients = jax.value_and_grad(sample_objective, argnums=(0, 1))(2., 3., noise)\nassert bool(jnp.isfinite(value))\nclose(gradients[0], 2 * jnp.mean(2. + 3. * noise))\nclose(gradients[1], 2 * jnp.mean((2. + 3. * noise) * noise))",
                    "Check the finite-sample identity before interpreting population error.",
                ),
            ),
            (
                case(
                    "Reuse draws in a derivative check",
                    "Central-difference the mean parameter with the same noise array for both perturbations.",
                    "Agreement with autodiff within absolute 1e-7.",
                    "Shared base draws prevent random resampling from contaminating the numerical derivative comparison.",
                    "h = 1e-5\nfinite = (sample_objective(2. + h, 3., noise) - sample_objective(2. - h, 3., noise)) / (2 * h)\nclose(finite, jax.grad(sample_objective)(2., 3., noise), atol=1e-7, rtol=0.)",
                    "Do not call the random generator separately inside each perturbation.",
                ),
                case(
                    "Parameterize a positive scale",
                    "Use scale=exp(log_scale) and differentiate at log(3) with the control pair.",
                    "Derivative 18.",
                    "The chain rule multiplies the scale derivative six by the current scale three.",
                    "function = lambda log_scale: sample_objective(2., jnp.exp(log_scale), control)\nclose(jax.grad(function)(math.log(3.)), 18.)",
                    "Differentiate the parameterization as well as the objective.",
                ),
                case(
                    "Check a zero-mean population formula",
                    "Evaluate the control pair with mean zero and scale two.",
                    "Objective four and mean derivative zero.",
                    "Symmetry makes the authored sample's first moment zero.",
                    "close(sample_objective(0., 2., control), 4.)\nclose(jax.grad(sample_objective)(0., 2., control), 0.)",
                    "Distinguish symmetry of the control from a universal finite-sample property.",
                ),
                case(
                    "Retain the Monte Carlo count",
                    "Calculate an estimated standard error for the mean squared transformed draws using sample variance.",
                    "A finite nonnegative SE with N=1024 explicitly retained.",
                    "The usual variance-over-count expression assumes the declared independent sampling design; it is not applied to the two authored control points as a population study.",
                    "draws = (2. + 3. * noise) ** 2\ncount = draws.size\nse = jnp.sqrt(jnp.var(draws, ddof=1) / count)\nassert count == 1024\nassert bool(jnp.isfinite(se)) and float(se) >= 0.",
                    "Use the variance of the quantity being averaged.",
                ),
                case(
                    "Vectorize parameter comparisons",
                    "Evaluate means [0,1,2] at scale three with the same control pair.",
                    "[9,10,13].",
                    "Sharing draws defines a controlled comparison of parameter settings.",
                    "values = jax.vmap(lambda mean: sample_objective(mean, 3., control))(jnp.array([0., 1., 2.]))\nclose(values, [9., 10., 13.])",
                    "The parameter axis is distinct from the draw axis.",
                ),
                case(
                    "Replay the sampled input",
                    "Recreate noise with the same root key, shape and dtype.",
                    "Matching draws and estimate in the pinned environment.",
                    "The complete random-operation contract supports replay.",
                    "again = jax.random.normal(jax.random.key(61), (1024,), dtype=jnp.float64)\nclose(again, noise)\nclose(sample_objective(2., 3., again), sample_objective(2., 3., noise))",
                    "Record shape and dtype along with the key policy.",
                ),
            ),
            "If a finite-difference sensitivity is noisy, first check whether the base draws changed. If a sample estimate differs from its analytic expectation, quantify sampling error before changing the algorithm. Autodiff of a discrete draw requires a separately justified estimator.",
            "Design a comparison of two simulation policies using common random numbers and independent repeated replications. State which uncertainty comes from Monte Carlo sampling and which comes from model or data assumptions.",
            (
                ("Random numbers", "https://docs.jax.dev/en/latest/random-numbers.html"),
                ("Autodiff cookbook", "https://docs.jax.dev/en/latest/301/cookbook.html"),
            ),
        ),
        Unit(
            22,
            "Custom JVP and VJP rule validation",
            "advanced",
            (21,),
            ("custom_jvp", "custom_vjp", "tangent linearity", "saved residual"),
            "Define and independently validate custom derivative rules while respecting their transformation limits.",
            r"""Ordinary differentiable JAX operations should be the first choice when they express a computation correctly. A custom derivative is useful when a justified derivative rule differs from the convenient implementation path, when a stable formulation needs a specialized derivative, or when an external operation has an explicitly supported differentiation contract.

A custom JVP specifies the primal value and how an input tangent maps to an output tangent. That tangent rule must be linear in the tangent input. Squaring the tangent or ignoring its scale would violate the meaning of a derivative even if one test with tangent one passed. JAX can transpose a valid linear tangent rule for reverse differentiation.

A custom VJP separates a forward pass that returns the value and saved residuals from a backward pass that consumes an output cotangent. Residuals should retain the information the pullback actually needs. The backward result must match the number and structure of differentiated arguments. A unit cotangent test is not enough: upstream scaling must propagate correctly through composition.

The decorators have different transformation limits. In particular, a custom_vjp function does not automatically support direct forward-mode JVP. Higher derivatives and batching also need their own checks. Do not assume that passing the first forward example qualifies every transformation.

This unit uses transparent functions whose ordinary derivatives are known. That makes it possible to compare custom behavior against algebra, finite differences and ordinary JAX primitives. A more complex rule should preserve this independent validation discipline instead of trusting that a decorator makes it mathematically correct.""",
            r"""Stable softplus is \(s(x)=\log(1+e^x)\), with derivative \(\sigma(x)\). Its JVP maps tangent t to \(\sigma(x)t\), which is linear in t. For \(f(x)=x^2\), a VJP maps output cotangent u to \(2xu\). At x=3 and u=4, the pullback is 24. Returning only 2x would pass a unit-upstream case and fail this composition.""",
            """@jax.custom_jvp
def stable_softplus(value):
    return jnp.logaddexp(0., value)


@stable_softplus.defjvp
def softplus_jvp(primals, tangents):
    (value,), (tangent,) = primals, tangents
    return stable_softplus(value), jax.nn.sigmoid(value) * tangent


@jax.custom_vjp
def custom_square(value):
    return value * value


def square_forward(value):
    return value * value, value


def square_backward(saved, cotangent):
    return (2 * saved * cotangent,)

custom_square.defvjp(square_forward, square_backward)""",
            (
                case(
                    "A stable custom JVP",
                    "Evaluate softplus at zero and its JVP with tangent three.",
                    "Value log(2), tangent 1.5.",
                    "The derivative is sigmoid(0)=0.5 and must be multiplied by the supplied tangent.",
                    "value, tangent = jax.jvp(stable_softplus, (jnp.float64(0.),), (jnp.float64(3.),))\nclose(value, math.log(2.))\nclose(tangent, 1.5)",
                    "Check a non-unit tangent.",
                ),
                case(
                    "Propagate a non-unit cotangent",
                    "Pull back cotangent four through custom_square at three.",
                    "24.",
                    "The backward rule composes local sensitivity six with incoming sensitivity four.",
                    "value, back = jax.vjp(custom_square, jnp.float64(3.))\nclose(value, 9.)\nclose(back(jnp.float64(4.))[0], 24.)",
                    "Do not drop the upstream factor.",
                ),
            ),
            (
                case(
                    "Compare an ordinary gradient",
                    "Compare the custom softplus gradient with sigmoid at [-2,0,2].",
                    "Matching values.",
                    "The independent primitive provides a direct analytic derivative implementation.",
                    "points = jnp.array([-2., 0., 2.])\nclose(jax.vmap(jax.grad(stable_softplus))(points), jax.nn.sigmoid(points))",
                    "Keep the forward formula and derivative formula separate.",
                ),
                case(
                    "Check tangent linearity",
                    "Compare JVP tangents two, three and five at x=1.",
                    "The five-direction result equals the sum of the two and three results.",
                    "Linearity is required of the local derivative map, not an optional optimization.",
                    "jvp = lambda tangent: jax.jvp(stable_softplus, (jnp.float64(1.),), (jnp.float64(tangent),))[1]\nclose(jvp(5.), jvp(2.) + jvp(3.))",
                    "Test additivity as well as one numerical value.",
                ),
                case(
                    "Check an extreme stable input",
                    "Evaluate softplus and its gradient at 1000.",
                    "Finite value 1000 and gradient one.",
                    "The primal avoids constructing exp(1000); the derivative also remains representable.",
                    "close(stable_softplus(1000.), 1000.)\nclose(jax.grad(stable_softplus)(1000.), 1.)",
                    "A stable forward needs a stable derivative rule too.",
                ),
                case(
                    "Differentiate a composition",
                    "Differentiate four times custom_square at three.",
                    "24.",
                    "This independently tests that upstream scaling survives through grad.",
                    "close(jax.grad(lambda x: 4 * custom_square(x))(3.), 24.)",
                    "The outer multiplication changes the incoming cotangent.",
                ),
                case(
                    "Check a second derivative",
                    "Differentiate the custom softplus gradient at zero.",
                    "0.25.",
                    "This exercises a higher derivative of the implemented custom rule rather than assuming it from the first derivative.",
                    "close(jax.grad(jax.grad(stable_softplus))(0.), .25)",
                    "Differentiate sigmoid as p(1-p).",
                ),
                case(
                    "Name the forward-mode limit",
                    "Attempt a direct JVP through the custom_vjp square.",
                    "TypeError under the documented custom_vjp contract.",
                    "The VJP decorator provides reverse-mode behavior, not an automatic forward-mode rule.",
                    "try:\n    jax.jvp(custom_square, (jnp.float64(3.),), (jnp.float64(1.),))\nexcept TypeError:\n    pass\nelse:\n    raise AssertionError('unexpected custom_vjp forward-mode support')",
                    "Choose the custom-rule mechanism according to required transformations.",
                ),
            ),
            "A correct forward result cannot validate a custom backward rule. Include non-unit upstream values, tangent linearity, independent derivatives and the transformation compositions you intend to support. Keep unsupported modes explicit rather than silently detaching a computation.",
            "Propose a custom derivative for an implicit scientific computation and list its required residuals. Explain which assumptions would justify it and how you would detect a rule that returns a plausible but incorrect gradient.",
            (
                (
                    "Custom derivative rules",
                    "https://docs.jax.dev/en/latest/301/custom-jvp-vjp.html",
                ),
            ),
        ),
    ]
)

UNITS.extend(
    [
        Unit(
            23,
            "Implicit differentiation depends on the solved equation",
            "advanced",
            (22,),
            ("implicit derivative", "custom_linear_solve", "primal residual", "transpose solve"),
            "Validate an implicit linear-solve derivative by checking both the defining equation and its sensitivity assumptions.",
            r"""An iterative algorithm can contain many steps, stopping decisions and temporary values. Sometimes the desired derivative is most naturally described by the equation its result satisfies rather than by differentiating every implementation step. Implicit differentiation uses that defining relation, under assumptions that make the solution locally well defined.

For a linear solve, the relation is Ax=b. JAX's custom_linear_solve lets an author supply a solve operation while differentiating through the stated equation. The author is responsible for making the solver satisfy that equation. The API does not prove convergence or automatically reject an incorrect solver output.

The transpose solve matters in reverse mode. A pullback can require solving A-transpose against an output cotangent. Declaring a matrix symmetric allows the same solve relationship to be reused, but that declaration is a mathematical promise. Making it merely because two shapes match can produce an incorrect derivative for a nonsymmetric system.

This example chooses a diagonal positive matrix so that both the solver and the sensitivity can be checked by hand. The custom solve uses direct coordinate division, not a sophisticated iterative method. The lesson therefore establishes the implicit interface and its invariants without claiming a speedup or convergence result for an unimplemented solver.

A deliberately wrong solver is included as a negative control. Its finite output has the right shape, yet a residual check reveals it does not solve the equation. This shows why a returned value and a callable gradient are not sufficient acceptance criteria. For an approximate iterative solve, residual tolerance and its influence on gradient error would need a separate numerical study.""",
            r"""For \(D(\theta)=\operatorname{diag}(2+\theta,3)\), \(x=D^{-1}b\). At \(\theta=0\), b=(2,6), x=(1,2). Holding b fixed gives \(dx/d\theta=(-1/2,0)\). The summed-output pullback with respect to b is \((1/2,1/3)\). Because this diagonal matrix is symmetric, primal and transpose solve equations use the same diagonal entries.""",
            """def implicit_solution(theta, right):
    diagonal = jnp.array([2. + theta, 3.])
    def matvec(value):
        return diagonal * value
    def solve(operation, rhs):
        return rhs / diagonal
    return jax.lax.custom_linear_solve(matvec, right, solve=solve, symmetric=True)

right = jnp.array([2., 6.])""",
            (
                case(
                    "Check the primal equation",
                    "Evaluate the implicit solution at theta zero and multiply it by the diagonal.",
                    "Solution [1,2], reconstructed right-hand side [2,6].",
                    "The residual verifies the invariant required by the custom-solve interface.",
                    "solution = implicit_solution(0., right)\nclose(solution, [1., 2.])\nclose(jnp.array([2., 3.]) * solution, right)",
                    "A right shape is weaker evidence than a small residual.",
                ),
                case(
                    "Check the implicit sensitivity",
                    "Differentiate the summed solution with respect to theta.",
                    "-0.5.",
                    "The derivative follows the equation's dependence on the diagonal, independently confirmed by the closed-form first coordinate.",
                    "close(jax.grad(lambda theta: implicit_solution(theta, right).sum())(0.), -.5)",
                    "Differentiate the defining equation, then solve for the sensitivity.",
                ),
            ),
            (
                case(
                    "Pull back to the right-hand side",
                    "Differentiate the summed solution with respect to b.",
                    "[0.5,1/3].",
                    "The output cotangent of ones is solved through the transposed diagonal system.",
                    "close(jax.grad(lambda b: implicit_solution(0., b).sum())(right), [.5, 1 / 3])",
                    "Identify the cotangent before solving.",
                ),
                case(
                    "Change the diagonal",
                    "Set theta two and solve the same right-hand side.",
                    "[0.5,2].",
                    "Only the first diagonal entry changes, so only the first solved coordinate changes.",
                    "close(implicit_solution(2., right), [.5, 2.])",
                    "Check each independent coordinate.",
                ),
                case(
                    "Compare an ordinary solve",
                    "Compare with jnp.linalg.solve for theta 0.5.",
                    "Matching primal values.",
                    "The ordinary solver is a second implementation of the same tiny equation, not proof of arbitrary custom-solver convergence.",
                    "a = jnp.diag(jnp.array([2.5, 3.]))\nclose(implicit_solution(.5, right), jnp.linalg.solve(a, right))",
                    "Hold A and b fixed in both paths.",
                ),
                case(
                    "Detect a bogus solver",
                    "Supply a solver returning zeros and test its residual.",
                    "Finite zero output, but a nonzero residual; the contract fails.",
                    "custom_linear_solve relies on the supplied solver's correctness and does not establish this invariant automatically.",
                    "diagonal = jnp.array([2., 3.])\nwrong = jax.lax.custom_linear_solve(lambda x: diagonal * x, right, solve=lambda operation, rhs: jnp.zeros_like(rhs), symmetric=True)\nassert bool(jnp.isfinite(wrong).all())\nassert not np.allclose(np.asarray(diagonal * wrong), np.asarray(right))",
                    "Validate returned solutions even when the library call succeeds.",
                ),
                case(
                    "Check a second derivative",
                    "Differentiate the summed solution twice at theta zero.",
                    "0.5.",
                    "For 2/(2+theta), the second derivative is 4/(2+theta)^3.",
                    "second = jax.grad(jax.grad(lambda theta: implicit_solution(theta, right).sum()))\nclose(second(0.), .5)",
                    "Higher derivatives deserve explicit qualification.",
                ),
                case(
                    "Compile the valid interface",
                    "JIT the implicit solution and compare the residual at theta one.",
                    "[2/3,2], satisfying the diagonal equation.",
                    "Compilation compatibility and solver correctness remain separate checks.",
                    "solution = jax.jit(implicit_solution)(1., right)\nclose(solution, [2 / 3, 2.])\nclose(jnp.array([3., 3.]) * solution, right)",
                    "Reconstruct the actual diagonal used in this call.",
                ),
            ),
            "Do not declare symmetry or convergence to make an API path convenient. Check the primal residual, required transpose behavior and independent sensitivities. Near singularity, the differentiable-solution assumptions and numerical conditioning can fail together.",
            "Describe how you would replace the direct diagonal solver with an iterative matrix-free solver. Specify stopping tolerance, residual evidence, transpose solve and a study of how solve error affects gradient error.",
            (
                (
                    "custom_linear_solve",
                    "https://docs.jax.dev/en/latest/_autosummary/jax.lax.custom_linear_solve.html",
                ),
            ),
        ),
        Unit(
            24,
            "Inspect shapes, jaxpr and compilation stages",
            "advanced",
            (23,),
            ("eval_shape", "jaxpr", "lowering", "compiled signature"),
            "Inspect distinct staging artifacts without treating their existence as a proof of portability or performance.",
            r"""A source function, a staged representation, a lowered computation and a compiled executable are different artifacts. The source expresses the user's numerical program. A jaxpr describes primitive operations under a tracing contract. Lowering prepares a compiler-facing representation. Compilation produces an executable for a particular backend and signature.

Shape evaluation can answer an interface question before allocating a full concrete input. A ShapeDtypeStruct describes an abstract shape and dtype, and eval_shape follows the supported numerical function to infer its output structure. This is useful for detecting an interface mismatch, but it does not inspect actual input values or prove that a numerical domain condition holds.

Reading a small jaxpr helps identify the operations and dependencies that a transformation saw. Avoid tying a course acceptance test to every character of pretty-printed compiler output, since representation details can change with versions. Check semantic properties such as the number and shape of outputs, then compare actual numerical values independently.

An ahead-of-time compiled callable is specialized to its abstract input contract. Calling it with a new incompatible shape is not the same as calling a jitted Python wrapper that can create another specialization. Explain which layer owns retracing and recompilation before diagnosing a signature error.

Portable export and deployment introduce additional contracts: supported platforms, serialized representation, shape polymorphism, dependencies, versions and trust. This unit does not claim that printing lowered text or retaining a process-local executable creates a portable model artifact. A separately prepared export workflow should test fresh-process reconstruction and the target runtime explicitly.""",
            r"""For \(f(X)=X^{\mathsf T}X\) with \(X\in\mathbb R^{N\times D}\), the output shape is \((D,D)\). N affects the reduction but not the output dimensions. For \(X=\begin{bmatrix}1&2\\3&4\\5&6\end{bmatrix}\), the Gram matrix is \(\begin{bmatrix}35&44\\44&56\end{bmatrix}\). This exact small matrix checks the same interface that abstract shape evaluation describes.""",
            """def gram(values):
    return values.T @ values

values = jnp.array([[1., 2.], [3., 4.], [5., 6.]])""",
            (
                case(
                    "Infer an output interface",
                    "Evaluate the abstract shape of gram on a (3,2) float64 input.",
                    "Shape (2,2), dtype float64.",
                    "The result describes the interface without claiming any particular Gram values for unseen data.",
                    "shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((3, 2), jnp.float64))\nassert shape.shape == (2, 2)\nassert shape.dtype == jnp.float64",
                    "Trace the two dimensions through the transpose and product.",
                ),
                case(
                    "Lower, compile and execute",
                    "Lower a jitted gram for the literal input, compile it and execute.",
                    "[[35,44],[44,56]].",
                    "Lowering and compilation precede execution. The numerical assertion qualifies this concrete call, while no timing or portability claim is inferred.",
                    "lowered = jax.jit(gram).lower(values)\ncompiled = lowered.compile()\nclose(compiled(values), [[35., 44.], [44., 56.]])",
                    "Do not confuse an inspectable compiler artifact with returned values.",
                ),
            ),
            (
                case(
                    "Change only the abstract row count",
                    "Infer gram's output for a (7,2) input.",
                    "Still (2,2).",
                    "The feature count controls the Gram dimensions; row count is reduced.",
                    "shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((7, 2), jnp.float64))\nassert shape.shape == (2, 2)",
                    "Name the reduced observation axis.",
                ),
                case(
                    "Change the feature count",
                    "Infer gram's output for a (3,4) input.",
                    "(4,4).",
                    "An extra feature changes both Gram axes.",
                    "shape = jax.eval_shape(gram, jax.ShapeDtypeStruct((3, 4), jnp.float64))\nassert shape.shape == (4, 4)",
                    "Do not hard-code output shape from the first fixture.",
                ),
                case(
                    "Inspect staged dependencies",
                    "Create a jaxpr for gram and inspect its output count.",
                    "One output variable and at least one numerical equation.",
                    "This robust structural check avoids asserting a version-specific pretty-print string.",
                    "closed = jax.make_jaxpr(gram)(values)\nassert len(closed.jaxpr.outvars) == 1\nassert closed.jaxpr.eqns",
                    "Use structural fields for the stated property.",
                ),
                case(
                    "Execute another compatible value",
                    "Reuse the compiled signature on twice the original input.",
                    "Four times the original Gram matrix.",
                    "The shape and dtype stay compatible, while the bilinear product scales quadratically.",
                    "compiled = jax.jit(gram).lower(values).compile()\nclose(compiled(2 * values), 4 * gram(values))",
                    "A new numeric value need not imply a new abstract signature.",
                ),
                case(
                    "Compose a scalar sensitivity",
                    "Differentiate the sum of the Gram matrix with respect to input values.",
                    "Each row has two copies of twice its row sum: [[6,6],[14,14],[22,22]].",
                    r"The sum of \(X^{\mathsf T}X\) equals the sum of squared row sums.",
                    "close(jax.grad(lambda x: gram(x).sum())(values), [[6., 6.], [14., 14.], [22., 22.]])",
                    "Derive an equivalent scalar formula before differentiating.",
                ),
                case(
                    "Separate metadata from values",
                    "Use a zero input with the same abstract signature and compare the output shape and values.",
                    "Same (2,2) shape, all-zero matrix.",
                    "Shape inference cannot establish a data-dependent numeric answer.",
                    "zero = jnp.zeros_like(values)\nresult = jax.jit(gram)(zero)\nassert result.shape == (2, 2)\nclose(result, jnp.zeros((2, 2)))",
                    "An interface contract is not a value oracle.",
                ),
            ),
            "For a staging mismatch, identify whether the failure concerns source tracing, lowering, backend compilation or an executable signature. Avoid brittle checks of textual IR, and do not call a process-local compiled object a portable export.",
            "Design a deployment artifact contract with input/output shapes, dtype, backend, version and fresh-process evidence. Explain which parts this unit checked and which would require a separately prepared export/target-runtime workflow.",
            (
                ("Ahead-of-time compilation", "https://docs.jax.dev/en/latest/aot.html"),
                ("Jaxpr", "https://docs.jax.dev/en/latest/601/jaxpr.html"),
            ),
        ),
    ]
)
