APPROVED='ds60sqlpy-k8s-fixture:0.2.0'
def allowed(containers):return all(c['image']==APPROVED for c in containers)

def main():
    assert allowed([{'image':APPROVED}])
    assert not allowed([{'image':APPROVED},{'image':'unapproved:0'}])
    layers={'local rejection':'source parser','policy denial':'API admission','ImagePullBackOff':'runtime'}
    assert len(set(layers.values()))==3
    print('k8s-031 predicate examples passed; no CEL evaluator or API admission invoked')

if __name__ == "__main__":
    main()
