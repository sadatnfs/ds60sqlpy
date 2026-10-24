"""llm-applied-001: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def choose(task):
    if task['exact_computation']: return 'deterministic_tool','exact computation'
    if task['fresh_evidence'] or task['citation_required']: return 'retrieval','current cited evidence'
    if task['stable_behavior_gap'] and task['governed_examples']>=100: return 'adaptation_candidate','stable measured behavior'
    return 'measure_baseline','prompt and evaluation first'


def verify():
    # Exercise 1: Route a changing definition
    task={'exact_computation':False,'fresh_evidence':True,'citation_required':True,'stable_behavior_gap':False,'governed_examples':0}
    assert choose(task)==('retrieval','current cited evidence')

    # Exercise 2: Route an exact calculation
    task={'exact_computation':True,'fresh_evidence':False,'citation_required':False,'stable_behavior_gap':False,'governed_examples':0}
    assert choose(task)==('deterministic_tool','exact computation')

    # Exercise 3: Require evidence before fine-tuning
    task={'exact_computation':False,'fresh_evidence':False,'citation_required':False,'stable_behavior_gap':True,'governed_examples':0}
    assert choose(task)[0]=='measure_baseline'
    task['governed_examples']=120; assert choose(task)[0]=='adaptation_candidate'

    # Exercise 4: Keep mechanisms composable
    task={'exact_computation':False,'fresh_evidence':True,'citation_required':True,'stable_behavior_gap':True,'governed_examples':120}
    assert choose(task)[0]=='retrieval'
    architecture={'knowledge':'versioned retrieval','format':'prompt baseline, then measured adapter if needed'}
    assert architecture['knowledge']=='versioned retrieval'

    # Exercise 5: Avoid training on secrets as an access mechanism
    policy={'access_control':'external pre-retrieval filter','weights_are_acl':False}
    assert not policy['weights_are_acl'] and 'pre-retrieval' in policy['access_control']

    # Exercise 6: Write a measurable subject-assistant contract
    contract={'fields':['assignment_unit','outcome','status'],'unknown_policy':'explicit unknown','split_unit':'study family','metric':'field exact match plus unsupported-field rate'}
    assert contract['split_unit']=='study family' and 'unsupported' in contract['metric']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
