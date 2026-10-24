def review(objects):
    for obj in objects:
        if obj['kind'] not in {'Deployment','Service','ConfigMap'}:return False
        if 'helm.sh/hook' in obj.get('metadata',{}).get('annotations',{}):return False
    return True

def main():
    assert review([{'kind':'Deployment','metadata':{'name':'hello'}}])
    assert not review([{'kind':'Job','metadata':{'annotations':{'helm.sh/hook':'post-install'}}}])
    assert not review([{'kind':'ClusterRole','metadata':{'name':'wide'}}])
    assert 1 in {1,2} and 3 not in {1,2}
    print('k8s-025 synthetic rendered-object review passed; Helm execution is separate')

if __name__ == "__main__":
    main()
