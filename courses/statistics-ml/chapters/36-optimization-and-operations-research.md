# 36. Optimization and Operations Research

Book: **Statistics and Machine Learning for Data Scientists End To End**. Chapter ID: `statistics-036`. Tutorial mode; all examples and interview answers are fully worked.

## The decision and the mental model

Optimization translates an objective and constraints into a decision. Prediction estimates what may happen; optimization chooses what to do under that estimate. A mathematically optimal solution can still be operationally wrong if the objective omits a cost, a constraint is missing, or uncertain inputs are treated as known. The first modeling task is therefore to name decision variables, units, feasible actions and the consequence being minimized or maximized.

### Write the model before choosing a solver

A linear program minimizes \(c^{\mathsf T}\cdot x\) subject to \(A\cdot x\le b\), equality constraints and variable bounds. Here x contains controllable decisions, c expresses per-unit objective contributions, and each row of A describes a resource or policy constraint. Integrality matters when a decision is indivisible. Relaxing a binary assignment to a fractional number can create a mathematically feasible answer that no operator can implement.

Convexity is valuable because a local optimum is global under the appropriate formulation, but it does not make poor data or objectives correct. A differentiable convex objective lies above its tangent plane. Nonconvex problems can have many stationary points, and a solver success flag generally does not certify the best global value. Read termination conditions, feasibility residuals and available optimality gaps.

### Constraints have economic meaning

For a minimization problem with \(g_i(x)\le0\), the Lagrangian is \(\mathcal{L}=f(x)+\sum_i\lambda_i g_i(x)\), with nonnegative multipliers for inequality constraints. KKT conditions combine stationarity, primal feasibility, dual feasibility and complementary slackness under suitable regularity. A multiplier can describe local sensitivity of the optimal value to a constraint bound, but sign conventions and degeneracy matter. It is not automatically a stable business price outside the local model.

### Uncertainty belongs in the decision model

Using expected demand in a deterministic inventory problem can differ from optimizing expected cost because shortages and excess stock have asymmetric consequences. Stochastic programming represents scenarios with probabilities; robust optimization protects against a set of possibilities; chance constraints require a specified probability of feasibility. Each approach encodes a different attitude toward uncertainty. Scenario quality, tail coverage and recourse assumptions determine whether the resulting protection is meaningful.

### Verify the returned decision

Recompute the objective and every constraint from the returned x using original units. Check integrality and tolerances, then perturb uncertain inputs to see whether the decision is stable. Compare with a simple feasible baseline and identify binding constraints. Separate solver failure, infeasibility, unboundedness and a time-limited feasible solution. A solver output is a candidate decision plus a certificate or status, not a substitute for model review.

The examples solve a small resource-allocation linear program, verify KKT conditions by hand, solve an assignment and calculate queue congestion. They demonstrate how exact arithmetic checks and solver residuals support a concrete claim. They do not infer that a much larger operational model has been validated.

## Methods, mechanisms, and limits

### stat-36-01

**Linear programming**

Linear programming optimizes a linear objective over linear equalities, inequalities and bounds. Feasible sets are polyhedra, and an optimum can often be found at an extreme point when one exists. Carefully encode units and inequality direction. A maximization objective is commonly negated for a minimization solver. Infeasible and unbounded statuses describe different modeling or operational situations and require different investigation.

### stat-36-02

**Integer programming**

Integer programming restricts some decision variables to integers, representing counts, selections or indivisible actions. This can make the feasible set nonconvex and computationally difficult even when all expressions are linear. Rounding a continuous relaxation can violate constraints or produce a poor solution. Inspect the incumbent feasible objective and bound/optimality gap when the solver stops before proving optimality.

### stat-36-03

**Mixed-integer programming**

Mixed-integer programming combines continuous quantities with discrete choices, such as whether to open a facility and how much flow to route through it. Linking constraints and big-M values require care: oversized M weakens relaxations and can harm numerical stability. A feasible solution may still rely on a missing business rule. Validate logic with small enumerated cases before scaling.

### stat-36-04

**Quadratic programming**

Quadratic programming adds a quadratic objective, often written one-half*x_transpose*Q*x+\(c^{\mathsf T}\cdot x\), with constraints. Positive semidefinite Q yields a convex objective; an indefinite Q changes the global-optimization problem. Portfolio and least-squares formulations are common uses, but input covariance or cost estimates can be unstable. Check symmetry, scaling and whether the solver assumptions match Q.

### stat-36-05

**Convex optimization**

Convex optimization minimizes a convex function over a convex feasible set. Under suitable conditions, local optimality is sufficient for global optimality, and duality can provide useful certificates. The formulation must actually preserve convexity; multiplying decision variables or imposing nonconvex equalities can break it. Convexity concerns computational geometry, not whether the objective measures the right operational value.

### stat-36-06

**Nonconvex optimization**

Nonconvex optimization includes multiple local minima, saddle points or disconnected feasible regions. Initialization, scaling and algorithm choice can affect the returned solution. Multiple starts and global bounds can provide evidence, but a local solver success flag is not a global certificate. Compare feasible alternatives and sensitivity, and state whether the result is locally optimal, approximately optimal or merely the best found.

### stat-36-07

**Lagrange multipliers**

Lagrange multipliers incorporate constraints into an augmented objective so feasible optimality can be characterized through derivatives. For equality constraints multipliers are unrestricted; inequality sign conventions determine multiplier signs. A multiplier can quantify local sensitivity to a bound under regularity. Redundant constraints or degenerate optima can make that interpretation nonunique, so avoid treating every reported multiplier as a definitive shadow price.

### stat-36-08

**Karush–Kuhn–Tucker conditions**

KKT conditions combine feasibility, nonnegative inequality multipliers, stationarity of the Lagrangian and complementary slackness. They are necessary under constraint qualifications and sufficient for suitable convex problems. Complementary slackness means an inactive inequality has zero multiplier, not that every active constraint must have a positive multiplier. Checking residuals helps diagnose a solver result but cannot certify a nonconvex global optimum alone.

### stat-36-09

**Duality**

Duality constructs a companion problem whose feasible values bound the primal optimum under a defined sign convention. Weak duality holds broadly; strong duality needs additional conditions. A small primal-dual gap can certify near-optimality when both sides are feasible. If a gap remains, distinguish true nonzero duality gap from numerical or convergence error.

### stat-36-10

**Gradient descent**

Gradient descent updates x toward minus the objective gradient. Step size determines whether the method progresses, oscillates or diverges, and scaling changes the effective geometry. A decreasing objective does not necessarily mean constraints remain feasible unless the method accounts for them. Monitor gradient or stationarity criteria and validation behavior when the optimized objective is a statistical training loss.

### stat-36-11

**Stochastic gradient descent**

Stochastic gradient descent uses a noisy gradient estimate from sampled observations or minibatches. Sampling design, learning-rate schedule and batch size affect variance and convergence. An unbiased gradient estimate can still have high variance, while data ordering and dependent batches can change behavior. Record the optimizer state and random seed for reproducibility, and assess the held-out task separately from training loss.

### stat-36-12

**Newton and quasi-Newton methods**

Newton methods use the Hessian to account for local curvature; quasi-Newton methods approximate curvature from gradient changes. These can converge rapidly near a suitable optimum but may need damping or trust regions when curvature is indefinite or the initial point is poor. Solving the linear system and computing derivatives can dominate cost. Verify gradient correctness before blaming the optimizer.

### stat-36-13

**Coordinate descent**

Coordinate descent optimizes one variable or block at a time while holding others fixed. It is effective when each subproblem has a cheap update, as in some penalized regression problems. Strong coupling among variables can slow progress, and coordinate-wise stationarity need not imply global optimality in a nonconvex problem. Variable scaling and update order can affect practical performance.

### stat-36-14

**Proximal optimization**

Proximal methods handle objectives combining a smooth loss with a nonsmooth penalty. A gradient step is followed by a proximal operator, such as soft-thresholding for an L1 penalty. The threshold depends on both penalty strength and step size. This is different from arbitrarily clipping coefficients after fitting. Check the objective and optimality conditions appropriate to the composite problem.

### stat-36-15

**Constrained optimization**

Constrained optimization encodes limits such as capacity, fairness budgets, physical feasibility or permissible actions. A penalty term can approximate a constraint but may permit violations when the objective gain is large. Mandatory constraints should have an explicit feasibility check. Tolerances need meaningful units, because a numerically small violation can still be operationally important.

### stat-36-16

**Multiobjective optimization**

Multiobjective optimization considers several goals that cannot be reduced to one universally agreed scale, such as cost, latency and quality. Weighted sums express a particular preference and can miss some nonconvex frontier points. Present tradeoffs and constraints transparently. Changing weights after seeing the solutions can be a legitimate decision discussion, but it should not be hidden as a uniquely objective optimum.

### stat-36-17

**Pareto frontiers**

A Pareto frontier contains feasible decisions for which no objective can improve without worsening another. Dominance depends on the chosen objectives and their direction. Frontier membership does not select the final decision; stakeholders still need preferences or constraints. Approximate solvers and uncertain objective estimates can make apparent frontier differences unreliable, so report uncertainty and practical significance.

### stat-36-18

**Stochastic programming**

Stochastic programming optimizes expected or risk-adjusted outcomes across explicit random scenarios, often with recourse decisions after uncertainty is observed. The scenario tree defines what is known when each decision is made. Allowing future information too early creates an unrealistically favorable solution. Validate scenario probabilities, dependence and out-of-sample performance rather than only the training-scenario objective.

### stat-36-19

**Robust optimization**

Robust optimization protects against all parameter values in a specified uncertainty set. Larger sets provide stronger worst-case protection but can produce conservative or costly decisions. The set should reflect plausible joint uncertainty, not an arbitrary independent range for every coefficient. A robust guarantee applies only to the modeled set and constraints; it does not cover unknown failure mechanisms automatically.

### stat-36-20

**Distributionally robust optimization**

Distributionally robust optimization optimizes against a family of probability distributions, such as distributions within a divergence or transport distance of empirical data. The ambiguity set encodes uncertainty about the data-generating distribution. Its radius and geometry determine conservatism and finite-sample claims. A mathematically robust solution can be misleading if the ambiguity set excludes the relevant deployment shift.

### stat-36-21

**Chance-constrained optimization**

Chance constraints require a condition to hold with probability at least one minus alpha under a specified distribution. Individual chance constraints do not automatically imply the same joint guarantee across many constraints. Tail estimation, dependence and model misspecification matter. Replacing a hard safety constraint with a probabilistic one is a substantive policy choice, not merely a solver convenience.

### stat-36-22

**Bayesian optimization**

Bayesian optimization selects evaluations of an expensive objective using a probabilistic surrogate and an acquisition function. It balances promising values with uncertainty, often under a small evaluation budget. The surrogate kernel, noise model and search space constrain what can be learned. Optimizing validation performance repeatedly can overfit that validation set, so retain a separate final test or nested evaluation.

### stat-36-23

**Optimal transport**

Optimal transport finds a coupling that moves mass between distributions at minimum cost. The ground cost encodes what changes are expensive, and mass constraints define which distributions are matched. Entropic regularization improves computation while changing the exact objective. Applications to distribution comparison or adaptation need a defensible feature geometry; a small transport distance is not automatically a small task-performance change.

### stat-36-24

**Assignment and matching optimization**

Assignment and matching optimization allocates entities to distinct opportunities using a cost or utility matrix and constraints. A standard one-to-one assignment differs from many-to-one matching, quotas or fairness-constrained allocation. Recompute the selected total and uniqueness conditions. The solution is only as meaningful as the cost matrix, which may itself be estimated with substantial uncertainty.

### stat-36-25

**Scheduling and routing**

Scheduling and routing choose timing, sequencing or paths under resource and service constraints. Travel times, precedence, capacity and time windows create different problem classes. A feasible static plan may fail when durations are uncertain or tasks arrive dynamically. Distinguish an offline optimal schedule from a policy for real-time disruptions, and retain slack or recourse when operational variability matters.

### stat-36-26

**Queueing theory**

Queueing theory relates arrivals, service and congestion. In an M/M/1 queue with arrival rate lambda below service rate mu, mean system time is \(\frac{1}{\mu-\lambda}\), showing nonlinear growth near full utilization. The model assumes Poisson arrivals and exponential independent service times. Real burstiness, priorities and multiple servers require other models or simulation, but the utilization lesson remains important.

### stat-36-27

**Inventory optimization**

Inventory optimization balances holding, shortage and replenishment costs under demand and lead-time uncertainty. In a simple newsvendor model, the optimal quantile depends on underage and overage costs. Censored sales and nonstationary demand can distort the estimated demand distribution. A forecast chosen for low RMSE may not minimize inventory cost, so align the predictive target and operational decision.

## Worked Python demonstrations

Complete offline program: [chapter_36.py](../examples/chapter_36.py). It uses tiny fixtures, no downloads, and assertions that check the expected observations. Run from the repository root:

```text
python courses/statistics-ml/examples/chapter_36.py
```

### Verify an actual solver result

Maximize 3x+2y with \(x+y\le 4\), \(x\le 2\), \(y\le 3\) and nonnegative decisions. Negating the objective adapts it to SciPy's minimization API. The optimum is [2,2] with value ten; the code recomputes all constraint slacks and the objective. Solver success is checked before reading the solution.

### Read a binding constraint through KKT conditions

Minimizing \({\left(x-3\right)}^{2}\) subject to \(x\le 2\) gives \(x=2\). The Lagrangian derivative is 2(x-3)+lambda, so \(\lambda=2\) makes stationarity zero. Feasibility, nonnegative multiplier and complementary slackness also hold. This small convex example makes the certificate visible rather than relying on a status string.

### Connect allocation and congestion to decisions

The two-by-two assignment selects cross-pairs at total cost three instead of diagonal cost seven. Separately, an M/M/1 queue with arrival rate eight and service rate ten has mean system time one-half and mean number four. Raising utilization closer to one increases waiting nonlinearly under this model, so maximizing utilization alone is not a service-quality objective.

### Complete executable example

```python
import numpy as np
from scipy.optimize import linprog, linear_sum_assignment


def resource_allocation():
    objective = np.array([-3.0, -2.0])
    a = np.array([[1.0, 1.0], [1.0, 0.0], [0.0, 1.0]])
    b = np.array([4.0, 2.0, 3.0])
    result = linprog(objective, A_ub=a, b_ub=b, bounds=(0, None), method="highs")
    assert result.success and np.all(a @ result.x <= b + 1e-9)
    assert np.allclose(result.x, [2.0, 2.0]) and np.isclose(-result.fun, 10.0)
    print("Allocation:", result.x, "profit:", -result.fun, "slack:", b - a @ result.x)


def kkt_trace():
    x = 2.0
    multiplier = 2.0
    stationarity = 2 * (x - 3) + multiplier
    constraint = x - 2
    assert (
        stationarity == 0 and constraint <= 0 and multiplier >= 0 and multiplier * constraint == 0
    )
    print("Constrained quadratic optimum, multiplier:", x, multiplier)


def assignment_and_queue():
    cost = np.array([[4.0, 1.0], [2.0, 3.0]])
    rows, cols = linear_sum_assignment(cost)
    assert cols.tolist() == [1, 0] and cost[rows, cols].sum() == 3.0
    arrival, service = 8.0, 10.0
    waiting_system = 1 / (service - arrival)
    number_system = arrival * waiting_system
    assert waiting_system == 0.5 and number_system == 4.0
    print(
        "Assignment cost:",
        cost[rows, cols].sum(),
        "M/M/1 time and count:",
        waiting_system,
        number_system,
    )


def main():
    resource_allocation()
    kkt_trace()
    assignment_and_queue()


if __name__ == "__main__":
    main()
```

## Data science interview discussions

**Interview: What should you inspect after a solver reports success?** Recompute objective and constraints in original units, check integrality and tolerances, inspect termination and optimality evidence, and compare with a simple feasible baseline. A correctly solved wrong model is still a wrong decision.

**Interview: Is a penalty equivalent to a hard constraint?** Not generally. A finite penalty trades violation against objective improvement. If a boundary is mandatory, enforce and verify feasibility explicitly or prove that the chosen formulation is equivalent under stated conditions.

**Interview: Why can optimizing expected demand be suboptimal?** Cost can be nonlinear and asymmetric, so cost at expected demand differs from expected cost. Scenario or distributional modeling preserves the uncertainty relevant to shortage and excess decisions.

## Primary sources and official APIs

- [Boyd and Vandenberghe, Convex Optimization](https://web.stanford.edu/~boyd/cvxbook/)

- [SciPy linprog](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html)

- [SciPy linear sum assignment](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html)

## Connected worked tutorial

[Resource allocation under effect uncertainty](../tutorials/science/05-ranking-policy-and-allocation.md). Compare expected-value and conservative allocation scenarios while preserving feasibility and intervention meaning.

## Reading connections

[Previous chapter](35-bandits-reinforcement-learning-and-adaptive-decisions.md) | [Book contents](../README.md) | [Next chapter](37-simulation-and-computational-statistics.md)
