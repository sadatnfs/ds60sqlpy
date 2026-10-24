CONTROLS={'foreign-namespace':'lease+RBAC','privileged':'schema+admission','hostPath':'schema+admission','unapproved-image':'schema+image-allowlist','foreign-service-account':'schema+RBAC','shell':'fixed-command'}

def owned(expected,obj):return all(obj.get(k)==v for k,v in expected.items())

def main():
    assert len(CONTROLS)==6 and all(CONTROLS.values())
    expected={'uid':'u1','nonce':'n1','owner':'lesson'}
    assert owned(expected,dict(expected))
    assert not owned(expected,{**expected,'uid':'u2'})
    assert not owned(expected,{**expected,'nonce':'foreign'})
    print('k8s-039 threat mapping and identity model passed; no adversarial workload executed')

if __name__ == "__main__":
    main()
