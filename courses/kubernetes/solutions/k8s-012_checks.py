def diagnose(record):
    if record.get('waiting')=='CreateContainerConfigError':return 'configuration'
    if record.get('probe_path')=='/missing' and record.get('http')==404:return 'readiness-path'
    if record.get('job_condition')=='Failed' and record.get('exit')==2:return 'finite-task'
    return 'insufficient-evidence'

def main():
    cases=[{'waiting':'CreateContainerConfigError'},{'probe_path':'/missing','http':404},{'job_condition':'Failed','exit':2}]
    assert [diagnose(x) for x in cases]==['configuration','readiness-path','finite-task']
    assert diagnose({'phase':'Running'})=='insufficient-evidence'
    print('k8s-012 synthetic triage checks passed; no live incident was inspected')

if __name__ == "__main__":
    main()
