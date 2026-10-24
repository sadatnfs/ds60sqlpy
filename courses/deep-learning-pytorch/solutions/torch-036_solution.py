"""torch-036: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
import tempfile, json, subprocess, sys, textwrap, hashlib
from pathlib import Path


def verify():
    # Exercise 1: Freeze the scalar experiment
    x = torch.tensor([[1.0], [2.0], [3.0]], dtype=torch.float64)
    y = 2 * x
    held = torch.tensor([[4.0], [5.0]], dtype=torch.float64)
    split = {"train": ["a", "b", "c"], "test": ["d", "e"]}
    assert not set(split["train"]) & set(split["test"]) and len(split["test"]) == 2

    # Exercise 2: Train within a declared budget
    model = nn.Linear(1, 1, bias=False, dtype=torch.float64)
    with torch.no_grad():
        model.weight.zero_()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    for _ in range(30):
        optimizer.zero_grad(set_to_none=True)
        (model(x) - y).square().mean().backward()
        optimizer.step()
    model.eval()
    with torch.no_grad():
        expected = model(held)
        error = (expected - 2 * held).square().mean().item()
    assert torch.isfinite(model.weight).all() and error < 26

    # Exercise 3: Build the owned release bundle
    temporary = tempfile.TemporaryDirectory()
    folder = Path(temporary.name)
    weights = folder / "weights.pt"
    torch.save(model.state_dict(), weights)
    manifest = {
        "schema": {"features": ["x"], "dtype": "float64", "width": 1},
        "split": split,
        "weight_sha256": hashlib.sha256(weights.read_bytes()).hexdigest(),
        "steps": 30,
    }
    manifest_path = folder / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))
    assert len(manifest["weight_sha256"]) == 64 and manifest["schema"]["width"] == 1

    # Exercise 4: Verify fresh-process prediction parity
    child = textwrap.dedent("""
    import hashlib,json,sys,torch
    from pathlib import Path
    from torch import nn
    folder=Path(sys.argv[1]); manifest=json.loads((folder/'manifest.json').read_text()); weights=folder/'weights.pt'
    if hashlib.sha256(weights.read_bytes()).hexdigest()!=manifest['weight_sha256']: raise ValueError('weight hash mismatch')
    if manifest['schema']!={'features':['x'],'dtype':'float64','width':1}: raise ValueError('schema mismatch')
    model=nn.Linear(1,1,bias=False,dtype=torch.float64); model.load_state_dict(torch.load(weights,map_location='cpu',weights_only=True)); model.eval()
    with torch.inference_mode(): predictions=model(torch.tensor([[4.],[5.]],dtype=torch.float64)).tolist()
    print(json.dumps(predictions))
    """)
    compile(child, "torch-release-child", "exec")
    result = subprocess.run(
        [sys.executable, "-c", child, str(folder)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if result.returncode:
        raise RuntimeError("release child failed: " + result.stderr)
    np.testing.assert_allclose(
        json.loads(result.stdout.strip().splitlines()[-1]), expected.numpy(), atol=1e-12, rtol=0
    )

    # Exercise 5: Make a corrupted artifact fail
    broken = {**manifest, "weight_sha256": "0" * 64}
    manifest_path.write_text(json.dumps(broken, sort_keys=True))
    rejected = subprocess.run(
        [sys.executable, "-c", child, str(folder)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert rejected.returncode != 0 and "weight hash mismatch" in rejected.stderr
    manifest_path.write_text(json.dumps(manifest, sort_keys=True))

    # Exercise 6: Record a bounded decision and cleanup
    receipt = {
        "local_contracts_pass": True,
        "test_count": 2,
        "previous_artifact": "v1",
        "production_go": False,
        "limits": ["synthetic fixture", "no operational deployment test"],
    }
    temporary.cleanup()
    assert receipt["local_contracts_pass"] and not receipt["production_go"] and not folder.exists()
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())
