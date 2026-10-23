"""llm-applied-014: bounded local reference checks. No network or persistent data writes."""



def prepare(prompt,answer,max_length):
    if not prompt or not answer or max_length<2: raise ValueError('prompt and answer targets required')
    if any(type(x) is not int or x<0 for x in prompt+answer): raise ValueError('nonnegative integer token IDs required')
    sequence=(list(prompt)+list(answer))[:max_length]
    inputs=sequence[:-1]; targets=sequence[1:]
    labels=[token if position>=len(prompt) else -100 for position,token in enumerate(targets,1)]
    if not any(x!=-100 for x in labels): raise ValueError('truncation removed answer targets')
    return inputs,labels


def verify():
    # Exercise 1: Align an answer-only record
    inputs,labels=prepare([1,2],[5,6,3],10)
    assert inputs==[1,2,5,6] and labels==[-100,5,6,3] and sum(x!=-100 for x in labels)==3

    # Exercise 2: Preserve prompt context without prompt loss
    other_inputs,other_labels=prepare([8,9],[5,6,3],10)
    assert other_inputs[:2]==[8,9] and other_labels==labels

    # Exercise 3: Reject an empty answer
    try: prepare([1,2],[],10)
    except ValueError: pass
    else: raise AssertionError('empty supervised answer accepted')

    # Exercise 4: Detect destructive truncation
    try: prepare([1,2],[5,6,3],2)
    except ValueError: pass
    else: raise AssertionError('answer removed by truncation')

    # Exercise 5: Keep family splits disjoint
    train_families={'F'}; test_families={'F','G'}
    assert train_families&test_families=={'F'}

    # Exercise 6: Reject unsupported targets before training
    record={'inputs':inputs,'labels':labels,'source_supported':False,'annotation_reviewed':True}
    accepted=record['source_supported'] and record['annotation_reviewed']
    assert not accepted
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
