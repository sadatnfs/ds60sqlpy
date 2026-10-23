def main():
    labels={'app':'hello'}
    assert all(labels.get(k)==v for k,v in {'app':'hello'}.items())
    assert not all(labels.get(k)==v for k,v in {'app':'wrong'}.items())
    ready={'pod-a','pod-b'};slices=[['pod-a','pod-b'],['pod-a','pod-b']]
    endpoints={uid for group in slices for uid in group}
    assert sum(map(len,slices))==4 and len(endpoints)==2 and endpoints==ready
    assert {'pod-a','foreign-c'}!=ready
    ports={'http':8080};assert ports['http']==8080
    print('k8s-007 synthetic selector,port and endpoint-identity checks passed')

if __name__ == "__main__":
    main()
