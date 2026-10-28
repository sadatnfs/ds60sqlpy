"""Deterministic queue and scan-cost models with declared units, not runtime benchmarks."""

import heapq
import math


def schedule(arrivals, service, workers):
    if type(workers) is not int or workers < 1 or not math.isfinite(service) or service <= 0:
        raise ValueError("Use positive finite service time and worker capacity")
    if not arrivals or len(arrivals) > 100 or any(not math.isfinite(t) or t < 0 for t in arrivals):
        raise ValueError("Use a bounded nonempty nonnegative arrival trace")
    available = [0.0] * workers
    heapq.heapify(available)
    records = []
    for request, arrival in sorted(enumerate(arrivals), key=lambda item: (item[1], item[0])):
        free = heapq.heappop(available)
        start = max(free, arrival)
        finish = start + service
        heapq.heappush(available, finish)
        records.append(
            {
                "id": request,
                "arrival": arrival,
                "start": start,
                "finish": finish,
                "latency": finish - arrival,
                "waiting": start - arrival,
            }
        )
    return records


def percentile(values, probability):
    if not values or not 0 < probability <= 1:
        raise ValueError("Use a nonempty sample and probability in (0,1]")
    return sorted(values)[math.ceil(probability * len(values)) - 1]


def example_one():
    steady = schedule([i / 10 for i in range(20)], 0.1, 4)
    burst = schedule([0.0] * 20, 0.1, 4)
    steady_p95 = percentile([r["latency"] for r in steady], 0.95)
    burst_p95 = percentile([r["latency"] for r in burst], 0.95)
    assert math.isclose(steady_p95, 0.1) and math.isclose(burst_p95, 0.5)
    assert math.isclose(max(row["waiting"] for row in burst), 0.4)
    return {
        "requests_in_declared_two_second_window": 20,
        "mean_arrivals_per_second": 10,
        "workers": 4,
        "service_seconds": 0.1,
        "average_offered_utilization": 0.25,
        "steady_p95_seconds": steady_p95,
        "burst_p95_seconds": burst_p95,
        "same_average_does_not_determine_tail_latency": True,
    }


def scan_model(partitions, files_per_partition, megabytes_per_file):
    if any(
        type(v) is not int or v < 1 for v in [partitions, files_per_partition, megabytes_per_file]
    ):
        raise ValueError("Use positive integer layout quantities")
    files = partitions * files_per_partition
    megabytes = files * megabytes_per_file
    return {
        "files": files,
        "megabytes": megabytes,
        "modeled_serial_seconds": files * 0.002 + megabytes / 500 + 0.05,
        "illustrative_cost_units": megabytes / 1000 * 0.02,
    }


def example_two():
    full, selected = scan_model(30, 20, 5), scan_model(1, 20, 5)
    assert full["megabytes"] == 3000 and selected["megabytes"] == 100
    assert math.isclose(full["modeled_serial_seconds"], 7.25)
    assert math.isclose(selected["modeled_serial_seconds"], 0.29)
    return {
        "all_partitions": full,
        "one_partition": selected,
        "byte_amplification": 30,
        "assumptions": "serial 2 ms/file + 500 MB/s transfer + 50 ms fixed work; decimal MB",
        "no_real_prices_or_measured_speedup": True,
    }


def main():
    from ds60sqlpy.plot_artifacts import publish_report, publish_table

    first, second = example_one(), example_two()
    print("Average load misses a burst:", first)
    print("A declared scan-layout model:", second)
    publish_table(
        ["scenario", "p95_seconds"],
        [["steady", first["steady_p95_seconds"]], ["burst", first["burst_p95_seconds"]]],
        description=(
            "Deterministic queue model with four workers and 0.1 second "
            "service: steady p95 is 0.1 seconds; burst p95 is 0.5 seconds."
        ),
    )
    publish_report(
        second,
        description=(
            "Illustrative scan accounting with stated file, byte, bandwidth "
            "and cost units; no actual benchmark or price quote."
        ),
    )


if __name__ == "__main__":
    main()
