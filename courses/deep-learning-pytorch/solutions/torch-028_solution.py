"""torch-028: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile, json, subprocess, sys, textwrap
from pathlib import Path


def make_state():
    model = nn.Linear(1, 1, bias=False)
    with torch.no_grad():
        model.weight.zero_()
    return model, torch.optim.Adam(model.parameters(), lr=0.05)


def step(model, optimizer, noise):
    x = torch.tensor([[1.0], [2.0]])
    target = 2 * x + noise
    optimizer.zero_grad(set_to_none=True)
    (model(x) - target).square().mean().backward()
    optimizer.step()


def verify():
    # Exercise 1: Create nontrivial training state
    torch.manual_seed(7)
    model, optimizer = make_state()
    for _ in range(2):
        step(model, optimizer, torch.zeros((2, 1)))
    parameter = next(model.parameters())
    assert optimizer.state[parameter]["step"].item() == 2 and parameter.item() > 0

    # Exercise 2: Save the complete local contract
    temporary = tempfile.TemporaryDirectory()
    folder = Path(temporary.name)
    path = folder / "checkpoint.pt"
    checkpoint = {
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "rng": torch.get_rng_state(),
        "data_position": 2,
    }
    torch.save(checkpoint, path)
    assert path.is_file() and checkpoint["data_position"] == 2

    # Exercise 3: Record uninterrupted continuation
    probe = torch.rand(3)
    noise = torch.rand((2, 1)) * 0.01
    step(model, optimizer, noise)
    expected = parameter.item()
    assert (
        torch.isfinite(probe).all()
        and optimizer.state[parameter]["step"].item() == 3
        and np.isfinite(expected)
    )

    # Exercise 4: Restore in a fresh interpreter
    program = textwrap.dedent("""
    import json,sys,torch
    from torch import nn
    state=torch.load(sys.argv[1],map_location='cpu',weights_only=True)
    model=nn.Linear(1,1,bias=False); optimizer=torch.optim.Adam(model.parameters(),lr=.05)
    model.load_state_dict(state['model']); optimizer.load_state_dict(state['optimizer']); torch.set_rng_state(state['rng'])
    probe=torch.rand(3); noise=torch.rand((2,1))*.01; x=torch.tensor([[1.],[2.]]); y=2*x+noise
    optimizer.zero_grad(set_to_none=True); (model(x)-y).square().mean().backward(); optimizer.step()
    print(json.dumps({'probe':probe.tolist(),'weight':model.weight.item(),'position':state['data_position']+1}))
    """)
    compile(program, "torch-checkpoint-child", "exec")
    result = subprocess.run(
        [sys.executable, "-c", program, str(path)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("checkpoint child failed: " + result.stderr)
    restored = json.loads(result.stdout.strip().splitlines()[-1])
    np.testing.assert_allclose(restored["probe"], probe.tolist(), atol=0, rtol=0)
    np.testing.assert_allclose(restored["weight"], expected, atol=1e-6, rtol=0)
    assert restored["position"] == 3

    # Exercise 5: Expose a weights-only restart
    state = torch.load(path, map_location="cpu", weights_only=True)
    weights_only, fresh_optimizer = make_state()
    weights_only.load_state_dict(state["model"])
    step(weights_only, fresh_optimizer, noise)
    assert abs(weights_only.weight.item() - expected) > 1e-6

    # Exercise 6: Verify cleanup and bounded claims
    temporary.cleanup()
    assert not folder.exists()
    receipt = {
        "cpu_next_step_checked": True,
        "multiprocess_loader_restored": False,
        "distributed_restart_verified": False,
    }
    assert receipt["cpu_next_step_checked"] and not receipt["distributed_restart_verified"]
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
