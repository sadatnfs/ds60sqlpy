# SPDX-License-Identifier: Apache-2.0
"""Private, source-bound model used only by the worker-loss integration test.

The same model class and configuration run in reference, fault and resume.
Only the explicitly selected test environment holds one forward after the
committed epoch-0 checkpoint. There is no mutable model counter or extra RNG.
"""

from __future__ import annotations

import json
import os
import re
import socket
import time
from pathlib import Path

import torch


class ControlledSequential(torch.nn.Sequential):
    def forward(self, input):
        token = os.environ.get("DS60_TORCH_TEST_GATE_TOKEN", "")
        if token and os.environ.get("RANK") == "1":
            if re.fullmatch(r"[0-9a-f]{32}", token) is None:
                raise RuntimeError("Invalid integration fixture token")
            shared = Path(os.environ.get("DS60_TORCH_TEST_GATE_DIR", ""))
            if not shared.is_absolute() or not shared.is_dir() or shared.is_symlink():
                raise RuntimeError("Integration fixture needs an owned shared gate path")
            selected = json.loads((shared.parent / "current-case.json").read_text())
            if selected != {"case": "fault", "token": token}:
                raise RuntimeError("Integration fixture token differs from selected fault case")
            plan = json.loads((shared.parent / "attempts/mlp-fault/plan.json").read_text())
            committed = shared.parent / "attempts/mlp-fault/checkpoints/epoch-0000/COMMITTED.json"
            if committed.is_file():
                marker = shared / ("ready-" + token + ".json")
                payload = {
                    "schema_version": 1,
                    "kind": "ds60-torch-controlled-worker-loss-gate",
                    "run_id": plan["run_id"],
                    "plan_digest": plan["plan_digest"],
                    "rank": 1,
                    "epoch": 1,
                    "hostname": socket.gethostname(),
                    "pid": os.getpid(),
                }
                with marker.open("x") as stream:
                    json.dump(payload, stream, sort_keys=True)
                    stream.write("\n")
                    stream.flush()
                    os.fsync(stream.fileno())
                deadline = time.monotonic() + 60
                while time.monotonic() < deadline:
                    time.sleep(0.1)
                raise RuntimeError("Integration fixture timed out before worker termination")
        return super().forward(input)


def gated_mlp_model(config: dict):
    if config != {"input_features": 2, "hidden_features": 16, "dropout_p": 0.2}:
        raise ValueError("Integration model configuration changed")
    return ControlledSequential(
        torch.nn.Linear(2, 16, dtype=torch.float64),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.2),
        torch.nn.Linear(16, 8, dtype=torch.float64),
        torch.nn.Tanh(),
        torch.nn.Linear(8, 1, dtype=torch.float64),
    )
