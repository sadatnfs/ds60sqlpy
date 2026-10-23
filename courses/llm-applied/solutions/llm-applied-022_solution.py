"""llm-applied-022: bounded local reference checks. No network or persistent data writes."""

import math
from collections import defaultdict

def dispatch(request,rows):
    if not isinstance(request,dict) or set(request)!={'operation','group_by','value'}: raise ValueError('exact tool fields required')
    if request!={'operation':'group_mean','group_by':'group','value':'value'}: raise ValueError('operation or columns not allowed')
    if not 1<=len(rows)<=20: raise ValueError('row budget1..20 required')
    if len({row['id'] for row in rows})!=len(rows): raise ValueError('duplicate row ID')
    groups=defaultdict(list)
    for row in rows:
        if set(row)!={'id','group','value'} or not isinstance(row['id'],str) or not isinstance(row['group'],str): raise ValueError('row schema')
        value=row['value']
        if type(value) not in (int,float): raise TypeError('numeric value required')
        if not math.isfinite(value): raise ValueError('finite value required')
        groups[row['group']].append(value)
    return [{'group':key,'count':len(values),'mean':sum(values)/len(values)} for key,values in sorted(groups.items())]


def verify():
    # Exercise 1: Execute a bounded grouped mean
    rows=[{'id':'a1','group':'A','value':1.},{'id':'a2','group':'A','value':3.},{'id':'b1','group':'B','value':10.}]
    request={'operation':'group_mean','group_by':'group','value':'value'}
    result=dispatch(request,rows)
    assert result==[{'group':'A','count':2,'mean':2.},{'group':'B','count':1,'mean':10.}]

    # Exercise 2: Reject an arbitrary operation
    for proposal in [{'operation':'run_sql','group_by':'group','value':'value'},{**request,'query':'DROP TABLE anything'}]:
        try: dispatch(proposal,rows)
        except ValueError: pass
        else: raise AssertionError('unbounded operation accepted')

    # Exercise 3: Reject invalid numeric values
    for bad in [True,float('nan'),None]:
        changed=[dict(r) for r in rows]; changed[0]['value']=bad
        try: dispatch(request,changed)
        except (TypeError,ValueError): pass
        else: raise AssertionError('invalid numeric value accepted')

    # Exercise 4: Enforce identity and work limits
    too_many=[{'id':str(i),'group':'A','value':1.} for i in range(21)]
    for bad_rows in [rows+[dict(rows[0])],too_many]:
        try: dispatch(request,bad_rows)
        except ValueError: pass
        else: raise AssertionError('identity or budget ignored')

    # Exercise 5: Verify an explanation against the artifact
    lookup={r['group']:r for r in result}
    assert lookup['A']['mean']==2 and lookup['A']['mean']!=20

    # Exercise 6: Refuse an unsupported causal interpretation
    report={'group_means':result,'random_assignment_verified':False,'causal_effect_established':False}
    assert report['group_means'] and not report['causal_effect_established']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
