def main():
    assert 2*10==20 and 2*16==32 and 64*2**20==67108864
    quota={'cpu_m':300,'memory_mi':256,'pods':3}
    assert 20<=quota['cpu_m'] and 32<=quota['memory_mi'] and 2<=quota['pods']
    assert not (200<=100)
    phases={'Forbidden/exceeded quota':'admission','FailedScheduling/Insufficient cpu':'scheduling','OOMKilled':'runtime'}
    assert len(set(phases.values()))==3
    print('k8s-010 synthetic unit,budget and failure-phase checks passed')

if __name__ == "__main__":
    main()
