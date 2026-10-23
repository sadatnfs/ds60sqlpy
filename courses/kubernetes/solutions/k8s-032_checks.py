def budget(healthy,minimum):return max(0,healthy-minimum)

def main():
    assert [budget(n,1) for n in (2,1,0)]==[1,0,0]
    pods=[{'app':'hello','ready':True},{'app':'hello','ready':True},{'app':'other','ready':True}]
    assert sum(p['ready'] for p in pods if p['app']=='hello')==2
    protected={'eviction':True,'direct-delete':False,'node-loss':False}
    assert protected['eviction'] and not protected['node-loss']
    print('k8s-032 synthetic budget passed; no eviction or drain performed')

if __name__ == "__main__":
    main()
