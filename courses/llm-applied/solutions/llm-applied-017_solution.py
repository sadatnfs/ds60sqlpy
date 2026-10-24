"""llm-applied-017: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F




def verify():
    # Exercise 1: Quantize a fixed matrix
    original=np.array([[.1,-.9],[1.7,-.2]],dtype=np.float32); scale=float(np.abs(original).max()/7)
    codes=np.clip(np.rint(original/scale),-7,7).astype(np.int8)
    np.testing.assert_array_equal(codes,[[0,-4],[7,-1]])

    # Exercise 2: Pack and unpack real nibbles
    unsigned=(codes.reshape(-1).astype(np.int16)+8).astype(np.uint8)
    packed=unsigned[::2] | (unsigned[1::2]<<4)
    unpacked=np.empty(4,dtype=np.uint8); unpacked[::2]=packed&15; unpacked[1::2]=packed>>4
    restored_codes=(unpacked.astype(np.int16)-8).astype(np.int8).reshape(2,2)
    np.testing.assert_array_equal(packed,[72,127]); np.testing.assert_array_equal(restored_codes,codes)

    # Exercise 3: Measure dequantization error
    dequantized=restored_codes.astype(np.float32)*scale; x_np=np.array([1.,-2.],dtype=np.float32)
    reference=original@x_np; approximate=dequantized@x_np
    np.testing.assert_allclose(reference,[1.9,2.1],atol=1e-6,rtol=0)
    assert np.isfinite(approximate).all() and np.max(np.abs(approximate-reference))>0

    # Exercise 4: Train only a small adapter
    w=torch.tensor(dequantized); a=nn.Parameter(torch.ones((2,1))*.1); b=nn.Parameter(torch.zeros((1,2))); x=torch.tensor(x_np[None,:]); saved=packed.copy(); opt=torch.optim.SGD([a,b],lr=.05)
    initial=(x@(w+a@b).T).square().mean().item()
    for _ in range(10):
        opt.zero_grad(set_to_none=True); loss=(x@(w+a@b).T).square().mean(); loss.backward(); opt.step()
    final=(x@(w+a@b).T).square().mean().item()
    assert final<initial and w.grad is None; np.testing.assert_array_equal(packed,saved)

    # Exercise 5: Account for storage honestly
    storage=packed.nbytes+np.dtype('float32').itemsize; compute_buffer=dequantized.nbytes
    assert storage==6 and compute_buffer==16

    # Exercise 6: State what was not measured
    receipt={'uniform_4bit_packing':True,'actual_adapter_update':True,'nf4':False,'double_quantization':False,'paged_optimizer':False,'gpu_peak_memory_measured':False}
    assert receipt['actual_adapter_update'] and not any(receipt[k] for k in ['nf4','double_quantization','paged_optimizer','gpu_peak_memory_measured'])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
