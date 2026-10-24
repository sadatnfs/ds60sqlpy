import hashlib
import json
import numpy as np

def point_in_time():
    rows=[{"event":1,"available":1,"value":10},
          {"event":2,"available":4,"value":20},
          {"event":3,"available":3,"value":30}]
    origin=3
    visible=[row for row in rows if row["event"]<=origin and row["available"]<=origin]
    assert [row["value"] for row in visible]==[10,30]
    print("Available values at origin 3:",[row["value"] for row in visible])

def version_identity():
    config={"model":"tiny-v1","threshold":.2,"features":["age","count"]}
    encoded=json.dumps(config,sort_keys=True,separators=(",",":")).encode()
    digest=hashlib.sha256(encoded).hexdigest()
    changed=dict(config,threshold=.3)
    other=hashlib.sha256(json.dumps(changed,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    assert digest!=other and len(digest)==64
    print("Configuration identity changes with threshold:",digest[:12],other[:12])

def decision_costs():
    p=np.array([.1,.4,.8]);false_positive=2.;false_negative=8.
    threshold=false_positive/(false_positive+false_negative)
    act=p>threshold
    positive_cost=(1-p)*false_positive;negative_cost=p*false_negative
    assert threshold==.2 and act.tolist()==[False,True,True]
    assert np.array_equal(act,positive_cost<negative_cost)
    print("Threshold and actions:",threshold,act)

def checked_extraction_and_claim():
    raw='{"case_id":"c1","category":"delay","evidence":"shipment arrived late"}'
    record=json.loads(raw)
    assert set(record)=={"case_id","category","evidence"}
    assert record["category"] in {"delay","damage","other"} and record["evidence"]
    events=10;failures=4;computed=failures/events;draft_claim=.9
    assert computed==.4 and not np.isclose(draft_claim,computed)
    print("Schema-valid extraction:",record,"verified failure fraction:",computed)

def main():
    point_in_time();version_identity();decision_costs();checked_extraction_and_claim()

if __name__ == "__main__":
    main()
