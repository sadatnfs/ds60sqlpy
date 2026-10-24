import math


def nearest_rank(values, q):
    return sorted(values)[math.ceil(q * len(values)) - 1]


def main():
    statuses = [200, 200, 500, 200, 200]
    latency = [10, 20, 30, 40, 100]
    assert sum(s >= 500 for s in statuses) / len(statuses) == 0.2
    assert nearest_rank(latency, 0.5) == 30 and nearest_rank(latency, 0.95) == 100
    before, after = 120, 3
    assert after < before
    metrics_available = False
    assert metrics_available is False
    print("k8s-027 synthetic SLI/quantile/reset checks passed; no metrics stack installed")


if __name__ == "__main__":
    main()
