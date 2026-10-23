import hashlib
import json
import re
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

TRAIN=[("net-a","router outage packet loss","network"),("net-a","network outage router","network"),
       ("bill-a","invoice payment refund","billing"),("bill-a","billing invoice payment","billing")]
TEST=[("net-b","router network packet","network"),("bill-b","payment billing refund","billing")]
KB=[{"id":"network","version":2,"role":"ops","published":7,"expires":20,"text":"Router resets require approved change."},
    {"id":"billing","version":3,"role":"billing","published":6,"expires":20,"text":"Refund review requires invoice identifier."},
    {"id":"network-old","version":1,"role":"ops","published":1,"expires":5,"text":"Old router procedure."}]

def fit_model():
    return make_pipeline(CountVectorizer(),LogisticRegression(solver="liblinear",random_state=0,max_iter=500)).fit([r[1] for r in TRAIN],[r[2] for r in TRAIN])

def ticket_id(text):
    found=re.findall(r'(?<!\w)TKT-([0-9]{3})(?![0-9])',text)
    if len(found)!=1:raise ValueError("exactly one three-digit ticket ID required")
    return "TKT-"+found[0]

def retrieve(query,role,now):
    words=set(re.findall(r'\w+',query.lower()))
    candidates=[]
    for doc in KB:
        if doc['role']!=role or not doc['published']<=now<=doc['expires']:continue
        overlap=len(words & set(re.findall(r'\w+',doc['text'].lower())))
        if overlap:candidates.append((overlap,doc['id'],doc))
    return [dict(item[2]) for item in sorted(candidates,key=lambda item:(-item[0],item[1]))]

def analyze(text,role,now,model):
    identity=ticket_id(text)
    represented=model[0].transform([text])
    if represented.nnz==0:return {"ticket_id":identity,"status":"unsupported-vocabulary","evidence":[]}
    label=str(model.predict([text])[0]);evidence=retrieve(text,role,now)
    status="evidence-ready" if evidence else "insufficient-evidence"
    packet={"ticket_id":identity,"category":label,"status":status,
            "evidence":[{"source_id":d['id'],"version":d['version'],"quote":d['text']} for d in evidence]}
    packet['evidence_hash']=hashlib.sha256(json.dumps(packet['evidence'],sort_keys=True).encode()).hexdigest()
    return packet

def main():
    assert {r[0] for r in TRAIN}.isdisjoint({r[0] for r in TEST})
    model=fit_model();pred=model.predict([r[1] for r in TEST]).tolist()
    assert pred==[r[2] for r in TEST]
    good=analyze("TKT-301 router packet loss","ops",10,model)
    assert good['category']=='network' and good['status']=='evidence-ready'
    assert good['evidence']==[{'source_id':'network','version':2,'quote':'Router resets require approved change.'}]
    assert len(good['evidence_hash'])==64
    wrong_role=analyze("TKT-301 router packet loss","billing",10,model)
    assert wrong_role['status']=='insufficient-evidence' and wrong_role['evidence']==[]
    stale=analyze("TKT-301 router packet loss","ops",30,model)
    assert stale['status']=='insufficient-evidence'
    unknown=analyze("TKT-303 botanical specimen","ops",10,model)
    assert unknown['status']=='unsupported-vocabulary'
    for bad in ["no identifier router","TKT-301 TKT-302 router","TKT-3019 router"]:
        try:ticket_id(bad)
        except ValueError:pass
        else:raise AssertionError("malformed or ambiguous ID accepted")
    assert all(d['id']!='network-old' for d in retrieve("router","ops",10))
    print("nlp-024: held-out-family baseline, exact extraction, permitted current evidence and failure ledger passed")

if __name__ == "__main__":
    main()
