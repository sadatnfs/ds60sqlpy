import numpy as np


def bellman_and_q():
    terminal = 0.0
    v_second = 2.0 + 0.9 * terminal
    v_first = 1.0 + 0.9 * v_second
    assert np.isclose(v_first, 2.8)
    old_q = 0.0
    alpha = 0.5
    target = 1.0 + 0.9 * 2.0
    updated = old_q + alpha * (target - old_q)
    assert np.isclose(updated, 1.4)
    print("Two-step value:", v_first, "one Q update:", updated)


def importance_weighting():
    action = np.array([0, 1, 0, 1])
    reward = np.array([0.0, 1.0, 0.0, 1.0])
    behavior = np.full(4, 0.5)
    target = (action == 1).astype(float)
    weights = target / behavior
    estimate = np.mean(weights * reward)
    assert weights.tolist() == [0.0, 2.0, 0.0, 2.0] and estimate == 1.0
    assert np.all(behavior > 0)
    print("Logged mean:", reward.mean(), "target-policy estimate:", estimate)


def reward_proxy():
    proxy = np.array([0.6, 0.99])
    real_utility = np.array([0.7, 0.1])
    selected = int(np.argmax(proxy))
    best = int(np.argmax(real_utility))
    assert selected == 1 and best == 0 and real_utility[selected] < real_utility[best]
    print("Proxy selects action", selected, "but true-utility best is", best)


def main():
    bellman_and_q()
    importance_weighting()
    reward_proxy()


if __name__ == "__main__":
    main()
