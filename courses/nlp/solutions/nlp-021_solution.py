import hashlib
import numpy as np

ROWS=[{"id":"a1","family":"a","time":1,"text":"Reset the router"},
      {"id":"a2","family":"a","time":2,"text":"reset  the router"},
      {"id":"b1","family":"b","time":1,"text":"Payment failed"},
      {"id":"b2","family":"b","time":3,"text":"Payment failed again"},
      {"id":"c1","family":"c","time":3,"text":"Account updated"}]

def normalized_hash(text):
    normalized=" ".join(text.casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()

def jaccard(a,b):
    a=set(a.casefold().split());b=set(b.casefold().split())
    return len(a&b)/len(a|b) if a|b else 1.

def future_new_families(rows,cutoff):
    train=[row for row in rows if row['time']<=cutoff]
    known={row['family'] for row in train}
    test=[row for row in rows if row['time']>cutoff and row['family'] not in known]
    excluded=[row for row in rows if row['time']>cutoff and row['family'] in known]
    return train,test,excluded

def family_bootstrap(deltas,seed=21,repeats=200):
    means=np.array([np.mean(deltas[key]) for key in sorted(deltas)])
    if not len(means):raise ValueError("families required")
    rng=np.random.default_rng(seed)
    sampled=rng.choice(means,size=(repeats,len(means)),replace=True).mean(axis=1)
    return float(means.mean()),np.quantile(sampled,[.025,.975])

def main():
    assert normalized_hash(ROWS[0]['text'])==normalized_hash(ROWS[1]['text'])
    assert normalized_hash("service ready")!=normalized_hash("service not ready")
    assert jaccard("service is ready","service is not ready")==.75
    train,test,excluded=future_new_families(ROWS,2)
    assert [r['id'] for r in train]==['a1','a2','b1'] and [r['id'] for r in test]==['c1']
    assert [r['id'] for r in excluded]==['b2']
    assert max(r['time'] for r in train)<min(r['time'] for r in test)
    assert {r['family'] for r in train}.isdisjoint({r['family'] for r in test})
    deltas={'a':[.2,.2],'b':[-.1],'c':[.3,.3,.3]}
    estimate,interval=family_bootstrap(deltas)
    repeat=family_bootstrap(deltas)
    assert np.isclose(estimate,2/15) and np.allclose(interval,repeat[1])
    assert interval[0]>=-.1-1e-12 and interval[1]<=.3+1e-12
    row_mean=np.mean([x for values in deltas.values() for x in values])
    assert np.isclose(row_mean,.2) and not np.isclose(row_mean,estimate)
    print("nlp-021: duplicate hash, semantic near-miss, temporal/family split and clustered comparison passed")

if __name__ == "__main__":
    main()
