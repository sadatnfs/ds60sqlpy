"""Actual embedded-R acceptance; requires prepared rpy2, pandas, NumPy and TMB."""

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("tmb_bridge", root / "python" / "bridge.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
frame = pd.DataFrame(
    {
        "row_id": ["r3", "r1", "r4", "r2", "r6", "r5"],
        "x": [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0],
        "y": [-2.9, -0.8, 0.9, 3.1, 4.8, 7.2],
    }
)
result = bridge.fit_frame(frame, root, os.environ["TMB_BUILD_DIR"])
X = np.column_stack([np.ones(len(frame)), frame["x"]])
expected = np.linalg.lstsq(X, frame["y"], rcond=None)[0]
np.testing.assert_allclose(result["parameters"][:2], expected, atol=1e-5)
assert result["row_id"] == frame["row_id"].tolist()
assert result["convergence"] == 0 and result["gradient_max"] < 1e-4
for bad in (frame.assign(y=np.nan), frame.assign(row_id="duplicate"), frame.assign(x=1.0)):
    try:
        bridge.fit_frame(bad, root, os.environ["TMB_BUILD_DIR"])
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid frame was not rejected")
print(
    json.dumps(
        {
            "status": "passed",
            "rows": len(frame),
            "row_order": result["row_id"],
            "gradient_max": result["gradient_max"],
            "coefficients": result["parameters"][:2],
        }
    )
)
