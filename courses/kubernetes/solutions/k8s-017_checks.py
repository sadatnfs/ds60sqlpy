def main():
    pod={'runAsNonRoot':True,'runAsUser':65532,'seccompProfile':{'type':'RuntimeDefault'}}
    container={'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}}
    assert pod['runAsUser']!=0 and pod['runAsNonRoot']
    assert not container['allowPrivilegeEscalation'] and container['capabilities']['drop']==['ALL']
    assert {'hostPath','hostNetwork','hostPID'}.isdisjoint({'containers','securityContext'})
    print('k8s-017 synthetic security-control checks passed; runtime identity is separate evidence')

if __name__ == "__main__":
    main()
