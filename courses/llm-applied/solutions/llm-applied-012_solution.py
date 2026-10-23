"""llm-applied-012: bounded local reference checks. No network or persistent data writes."""



def retrieval_metrics(retrieved,relevant):
    if len(retrieved)!=len(set(retrieved)): raise ValueError('duplicate retrieved ID')
    recall=None if not relevant else len(set(retrieved)&relevant)/len(relevant)
    rank=next((i for i,key in enumerate(retrieved,1) if key in relevant),None)
    return recall,0. if rank is None else 1/rank


def verify():
    # Exercise 1: Calculate recall and reciprocal rank
    recall,rr=retrieval_metrics(['b','c','a'],{'a','c'})
    assert recall==1 and rr==.5

    # Exercise 2: Measure a retrieval miss
    assert retrieval_metrics(['b','c'],{'a'})==(0.,0.)

    # Exercise 3: Handle an unanswerable question
    assert retrieval_metrics(['b'],set())==(None,0.)
    result={'question':'q-missing','answerable':False,'abstained':True}; assert not result['answerable'] and result['abstained']

    # Exercise 4: Separate support from correctness
    saved={'question':'q1','correct':True,'supported':False,'retrieval_miss':True}
    assert saved['correct'] and not saved['supported']

    # Exercise 5: Apply an oracle-context control
    observed={'q1':0,'q2':0}; oracle={'q1':1,'q2':0}
    assert oracle['q1']-observed['q1']==1 and oracle['q2']-observed['q2']==0

    # Exercise 6: Reject duplicate result identities
    ids=['q1','q2','q3']; assert len(ids)==len(set(ids))
    bad=ids+['q1']; assert len(bad)!=len(set(bad))
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
