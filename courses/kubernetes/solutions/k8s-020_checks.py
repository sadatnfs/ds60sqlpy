def classify(trace):
    if trace.get('dns')=='NXDOMAIN':return 'name-resolution'
    if trace.get('connected') is False:return 'transport-or-backend-unresolved'
    if trace.get('http')==404:return 'route'
    if trace.get('http')==200 and trace.get('body')!='ds60-fixture-v1':return 'application-contract'
    return 'insufficient-evidence'

def main():
    traces=[{'dns':'NXDOMAIN'},{'dns':'resolved','connected':False},{'http':404},{'http':200,'body':'wrong'}]
    assert [classify(x) for x in traces]==['name-resolution','transport-or-backend-unresolved','route','application-contract']
    print('k8s-020 synthetic layered-diagnosis checks passed; no network probes performed')

if __name__ == "__main__":
    main()
