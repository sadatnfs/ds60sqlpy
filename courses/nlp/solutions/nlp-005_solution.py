def lemma(word,pos):
    table={("saw","VERB"):"see",("saw","NOUN"):"saw",("studies","NOUN"):"study",("better","ADJ"):"good"}
    return table.get((word.lower(),pos),word.lower())

def toy_tags(tokens):
    result=[]
    for i,word in enumerate(tokens):
        if word.lower()=="saw":result.append("NOUN" if i>0 and tokens[i-1].lower()=="the" else "VERB")
        else:result.append("OTHER")
    return result

def valid_dependency_tree(heads):
    n=len(heads)
    if n==0:return False
    if any(type(h) is not int or h < -1 or h>=n for h in heads):return False
    if heads.count(-1)!=1:return False
    for origin in range(n):
        seen=set();node=origin
        while node!=-1:
            if node in seen:return False
            seen.add(node);node=heads[node]
    return True

def main():
    assert lemma("saw","VERB")=="see" and lemma("saw","NOUN")=="saw"
    assert lemma("studies","NOUN")=="study" and lemma("better","ADJ")=="good"
    assert toy_tags(["I","saw","her"])[1]=="VERB"
    assert toy_tags(["the","saw","broke"])[1]=="NOUN"
    assert toy_tags(["the","old","saw"])[2]=="VERB"  # explicit known failure against NOUN gold
    assert valid_dependency_tree([1,-1,1])
    assert valid_dependency_tree([1,-1,0]) # structurally valid, not semantic proof
    assert not valid_dependency_tree([1,0,-1])
    assert not valid_dependency_tree([-1,-1])
    assert not valid_dependency_tree([2,-1]) and not valid_dependency_tree([])
    print("nlp-005: POS-conditioned lemmas; known old-saw error; structural tree checks passed")

if __name__ == "__main__":
    main()
