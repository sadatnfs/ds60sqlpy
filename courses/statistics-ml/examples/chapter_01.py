import numpy as np


def compare_units():
    delays = np.array([1.0, 1.0, 1.0, 9.0])
    customer = np.array([0, 0, 0, 1])
    per_request = delays.mean()
    per_customer = np.mean([delays[customer == k].mean() for k in [0, 1]])
    assert per_request == 3 and per_customer == 5
    print("Request mean:", per_request, "customer mean:", per_customer)


def choose_action():
    probability = np.array([0.1, 0.3, 0.8])
    false_alarm_cost, miss_cost = 2.0, 8.0
    threshold = false_alarm_cost / (false_alarm_cost + miss_cost)
    intervene = probability > threshold
    assert intervene.tolist() == [False, True, True]
    assert np.all(np.minimum(2 * (1 - probability), 8 * probability) <= 8 * probability)
    print("Loss-derived threshold:", threshold, "intervene:", intervene.tolist())


def main():
    compare_units()
    choose_action()


if __name__ == "__main__":
    main()
