def main():
    def millicores(value):
        return int(value.removesuffix("m"))

    def mebibytes(value):
        return int(value.removesuffix("Mi"))

    requests = {"cpu": "10m", "memory": "16Mi"}
    limits = {"cpu": "100m", "memory": "64Mi"}
    replicas = 2
    total_cpu = replicas * millicores(requests["cpu"])
    total_memory = replicas * mebibytes(requests["memory"])
    assert (total_cpu, total_memory) == (20, 32) and mebibytes(limits["memory"]) * 2**20 == 67108864
    quota = {"cpu_m": 300, "memory_mi": 256, "pods": 3}
    assert (
        total_cpu <= quota["cpu_m"]
        and total_memory <= quota["memory_mi"]
        and replicas <= quota["pods"]
    )
    scratch = {"request": "200m", "limit": "100m"}
    assert millicores(scratch["request"]) > millicores(scratch["limit"])
    phases = {
        "Forbidden/exceeded quota": "admission",
        "FailedScheduling/Insufficient cpu": "scheduling",
        "OOMKilled": "runtime",
    }
    assert len(set(phases.values())) == 3
    print("k8s-010 synthetic unit, budget and failure-phase checks passed")


if __name__ == "__main__":
    main()
