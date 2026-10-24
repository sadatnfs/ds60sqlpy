"""llm-applied-005: bounded local reference checks. No network or persistent data writes."""

import re

def chunk(text,document_id,version,size,overlap):
    if type(size) is not int or type(overlap) is not int or size<=0 or not 0<=overlap<size: raise ValueError('0<=overlap<size required')
    spans=list(re.finditer(r'\S+',text)); result=[]; step=size-overlap
    for begin in range(0,len(spans),step):
        end=min(begin+size,len(spans)); start_char=spans[begin].start(); end_char=spans[end-1].end()
        result.append({'document_id':document_id,'version':version,'start':start_char,'end':end_char,'text':text[start_char:end_char]})
        if end==len(spans): break
    return result


def verify():
    # Exercise 1: Split a fixed document
    text='one two three four five six seven'; chunks=chunk(text,'d',1,3,1)
    assert [c['text'] for c in chunks]==['one two three','three four five','five six seven']

    # Exercise 2: Verify citation offsets
    assert all(text[c['start']:c['end']]==c['text'] for c in chunks)
    assert chunks[1]['start']==text.index('three')

    # Exercise 3: Preserve unusual whitespace
    odd='alpha  beta\ngamma'; pieces=chunk(odd,'odd',2,2,0)
    assert pieces[0]['text']=='alpha  beta' and pieces[1]['text']=='gamma'

    # Exercise 4: Measure overlap duplication
    assert sum(len(c['text'].split()) for c in chunks)==9
    assert len(text.split())==7

    # Exercise 5: Reject invalid policies
    for size,overlap in [(3,3),(3,-1),(0,0)]:
        try: chunk(text,'d',1,size,overlap)
        except ValueError: pass
        else: raise AssertionError('invalid chunk policy')

    # Exercise 6: Handle empty and short sources
    assert chunk('','empty',1,5,1)==[]
    short=chunk('only two','short',1,5,1); assert len(short)==1 and short[0]['text']=='only two'
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
