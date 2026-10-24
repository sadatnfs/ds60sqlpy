"""llm-applied-002: bounded local reference checks. No network or persistent data writes."""

import re

def validate(value):
    if not isinstance(value,dict): raise TypeError('object required')
    if set(value)!={'visits','purchases','assignment_unit'}: raise ValueError('exact fields required')
    if any(type(value[k]) is not int for k in ('visits','purchases')): raise TypeError('integer counts required')
    if not 0<=value['purchases']<=value['visits']: raise ValueError('inconsistent counts')
    if value['assignment_unit']!='account': raise ValueError('account assignment required')
    return dict(value)
def rate(record):
    if record['visits']==0: raise ValueError('positive denominator required')
    return record['purchases']/record['visits']
def extract(text):
    match=re.fullmatch(r'Visits: (\d+); Purchases: (\d+); Unit: (account)',text)
    if match is None: raise ValueError('unsupported source grammar')
    result=validate({'visits':int(match[1]),'purchases':int(match[2]),'assignment_unit':match[3]})
    return result,{name:match.span(i) for i,name in enumerate(['visits','purchases','assignment_unit'],1)}


def verify():
    # Exercise 1: Validate a correct proposal
    record=validate({'visits':10,'purchases':3,'assignment_unit':'account'})
    assert rate(record)==.3

    # Exercise 2: Reject a plausible but impossible record
    try: validate({'visits':2,'purchases':3,'assignment_unit':'account'})
    except ValueError: pass
    else: raise AssertionError('impossible counts accepted')

    # Exercise 3: Trace extracted values to text
    text='Visits: 10; Purchases: 3; Unit: account'
    parsed,spans=extract(text)
    assert parsed==record
    assert text[slice(*spans['visits'])]=='10' and text[slice(*spans['purchases'])]=='3'

    # Exercise 4: Distinguish missing from zero
    try: validate({'visits':10,'purchases':None,'assignment_unit':'account'})
    except TypeError: pass
    else: raise AssertionError('missing treated as count')
    assert rate(validate({'visits':10,'purchases':0,'assignment_unit':'account'}))==0

    # Exercise 5: Reject boolean and extra fields
    for candidate,kind in [({'visits':True,'purchases':0,'assignment_unit':'account'},TypeError),({**record,'p_value':.01},ValueError)]:
        try: validate(candidate)
        except kind: pass
        else: raise AssertionError('schema bypass accepted')

    # Exercise 6: Preserve the assignment unit
    try: validate({**record,'assignment_unit':'visit'})
    except ValueError: pass
    else: raise AssertionError('unsupported assignment unit')
    assert record['assignment_unit']=='account'
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
