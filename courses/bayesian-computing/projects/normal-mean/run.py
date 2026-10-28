"""Run a deliberately prepared CmdStan project with explicit local data and outputs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def validate_data(data: dict[str, Any]) -> None:
    if not isinstance(data, dict) or set(data) != {
        "N",
        "y",
        "prior_mean",
        "prior_sd",
        "observation_sd",
    }:
        raise ValueError("Supply exactly the model's declared data fields")
    if type(data["N"]) is not int or not 1 <= data["N"] <= 1000:
        raise ValueError("N must be an integer from 1 through 1000")
    if not isinstance(data["y"], list) or len(data["y"]) != data["N"]:
        raise ValueError("N must match the outcome vector")
    values = [*data["y"], data["prior_mean"], data["prior_sd"], data["observation_sd"]]
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in values):
        raise ValueError("Data must contain finite numeric values")
    if data["prior_sd"] <= 0 or data["observation_sd"] <= 0:
        raise ValueError("Both standard deviations must be positive")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cmdstan", required=True, type=Path)
    parser.add_argument("--data", type=Path, default=HERE / "data.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--draws", type=int, default=1000)
    parser.add_argument("--warmup", type=int, default=1000)
    args = parser.parse_args()
    if not 100 <= args.draws <= 5000 or not 100 <= args.warmup <= 5000:
        parser.error("Warmup and retained draws must each be from 100 through 5000")
    data = json.loads(args.data.read_text("utf-8"))
    validate_data(data)
    if args.output.exists():
        parser.error("Choose a new output directory; existing work is never overwritten")
    # No toolchain installation or download is performed by this driver.
    import cmdstanpy
    import numpy as np

    cmdstanpy.set_cmdstan_path(str(args.cmdstan.expanduser().resolve()))
    args.output.mkdir(parents=True, exist_ok=False)
    model_path = args.output / "model.stan"
    model_path.write_bytes((HERE / "model.stan").read_bytes())
    data_path = args.output / "data.json"
    data_path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", "utf-8")
    model = cmdstanpy.CmdStanModel(stan_file=str(model_path))
    fit = model.sample(
        data=str(data_path),
        chains=4,
        parallel_chains=1,
        iter_warmup=args.warmup,
        iter_sampling=args.draws,
        seed=20261028,
        adapt_delta=0.9,
        output_dir=str(args.output / "chains"),
        show_progress=False,
    )
    values = fit.stan_variable("mu")
    assert len(values) == 4 * args.draws and np.all(np.isfinite(values))
    variance = 1 / (1 / data["prior_sd"] ** 2 + data["N"] / data["observation_sd"] ** 2)
    mean = variance * (
        data["prior_mean"] / data["prior_sd"] ** 2 + sum(data["y"]) / data["observation_sd"] ** 2
    )
    fit.summary().to_csv(args.output / "summary.csv")
    (args.output / "diagnostics.txt").write_text(fit.diagnose(), "utf-8")
    record = {
        "cmdstanpy": importlib.metadata.version("cmdstanpy"),
        "cmdstan": list(cmdstanpy.cmdstan_version() or ()),
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "chains": 4,
        "retained_draws": len(values),
        "sample_mean": float(values.mean()),
        "analytic_mean": mean,
        "analytic_variance": variance,
        "interpretation": "Review sampler diagnostics and Monte Carlo error before inference.",
    }
    (args.output / "run.json").write_text(json.dumps(record, indent=2) + "\n", "utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
