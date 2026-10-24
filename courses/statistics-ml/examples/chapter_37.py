import numpy as np


def control_and_antithetic():
    rng = np.random.default_rng(37)
    u = rng.uniform(size=20000)
    raw = u**2
    controlled = raw - (u - 0.5)
    raw_se = raw.std(ddof=1) / np.sqrt(len(u))
    controlled_se = controlled.std(ddof=1) / np.sqrt(len(u))
    assert abs(raw.mean() - 1 / 3) < 0.01 and abs(controlled.mean() - 1 / 3) < 0.01
    assert controlled_se < raw_se / 3
    antithetic = (u + (1 - u)) / 2
    assert np.allclose(antithetic, 0.5)
    print("Means and MC standard errors:", raw.mean(), controlled.mean(), raw_se, controlled_se)


def queue_conservation():
    arrivals = np.array([0.0, 0.5, 1.5])
    service = np.array([1.0, 1.0, 1.0])
    departure = []
    previous = 0.0
    for arrival, duration in zip(arrivals, service):
        previous = max(arrival, previous) + duration
        departure.append(previous)
    waits = np.array(departure) - arrivals - service
    assert np.allclose(departure, [1.0, 2.0, 3.0]) and np.allclose(waits, [0.0, 0.5, 0.5])
    observed_time = 2.5
    arrived = np.sum(arrivals <= observed_time)
    left = np.sum(np.array(departure) <= observed_time)
    assert arrived == 3 and left == 2 and arrived - left == 1
    print("Departures:", departure, "queue waits:", waits, "remaining at 2.5:", arrived - left)


def perfect_information():
    payoff = np.array([[8.0, -2.0], [2.0, 4.0]])  # rows decisions, columns equally probable states
    current = np.max(payoff.mean(axis=1))
    informed = np.mean(np.max(payoff, axis=0))
    evpi = informed - current
    assert current == 3.0 and informed == 6.0 and evpi == 3.0
    print("Current value, perfect-information value, EVPI:", current, informed, evpi)


def main():
    control_and_antithetic()
    queue_conservation()
    perfect_information()


if __name__ == "__main__":
    main()
