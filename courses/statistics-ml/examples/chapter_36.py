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
