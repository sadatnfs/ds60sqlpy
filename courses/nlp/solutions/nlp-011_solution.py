import re

def extract_entities(text,lexicon):
    if not isinstance(text,str):raise TypeError("text must be a string")
    if not lexicon:return []
    names=sorted(lexicon,key=lambda name:(-len(name),name))
    if any(not name for name in names):raise ValueError("empty entity name")
    pattern=re.compile(r"(?<!\w)(?:"+"|".join(re.escape(name) for name in names)+r")(?!\w)")
    return [(m.start(),m.end(),lexicon[m.group()],m.group()) for m in pattern.finditer(text)]

def exact_scores(gold,predicted):
    gold=set(gold);predicted=set(predicted)
    tp=len(gold&predicted);fp=len(predicted-gold);fn=len(gold-predicted)
    precision=tp/(tp+fp) if tp+fp else 0.
    recall=tp/(tp+fn) if tp+fn else 0.
    f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.
    return tp,fp,fn,precision,recall,f1

def acquisition(text):
    # Strict authored grammar, not general relation extraction.
    pattern=r"(?P<subject>Acme Labs|Beta Ltd) acquired (?P<object>Acme Labs|Beta Ltd)\."
    match=re.fullmatch(pattern,text)
    if match is None:return None
    return {"subject":match.group("subject"),"predicate":"acquired",
            "object":match.group("object"),"subject_span":match.span("subject"),
            "object_span":match.span("object")}

def main():
    text="Ada joined Acme Labs in Paris."
    lexicon={"Ada":"PER","Acme":"ORG","Acme Labs":"ORG","Paris":"LOC"}
    spans=extract_entities(text,lexicon)
    assert spans==[(0,3,"PER","Ada"),(11,20,"ORG","Acme Labs"),(24,29,"LOC","Paris")]
    assert all(text[start:end]==surface for start,end,kind,surface in spans)
    repeated=extract_entities("Ada met Ada.",{"Ada":"PER"})
    assert [(s,e) for s,e,_,_ in repeated]==[(0,3),(8,11)]
    assert extract_entities("C++ Labs",{"C++ Labs":"ORG"})==[(0,8,"ORG","C++ Labs")]
    gold={('d1',kind,start,end) for start,end,kind,_ in spans}
    pred={('d1','PER',0,3),('d1','ORG',11,15)}
    tp,fp,fn,p,r,f1=exact_scores(gold,pred)
    assert (tp,fp,fn)==(1,1,2) and p==.5 and r==1/3 and f1==.4
    forward=acquisition("Acme Labs acquired Beta Ltd.")
    reverse=acquisition("Beta Ltd acquired Acme Labs.")
    assert forward['subject']==reverse['object'] and forward['object']==reverse['subject']
    assert acquisition("Acme Labs did not acquire Beta Ltd.") is None
    assert acquisition("Rumor: Acme Labs acquired Beta Ltd.") is None
    assert extract_entities("",lexicon)==[]
    print("nlp-011: raw spans, exact F1=.4, directed relations and abstention checks passed")

if __name__ == "__main__":
    main()
