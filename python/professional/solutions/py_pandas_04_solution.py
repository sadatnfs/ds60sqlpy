"""Reference implementation and exact boundary checks for python-pandas-04."""

import math
from collections import deque
from io import StringIO
import numpy as np
import pandas as pd

def mean_state(values: pd.Series) -> tuple[float, int]:
    if not pd.api.types.is_numeric_dtype(values.dtype):
        raise ValueError("Expected numeric measurements")
    known=values.dropna().to_numpy(dtype=float)
    if not np.isfinite(known).all():
        raise ValueError("Known measurements must be finite")
    return math.fsum(float(value) for value in known),len(known)

def merge_means(states: list[tuple[float, int]]) -> float | None:
    for total,count in states:
        if not math.isfinite(total) or isinstance(count,bool) or not isinstance(count,(int,np.integer)) or count<0 or (count==0 and total!=0):
            raise ValueError("Expected valid sum/count states")
    count=sum(count for _,count in states)
    return math.fsum(total for total,_ in states)/count if count else None

def customer_totals(chunks) -> pd.DataFrame:
    state={}
    for chunk in chunks:
        if not {"customer_id","amount_cents"}.issubset(chunk.columns) or chunk["customer_id"].isna().any() or not pd.api.types.is_integer_dtype(chunk["amount_cents"].dtype):
            raise ValueError("Expected customer identities and integer-cent measurements")
        for customer,amount in chunk[["customer_id","amount_cents"]].itertuples(index=False,name=None):
            rows,known,total=state.get(customer,(0,0,0))
            if not pd.isna(amount):
                known+=1;total+=int(amount)
            state[customer]=(rows+1,known,total)
    rows=[]
    for customer,(count,known,total) in sorted(state.items()):
        if not -(2**63)<=total<2**63:
            raise ValueError("Customer total exceeds the declared Int64 representation")
        rows.append((customer,count,known,total if known else pd.NA))
    result=pd.DataFrame(rows,columns=["customer_id","row_count","known_count","total_cents"])
    result["total_cents"]=pd.array(result["total_cents"],dtype="Int64")
    return result

def unique_records(chunks) -> pd.DataFrame:
    seen={};rows=[]
    for chunk in chunks:
        if not {"event_id","amount_cents"}.issubset(chunk.columns) or chunk["event_id"].isna().any() or not pd.api.types.is_integer_dtype(chunk["event_id"].dtype) or not pd.api.types.is_integer_dtype(chunk["amount_cents"].dtype):
            raise ValueError("Expected integer event IDs and integer-cent amounts")
        for event,amount in chunk[["event_id","amount_cents"]].itertuples(index=False,name=None):
            event=int(event);value=None if pd.isna(amount) else int(amount)
            if event in seen:
                if seen[event]!=value:
                    raise ValueError("One event identity has conflicting amounts")
            else:
                seen[event]=value;rows.append((event,value))
    result=pd.DataFrame(rows,columns=["event_id","amount_cents"])
    result["amount_cents"]=pd.array(result["amount_cents"],dtype="Int64")
    return result

def rolling_means(chunks, window: int):
    if isinstance(window,bool) or not isinstance(window,(int,np.integer)) or window<=0:
        raise ValueError("Expected a positive integer window")
    history=deque(maxlen=window)
    for chunk in chunks:
        values=np.asarray(chunk,dtype=float)
        if values.ndim!=1 or not np.isfinite(values).all():
            raise ValueError("Expected finite one-dimensional chunks")
        for value in values:
            history.append(float(value))
            if len(history)==window:
                yield math.fsum(history)/window

def csv_chunks(text: str, chunksize: int):
    if isinstance(chunksize,bool) or not isinstance(chunksize,int) or chunksize<=0:
        raise ValueError("Expected a positive integer chunk size")
    for chunk in pd.read_csv(StringIO(text),chunksize=chunksize,dtype={"event_id":"Int64","customer_id":"string","amount_cents":"Int64"}):
        if chunk.columns.tolist()!=["event_id","customer_id","amount_cents"] or chunk["event_id"].isna().any() or chunk["customer_id"].isna().any():
            raise ValueError("CSV schema and record identities must be valid")
        yield chunk

def expect_value_error(call):
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError")

def main():
    # Exercise 1: Retain the correct mean denominator
    assert mean_state(pd.Series([1,pd.NA,3],dtype="Float64"))==(4.,2)
    assert mean_state(pd.Series([],dtype="Float64"))==(0.,0)
    assert mean_state(pd.Series([pd.NA],dtype="Float64"))==(0.,0)
    expect_value_error(lambda:mean_state(pd.Series([np.inf])))
    # Exercise 2: Combine uneven chunks correctly
    assert math.isclose(merge_means([(4.,2),(100.,1)]),104/3)
    assert math.isclose(merge_means([(0.,0),(4.,2),(100.,1)]),104/3)
    assert merge_means([]) is None
    expect_value_error(lambda:merge_means([(5.,0)]))
    expect_value_error(lambda:merge_means([(1.,True)]))
    # Exercise 3: Reduce typed amounts across batches
    a=pd.DataFrame({"customer_id":["a","b"],"amount_cents":pd.Series([10,pd.NA],dtype="Int64")});b=pd.DataFrame({"customer_id":["a","b"],"amount_cents":pd.Series([20,pd.NA],dtype="Int64")})
    r=customer_totals(iter([a,b]))
    assert r.customer_id.tolist()==["a","b"] and r.row_count.tolist()==[2,2] and r.known_count.tolist()==[2,0]
    assert r.loc[0,"total_cents"]==30 and pd.isna(r.loc[1,"total_cents"])
    pd.testing.assert_frame_equal(r,customer_totals([pd.concat([a,b])]))
    # Exercise 4: Detect conflicts across chunk boundaries
    a=pd.DataFrame({"event_id":pd.Series([1,2],dtype="Int64"),"amount_cents":pd.Series([10,pd.NA],dtype="Int64")});b=pd.DataFrame({"event_id":pd.Series([1,3],dtype="Int64"),"amount_cents":pd.Series([10,20],dtype="Int64")})
    r=unique_records([a,b])
    assert r.event_id.tolist()==[1,2,3] and pd.isna(r.loc[1,"amount_cents"])
    conflict=pd.DataFrame({"event_id":pd.Series([2],dtype="Int64"),"amount_cents":pd.Series([0],dtype="Int64")})
    expect_value_error(lambda:unique_records([a,conflict]))
    # Exercise 5: Carry rolling history across batches
    assert list(rolling_means([[1,2],[3,4]],3))==[2.,3.]
    assert list(rolling_means([[1,2,3,4]],3))==[2.,3.]
    assert list(rolling_means([],3))==[]
    expect_value_error(lambda:list(rolling_means([[1]],0)))
    expect_value_error(lambda:list(rolling_means([[np.nan]],1)))
    # Exercise 6: Make parsing a typed batch boundary
    text="event_id,customer_id,amount_cents\n1,a,10\n2,b,\n3,a,20\n"
    chunks=list(csv_chunks(text,2))
    assert [len(c) for c in chunks]==[2,1] and str(chunks[0].amount_cents.dtype)=="Int64" and pd.isna(chunks[0].loc[1,"amount_cents"])
    expect_value_error(lambda:list(csv_chunks("event_id,customer_id,amount_cents\n1,a,bad\n",2)))
    expect_value_error(lambda:list(csv_chunks("event_id,customer_id,amount_cents\n,a,10\n",2)))
    print("python-pandas-04: all six normal and boundary contracts passed")

if __name__ == "__main__":
    main()
