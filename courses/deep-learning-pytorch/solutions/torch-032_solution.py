"""torch-032: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile, json, subprocess, sys, textwrap
from pathlib import Path


def verify():
    # Exercise 1: Create a known inference model
    model = nn.Linear(2, 1, bias=False)
    with torch.no_grad():
        model.weight.copy_(torch.tensor([[2.0, -1.0]]))
    model.eval()
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
    expected = model(x).detach()
    assert expected.tolist() == [[0.0], [2.0]]

    # Exercise 2: Round-trip named state
    temporary = tempfile.TemporaryDirectory()
    folder = Path(temporary.name)
    state_path = folder / "weights.pt"
    torch.save(model.state_dict(), state_path)
    restored = nn.Linear(2, 1, bias=False)
    restored.load_state_dict(torch.load(state_path, map_location="cpu", weights_only=True))
    restored.eval()
    torch.testing.assert_close(restored(x), expected, atol=1e-6, rtol=0)

    # Exercise 3: Save an exported program
    program = torch.export.export(model, (x,), strict=True)
    export_path = folder / "model.pt2"
    torch.export.save(program, export_path)
    loaded_program = torch.export.load(export_path)
    exported_module = loaded_program.module()
    torch.testing.assert_close(exported_module(x), expected, atol=1e-6, rtol=0)

    # Exercise 4: Check both artifacts in a fresh process
    child = textwrap.dedent("""
    import json,sys,torch
    from torch import nn
    x=torch.tensor([[1.,2.],[3.,4.]])
    model=nn.Linear(2,1,bias=False); model.load_state_dict(torch.load(sys.argv[1],map_location='cpu',weights_only=True)); model.eval()
    owner=torch.export.load(sys.argv[2]); exported=owner.module()
    with torch.no_grad(): result=[model(x).tolist(),exported(x).tolist()]
    print(json.dumps(result))
    """)
    compile(child, "torch-export-child", "exec")
    result = subprocess.run(
        [sys.executable, "-c", child, str(state_path), str(export_path)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("export child failed: " + result.stderr)
    a, b = json.loads(result.stdout.strip().splitlines()[-1])
    np.testing.assert_allclose(a, expected.numpy(), atol=1e-6, rtol=0)
    np.testing.assert_allclose(b, expected.numpy(), atol=1e-6, rtol=0)

    # Exercise 5: Expose static batch specialization
    three = torch.tensor([[0.0, 0.0], [1.0, 2.0], [3.0, 4.0]])
    assert tuple(restored(three).shape) == (3, 1)
    try:
        exported_module(three)
    except AssertionError as error:
        if "Guard failed: input.size()[0] == 2" not in str(error):
            raise
    else:
        raise AssertionError("static export constraint not enforced")

    # Exercise 6: Declare a bounded dynamic batch and clean up
    batch = torch.export.Dim("batch", min=1, max=4)
    dynamic = torch.export.export(model, (x,), dynamic_shapes=({0: batch},), strict=True).module()
    torch.testing.assert_close(dynamic(three), restored(three), atol=1e-6, rtol=0)
    temporary.cleanup()
    assert not folder.exists()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
