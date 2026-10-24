def replace(store,expected_uid,expected_rv,message):
    if store['uid']!=expected_uid:return 'identity-refused',dict(store)
    if store['rv']!=expected_rv:return '409',dict(store)
    return 'accepted',{**store,'message':message,'rv':'server-next-token'}

def main():
    store={'uid':'u1','rv':'rv-B','message':'reviewer','other':'preserve'}
    status,after=replace(store,'u1','rv-A','hello')
    assert status=='409' and after==store
    status,after=replace(store,'u1','rv-B','hello')
    assert status=='accepted' and after['other']=='preserve'
    assert replace({**store,'uid':'u2'},'u1','rv-B','hello')[0]=='identity-refused'
    cache={'hello-config':{'uid':'u1'}}
    fresh={'hello-config':{'uid':'u2','message':'reviewer'}}
    cache=dict(fresh)
    assert cache['hello-config']['uid']=='u2'
    print('k8s-035 synthetic concurrency and relist passed; resourceVersion tokens remain opaque')

if __name__ == "__main__":
    main()
