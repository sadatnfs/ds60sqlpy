"""llm-034: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Compute the full-precision reference
    w=np.array([[.1,-.9],[1.7,-.2]]); x=np.array([1.,-2.]); reference=w@x
    np.testing.assert_allclose(reference,[1.9,2.1],atol=1e-12,rtol=0)

    # Exercise 2: Quantize one shared scale
    scale=np.abs(w).max()/127; raw=np.rint(w/scale); q=np.clip(raw,-127,127).astype(np.int8)
    np.testing.assert_array_equal(q,[[7,-67],[127,-15]]); assert scale==1.7/127

    # Exercise 3: Measure output error
    restored=q.astype(float)*scale; output=restored@x; error=float(np.max(np.abs(output-reference)))
    assert np.isfinite(error) and 0<error<.02

    # Exercise 4: Use per-row scales
    scales=np.max(np.abs(w),axis=1,keepdims=True)/127; qr=np.clip(np.rint(w/scales),-127,127).astype(np.int8)
    np.testing.assert_array_equal(qr[0],[14,-127]); np.testing.assert_allclose(scales[:,0],[.9/127,1.7/127],atol=1e-12,rtol=0)
    row_error=float(np.max(np.abs((qr.astype(float)*scales)@x-reference))); assert np.isfinite(row_error)

    # Exercise 5: Account for storage metadata
    per_tensor=4*1+1*4; per_row=4*1+2*4
    assert (per_tensor,per_row)==(8,12)

    # Exercise 6: Expose clipping and tie policy
    values=np.array([127.,128.]); rounded=np.rint(values); saturated=np.count_nonzero((rounded<-127)|(rounded>127))
    assert saturated==1; np.testing.assert_array_equal(np.rint([.5,1.5,2.5]),[0,2,2])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
