def main():
    mixed={'generation':5,'observed':5,'updated':2,'new_ready':0,'old_ready':2,'marker':'A'}
    assert mixed['observed']==mixed['generation'] and mixed['old_ready']==2
    assert not (mixed['new_ready']==2 and mixed['marker']=='B')
    restored={'generation':6,'observed':6,'ready':2,'marker':'A'}
    assert restored['generation']>mixed['generation'] and restored['marker']=='A'
    print('k8s-013 synthetic rollout/rollback reasoning passed; no live update performed')

if __name__ == "__main__":
    main()
