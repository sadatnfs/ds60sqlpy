"""Original bounded pandas/rpy2 bridge. Importing this file never starts R."""

import math
from pathlib import Path

EXPECTED_COLUMNS = ("row_id", "x", "y")
MAX_ROWS = 100_000


def validate_rows(rows):
    """Validate logical row identity and finite scalar fields before conversion."""
    rows = list(rows)
    if not 3 <= len(rows) <= MAX_ROWS:
        raise ValueError("Require 3 to 100000 rows")
    seen = set()
    for row in rows:
        if set(row) != set(EXPECTED_COLUMNS):
            raise ValueError("Require exactly row_id, x and y")
        row_id = row["row_id"]
        if not isinstance(row_id, str) or not row_id or row_id in seen:
            raise ValueError("Row IDs must be unique nonempty strings")
        seen.add(row_id)
        for key in ("x", "y"):
            value = row[key]
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{key} must be finite numeric, with no missing values")
    if len({float(row["x"]) for row in rows}) < 2:
        raise ValueError("Intercept and slope need at least two distinct x values")
    return rows


def fit_frame(frame, project_root, build_dir):
    """Fit original regression in embedded R; return detached Python values only.

    R must be called from this process's main thread. Do not share R pointers
    between processes or serialize the returned R objective into Spark tasks.
    """
    import threading

    if threading.current_thread() is not threading.main_thread():
        raise RuntimeError("Embedded R must run in the process main thread")
    if tuple(frame.columns) != EXPECTED_COLUMNS:
        raise ValueError("Columns must be row_id, x, y in that order")
    rows = validate_rows(frame.to_dict(orient="records"))
    import numpy as np
    import pandas as pd
    import rpy2.robjects as ro
    from rpy2.robjects import pandas2ri

    clean = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)
    clean[["x", "y"]] = clean[["x", "y"]].astype("float64")
    root = Path(project_root).resolve(strict=True)
    source = root / "R" / "api.R"
    ro.r["source"](str(source))
    with (ro.default_converter + pandas2ri.converter).context():
        r_frame = ro.conversion.get_conversion().py2rpy(clean)
    helper = ro.r("""
        function(frame, build_dir) {
          X <- cbind(1, frame$x)
          obj <- make_objective("regression", list(y=frame$y, X=X, X_pred=X),
                                 list(beta=c(0,0), log_sigma=0), build_dir=build_dir)
          fit <- fit_objective(obj)
          list(par=fit$par, value=fit$objective, gradient_max=fit$gradient_max,
               convergence=fit$convergence, row_id=as.character(frame$row_id),
               fitted=as.numeric(obj$report(fit$par)$mean))
        }
    """)
    result = helper(r_frame, str(Path(build_dir).resolve(strict=True)))
    ids = list(result.rx2("row_id"))
    if ids != [row["row_id"] for row in rows]:
        raise RuntimeError("R conversion changed row identity/order")
    return {
        "parameters": np.asarray(result.rx2("par")).tolist(),
        "objective": float(result.rx2("value")[0]),
        "gradient_max": float(result.rx2("gradient_max")[0]),
        "convergence": int(result.rx2("convergence")[0]),
        "row_id": ids,
        "fitted": np.asarray(result.rx2("fitted")).tolist(),
    }
