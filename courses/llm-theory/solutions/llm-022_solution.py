"""llm-022: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile,json,subprocess,sys,textwrap
from pathlib import Path




def verify():
    # Exercise 1: Create Adam history
    w=nn.Parameter(torch.tensor(0.)); opt=torch.optim.Adam([w],lr=.1)
    for _ in range(2): opt.zero_grad(set_to_none=True); (w-2).square().backward(); opt.step()
    assert w.item()>0 and opt.state[w]['step'].item()==2

    # Exercise 2: Save a trusted local checkpoint
    temporary=tempfile.TemporaryDirectory(); path=Path(temporary.name)/'state.pt'
    torch.save({'weight':w.detach().clone(),'optimizer':opt.state_dict()},path)
    assert path.is_file(); saved=w.item()

    # Exercise 3: Calculate the uninterrupted next step
    opt.zero_grad(set_to_none=True); (w-2).square().backward(); opt.step(); expected=w.item()
    assert opt.state[w]['step'].item()==3 and expected!=saved

    # Exercise 4: Restore in a new interpreter
    program=textwrap.dedent("""
    import torch,json,sys
    from torch import nn
    state=torch.load(sys.argv[1],map_location='cpu',weights_only=True)
    w=nn.Parameter(state['weight'].clone()); opt=torch.optim.Adam([w],lr=.1); opt.load_state_dict(state['optimizer'])
    opt.zero_grad(set_to_none=True); (w-2).square().backward(); opt.step()
    print(json.dumps({'weight':w.item()}))
    """)
    compile(program, "checkpoint-child", "exec")
    result=subprocess.run([sys.executable,'-c',program,str(path)],check=False,capture_output=True,text=True,timeout=60)
    if result.returncode: raise RuntimeError('child process failed: '+result.stderr)
    restored=json.loads(result.stdout.strip().splitlines()[-1]); np.testing.assert_allclose(restored['weight'],expected,atol=1e-6,rtol=0)

    # Exercise 5: Expose weights-only continuation
    fresh_w=nn.Parameter(torch.tensor(saved)); fresh_opt=torch.optim.Adam([fresh_w],lr=.1)
    (fresh_w-2).square().backward(); fresh_opt.step(); assert abs(fresh_w.item()-expected)>1e-6

    # Exercise 6: Verify evaluation and cleanup
    drop=nn.Dropout(.5); drop.eval(); ones=torch.ones(8)
    assert torch.equal(drop(ones),ones); temporary.cleanup(); assert not path.exists()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
