import numpy as np


def differencing_trace():
    t = np.arange(16, dtype=float)
    seasonal = np.tile([0.0, 2.0, 0.0, -2.0], 4)
    y = 10 + 3 * t + seasonal
    seasonal_difference = y[4:] - y[:-4]
    assert np.allclose(seasonal_difference, 12.0)
    assert np.allclose(np.diff(seasonal_difference), 0.0)
    print(
        "Seasonal difference:",
        seasonal_difference[:4],
        "then first difference:",
        np.diff(seasonal_difference)[:3],
    )


def frequency_trace():
    t = np.arange(32, dtype=float)
    y = np.sin(2 * np.pi * t / 8)
    power = np.abs(np.fft.rfft(y - y.mean())) ** 2
    frequency = np.fft.rfftfreq(len(y), d=1.0)
    peak = frequency[np.argmax(power[1:]) + 1]
    assert np.isclose(peak, 1 / 8)
    print("Peak cycles per observation:", peak, "period:", 1 / peak)


def information_order():
    event_time = np.array([1, 2, 3, 4])
    available_time = np.array([1, 3, 3, 5])
    origin = 3
    allowed = (event_time <= origin) & (available_time <= origin)
    assert allowed.tolist() == [True, True, True, False]
    y = np.array([10.0, 12.0, 15.0, 18.0])
    lag1 = np.r_[np.nan, y[:-1]]
    assert lag1[3] == 15 and lag1[3] != y[3]
    print(
        "Available rows at origin 3:", np.flatnonzero(allowed), "lagged feature at time 4:", lag1[3]
    )


def main():
    differencing_trace()
    frequency_trace()
    information_order()


if __name__ == "__main__":
    main()
